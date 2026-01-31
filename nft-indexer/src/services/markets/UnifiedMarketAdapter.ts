import { TonApiAdapter } from './TonApiAdapter';
import { GetGemsAdapter } from './GetGemsAdapter';
import { MajorAdapter } from './MajorAdapter';
import { PortalsAdapter } from './PortalsAdapter';
import { DB } from '../../db';

/**
 * UnifiedMarketAdapter - объединяет все маркет-адаптеры
 *
 * Стратегия:
 * 1. Primary: TonApiAdapter (получает listings со всех маркетов)
 * 2. Secondary: GetGemsAdapter (дополнительные данные: аукционы, bids)
 * 3. Major.tg: дополнительные listings без аутентификации
 * 4. Portals.tg: требует TMA auth (опционально)
 * 5. Merge и deduplicate результаты
 */
export class UnifiedMarketAdapter {
  private tonApi: TonApiAdapter;
  private getgems: GetGemsAdapter;
  private major: MajorAdapter;
  private portals: PortalsAdapter | null;

  constructor(portalsInitData?: string) {
    this.tonApi = new TonApiAdapter();
    this.getgems = new GetGemsAdapter();
    this.major = new MajorAdapter();
    this.portals = portalsInitData ? new PortalsAdapter(portalsInitData) : null;
  }

  /**
   * Полная индексация коллекции со всех маркетов
   */
  async indexCollection(collectionAddress: string): Promise<{
    nfts_indexed: number;
    listings_indexed: number;
    markets: string[];
  }> {
    console.log(`\n[UnifiedAdapter] Starting full index for ${collectionAddress}`);

    // 1. TON API — основной источник (все маркеты)
    const listingsCount = await this.tonApi.fetchCollectionListings(collectionAddress);

    // 2. GetGems GraphQL — дополнительные данные
    // (опционально, если нужны аукционы или детали bids)
    try {
      await this.getgems.fetchCollectionListings(collectionAddress);
    } catch (error: any) {
      console.warn('[UnifiedAdapter] GetGems GraphQL failed, using TON API data only');
    }

    // 3. Major.tg — дополнительные listings
    try {
      await this.major.fetchCollectionListings(collectionAddress);
    } catch (error: any) {
      console.warn('[UnifiedAdapter] Major.tg failed, skipping');
    }

    // 4. Portals.tg — если доступна аутентификация
    if (this.portals) {
      try {
        await this.portals.fetchCollectionListings(collectionAddress);
      } catch (error: any) {
        console.warn('[UnifiedAdapter] Portals.tg failed, skipping');
      }
    }

    // 5. Деактивируем stale listings
    await this.tonApi.deactivateStaleListings(collectionAddress);

    // 6. Собираем статистику
    const stats = await this.getStats(collectionAddress);

    console.log(`[UnifiedAdapter] ✅ Indexed ${stats.listings_indexed} listings from ${stats.markets.length} markets`);

    return stats;
  }

  /**
   * Обновить listings для конкретного NFT
   */
  async updateNFTListings(nftAddress: string): Promise<void> {
    // TON API fallback достаточно (включает все маркеты)
    await this.tonApi.fetchNFTListing(nftAddress);
  }

  /**
   * Индексация всех доступных listings (глобально)
   * Полезно для Major.tg который может вернуть все listings сразу
   */
  async indexAllMarkets(): Promise<{
    total_listings: number;
    markets: string[];
  }> {
    console.log('\n[UnifiedAdapter] Starting global market index...');

    let totalListings = 0;

    // Major.tg — может вернуть все listings без фильтра по коллекции
    try {
      const majorCount = await this.major.fetchAllListings();
      totalListings += majorCount;
      console.log(`[UnifiedAdapter] Major.tg indexed: ${majorCount} listings`);
    } catch (error: any) {
      console.warn('[UnifiedAdapter] Major.tg failed:', error.message);
    }

    // Portals.tg — если доступна аутентификация
    if (this.portals) {
      try {
        const portalsCount = await this.portals.fetchAllListings();
        totalListings += portalsCount;
        console.log(`[UnifiedAdapter] Portals.tg indexed: ${portalsCount} listings`);
      } catch (error: any) {
        console.warn('[UnifiedAdapter] Portals.tg failed:', error.message);
      }
    }

    // Собираем статистику
    const markets = await DB.query<{ market: string }>(
      `SELECT DISTINCT market FROM listings WHERE is_active = true`
    );

    const marketNames = markets.map((m) => m.market);

    console.log(`[UnifiedAdapter] ✅ Total listings: ${totalListings} from ${marketNames.length} markets`);

    return {
      total_listings: totalListings,
      markets: marketNames,
    };
  }

