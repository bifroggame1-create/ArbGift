import express, { Request, Response } from 'express';
import { CONFIG } from '../config';
import { DB } from '../db';
import { UnifiedMarketAdapter } from '../services/markets/UnifiedMarketAdapter';

const app = express();

app.use(express.json());

// CORS для Telegram Mini App
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

/**
 * GET /api/collections
 * Получить все коллекции с floor price
 */
app.get('/api/collections', async (req: Request, res: Response) => {
  try {
    const collections = await DB.query(
      `SELECT
         id, address, name, description, image_url,
         total_supply, floor_price, floor_price_usd,
         indexed_at, created_at
       FROM collections
       ORDER BY indexed_at DESC NULLS LAST`
    );

    res.json({ collections });
  } catch (error: any) {
    console.error('[API] /collections error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/nfts
 * Получить NFT с фильтрами и listings
 *
 * Query params:
 * - collection_address: фильтр по коллекции
 * - owner: фильтр по владельцу
 * - on_sale: true/false - только NFT с active listings
 * - limit: количество (default 100, max 1000)
 * - offset: пагинация
 */
app.get('/api/nfts', async (req: Request, res: Response) => {
  try {
    const {
      collection_address,
      owner,
      on_sale,
      limit = 100,
      offset = 0,
    } = req.query;

    let query = `
      SELECT
        n.*,
        c.name as collection_name,
        c.address as collection_address,
        json_agg(
          json_build_object(
            'market', l.market,
            'price', l.price,
            'price_usd', l.price_usd,
            'seller', l.seller,
            'listing_url', l.listing_url
          ) ORDER BY l.price ASC
        ) FILTER (WHERE l.is_active) as listings
      FROM nfts n
      LEFT JOIN collections c ON c.id = n.collection_id
      LEFT JOIN listings l ON l.nft_address = n.address AND l.is_active = true
      WHERE 1=1
    `;

    const params: any[] = [];
    let paramIndex = 1;

    if (collection_address) {
      query += ` AND c.address = $${paramIndex++}`;
      params.push(collection_address);
    }

    if (owner) {
      query += ` AND n.owner = $${paramIndex++}`;
      params.push(owner);
    }

    if (on_sale === 'true') {
      query += ` AND EXISTS (
        SELECT 1 FROM listings WHERE nft_address = n.address AND is_active = true
      )`;
    }

    query += `
      GROUP BY n.id, c.name, c.address
      ORDER BY n.id DESC
      LIMIT $${paramIndex++} OFFSET $${paramIndex++}
    `;

    params.push(Math.min(Number(limit), 1000), Number(offset));

    const nfts = await DB.query(query, params);

    res.json({ nfts, count: nfts.length });
  } catch (error: any) {
    console.error('[API] /nfts error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/nfts/:address
 * Получить конкретный NFT со всеми listings
 */
app.get('/api/nfts/:address', async (req: Request, res: Response) => {
  try {
    const { address } = req.params;

    const nft = await DB.queryOne(
      `SELECT
         n.*,
         c.name as collection_name,
         c.address as collection_address,
         c.image_url as collection_image
       FROM nfts n
       LEFT JOIN collections c ON c.id = n.collection_id
       WHERE n.address = $1`,
      [address]
    );

    if (!nft) {
      return res.status(404).json({ error: 'NFT not found' });
    }

    // Получаем все listings
    const listings = await DB.query(
      `SELECT
         market, price, price_usd, seller, listing_url,
         sale_contract_address, indexed_at, created_at
       FROM listings
       WHERE nft_address = $1 AND is_active = true
       ORDER BY price ASC`,
      [address]
    );

    // История продаж
    const sales = await DB.query(
      `SELECT price, price_usd, seller, buyer, market, sold_at
       FROM sales
       WHERE nft_address = $1
       ORDER BY sold_at DESC
       LIMIT 10`,
      [address]
    );

    res.json({ nft, listings, sales });
  } catch (error: any) {
    console.error('[API] /nfts/:address error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/listings
 * Получить все активные listings с сортировкой
 *
 * Query params:
 * - market: фильтр по маркету ('getgems', 'fragment', etc)
 * - sort: 'price_asc' | 'price_desc' | 'recent'
 * - limit, offset
 */
app.get('/api/listings', async (req: Request, res: Response) => {
  try {
    const { market, sort = 'price_asc', limit = 100, offset = 0 } = req.query;

    let query = `
      SELECT
        l.*,
        n.name as nft_name,
        n.image_url as nft_image,
        c.name as collection_name
      FROM listings l
      JOIN nfts n ON n.address = l.nft_address
      LEFT JOIN collections c ON c.id = n.collection_id
      WHERE l.is_active = true
    `;

    const params: any[] = [];
    let paramIndex = 1;

    if (market) {
      query += ` AND l.market = $${paramIndex++}`;
      params.push(market);
    }

    // Сортировка
    switch (sort) {
      case 'price_desc':
        query += ' ORDER BY l.price DESC';
        break;
      case 'recent':
        query += ' ORDER BY l.indexed_at DESC';
        break;
      default:
        query += ' ORDER BY l.price ASC';
    }

    query += ` LIMIT $${paramIndex++} OFFSET $${paramIndex++}`;
    params.push(Math.min(Number(limit), 1000), Number(offset));

    const listings = await DB.query(query, params);

    res.json({ listings, count: listings.length });
  } catch (error: any) {
    console.error('[API] /listings error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/search
 * Полнотекстовый поиск по NFT (name, description)
 */
app.get('/api/search', async (req: Request, res: Response) => {
  try {
    const { q, limit = 50 } = req.query;

    if (!q || typeof q !== 'string') {
      return res.status(400).json({ error: 'Query parameter "q" required' });
    }

    const nfts = await DB.query(
      `SELECT
         n.*,
         c.name as collection_name,
         ts_rank(to_tsvector('english', n.name || ' ' || COALESCE(n.description, '')), plainto_tsquery('english', $1)) as rank
       FROM nfts n
       LEFT JOIN collections c ON c.id = n.collection_id
       WHERE to_tsvector('english', n.name || ' ' || COALESCE(n.description, '')) @@ plainto_tsquery('english', $1)
       ORDER BY rank DESC
       LIMIT $2`,
      [q, Math.min(Number(limit), 100)]
    );

    res.json({ nfts, count: nfts.length });
  } catch (error: any) {
    console.error('[API] /search error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/markets
 * Получить все поддерживаемые маркеты со статистикой
 */
app.get('/api/markets', async (req: Request, res: Response) => {
  try {
    const adapter = new UnifiedMarketAdapter();
    const markets = await adapter.getAllMarketsStats();
    res.json({ markets });
  } catch (error: any) {
    console.error('[API] /markets error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/nfts/:address/market-compare
 * Сравнить цены NFT на разных маркетах
 */
app.get('/api/nfts/:address/market-compare', async (req: Request, res: Response) => {
  try {
    const { address } = req.params;
    const adapter = new UnifiedMarketAdapter();
    const comparison = await adapter.getMarketComparison(address);
    res.json(comparison);
  } catch (error: any) {
    console.error('[API] /market-compare error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/trending
 * Получить trending NFTs (самые активные по продажам за 7 дней)
 */
app.get('/api/trending', async (req: Request, res: Response) => {
  try {
    const limit = Math.min(Number(req.query.limit) || 20, 100);
    const adapter = new UnifiedMarketAdapter();
    const trending = await adapter.getTrendingNFTs(limit);
    res.json({ trending, count: trending.length });
  } catch (error: any) {
    console.error('[API] /trending error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/price-drops
 * Найти NFT с падением цены (для price alerts)
 */
app.get('/api/price-drops', async (req: Request, res: Response) => {
  try {
    const threshold = Number(req.query.threshold) || 10; // 10% default
    const adapter = new UnifiedMarketAdapter();
    const drops = await adapter.findPriceDrops(threshold);
    res.json({ drops, count: drops.length });
  } catch (error: any) {
    console.error('[API] /price-drops error:', error.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /health
 * Health check
 */
app.get('/health', async (req: Request, res: Response) => {
  try {
    await DB.query('SELECT 1');
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ status: 'error', error: 'Database connection failed' });
  }
});

/**
 * Start server
 */
export function startAPIServer() {
  app.listen(CONFIG.API_PORT, () => {
    console.log(`[API] Server running on http://localhost:${CONFIG.API_PORT}`);
    console.log(`[API] Health check: http://localhost:${CONFIG.API_PORT}/health`);
  });
}

if (require.main === module) {
  startAPIServer();
}