  /**
   * Получить сравнение цен на разных маркетах для NFT
   */
  async getMarketComparison(nftAddress: string): Promise<{
    listings: Array<{
      market: string;
      price: string;
      seller: string;
      listing_url: string;
      indexed_at: Date;
    }>;
    bestDeal: { market: string; price: string; listing_url: string } | null;
    savings: number;
  }> {
    const listings = await DB.query<{
      market: string;
      price: string;
      seller: string;
      listing_url: string;
      indexed_at: Date;
    }>(
      `SELECT market, price, seller, listing_url, indexed_at
       FROM listings
       WHERE nft_address = $1 AND is_active = true
       ORDER BY price::numeric ASC`,
      [nftAddress]
    );

    const bestDeal = listings[0] || null;
    const savings =
      listings.length > 1
        ? parseFloat(listings[1].price) - parseFloat(bestDeal.price)
        : 0;

    return { listings, bestDeal, savings };
  }

  /**
   * Получить статистику по всем маркетам
   */
  async getAllMarketsStats(): Promise<Array<{
    market: string;
    display_name: string;
    listings_count: number;
    floor_price: string;
    avg_price: string;
    total_volume: string;
  }>> {
    return await DB.query(`
      SELECT
        m.name as market,
        m.display_name,
        COUNT(DISTINCT l.nft_address) as listings_count,
        MIN(l.price::numeric) as floor_price,
        AVG(l.price::numeric) as avg_price,
        COALESCE(SUM(s.price::numeric), 0) as total_volume
      FROM markets m
      LEFT JOIN listings l ON l.market = m.name AND l.is_active = true
      LEFT JOIN sales s ON s.market = m.name
      WHERE m.is_active = true
      GROUP BY m.name, m.display_name
      ORDER BY listings_count DESC
    `);
  }

  /**
   * Получить trending NFTs (самые активные по продажам)
   */
  async getTrendingNFTs(limit: number = 20): Promise<Array<{
    nft_address: string;
    name: string;
    image_url: string;
    sales_count: number;
    avg_price: string;
    floor_price: string;
    markets_available: number;
  }>> {
    return await DB.query(
      `SELECT
         n.address as nft_address,
         n.name,
         n.image_url,
         COUNT(DISTINCT s.id) as sales_count,
         AVG(s.price::numeric) as avg_price,
         MIN(l.price::numeric) as floor_price,
         COUNT(DISTINCT l.market) as markets_available
       FROM nfts n
       LEFT JOIN sales s ON s.nft_address = n.address
         AND s.sold_at > NOW() - INTERVAL '7 days'
       LEFT JOIN listings l ON l.nft_address = n.address AND l.is_active = true
       WHERE s.id IS NOT NULL
       GROUP BY n.address, n.name, n.image_url
       ORDER BY sales_count DESC, avg_price DESC
       LIMIT $1`,
      [limit]
    );
  }

  /**
   * Price alerts: найти NFT с drop в цене
   */
  async findPriceDrops(thresholdPercent: number = 10): Promise<Array<{
    nft_address: string;
    name: string;
    old_price: string;
    new_price: string;
    drop_percent: number;
    market: string;
  }>> {
    // Сравниваем текущий floor с последней продажей
    return await DB.query(
      `SELECT
         n.address as nft_address,
         n.name,
         n.last_price as old_price,
         l.price as new_price,
         ROUND(((n.last_price::numeric - l.price::numeric) / n.last_price::numeric * 100)::numeric, 2) as drop_percent,
         l.market
       FROM nfts n
       JOIN listings l ON l.nft_address = n.address AND l.is_active = true
       WHERE n.last_price IS NOT NULL
         AND n.last_price::numeric > 0
         AND ((n.last_price::numeric - l.price::numeric) / n.last_price::numeric * 100) >= $1
       ORDER BY drop_percent DESC`,
      [thresholdPercent]
    );
  }

  /**
   * Внутренняя статистика
   */
  private async getStats(collectionAddress: string) {
    const nfts = await DB.query<{ count: string }>(
      `SELECT COUNT(*) as count FROM nfts WHERE collection_id = (
         SELECT id FROM collections WHERE address = $1
       )`,
      [collectionAddress]
    );

    const listings = await DB.query<{ count: string; markets: string[] }>(
      `SELECT
         COUNT(*) as count,
         array_agg(DISTINCT market) as markets
       FROM listings
       WHERE nft_address IN (
         SELECT address FROM nfts WHERE collection_id = (
           SELECT id FROM collections WHERE address = $1
         )
       ) AND is_active = true`,
      [collectionAddress]
    );

    return {
      nfts_indexed: parseInt(nfts[0]?.count || '0'),
      listings_indexed: parseInt(listings[0]?.count || '0'),
      markets: listings[0]?.markets || [],
    };
  }
}
