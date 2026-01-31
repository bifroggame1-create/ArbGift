import { Pool, PoolClient } from 'pg';
import { CONFIG } from '../config';

// PostgreSQL connection pool
export const pool = new Pool({
  host: CONFIG.DB_HOST,
  port: CONFIG.DB_PORT,
  database: CONFIG.DB_NAME,
  user: CONFIG.DB_USER,
  password: CONFIG.DB_PASSWORD,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

pool.on('error', (err) => {
  console.error('Unexpected database error:', err);
  process.exit(-1);
});

// Типы данных
export interface Collection {
  id: number;
  address: string;
  name: string | null;
  description: string | null;
  image_url: string | null;
  total_supply: number;
  floor_price: string | null;
  floor_price_usd: string | null;
  indexed_at: Date | null;
  created_at: Date;
  updated_at: Date;
}

export interface NFT {
  id: number;
  address: string;
  collection_id: number | null;
  token_id: string | null;
  owner: string | null;
  name: string | null;
  description: string | null;
  image_url: string | null;
  image_preview_url: string | null;
  content_uri: string | null;
  metadata: Record<string, any> | null;
  rarity_rank: number | null;
  last_price: string | null;
  indexed_at: Date | null;
  created_at: Date;
  updated_at: Date;
}

export interface Listing {
  id: number;
  nft_address: string;
  market: string;
  price: string;
  price_usd: string | null;
  seller: string;
  listing_url: string | null;
  sale_contract_address: string | null;
  is_active: boolean;
  indexed_at: Date;
  expires_at: Date | null;
  created_at: Date;
  updated_at: Date;
}

export interface Sale {
  id: number;
  nft_address: string;
  market: string;
  price: string;
  price_usd: string | null;
  seller: string;
  buyer: string;
  tx_hash: string | null;
  sold_at: Date;
  created_at: Date;
}

// Database helpers
export class DB {
  static async query<T = any>(text: string, params?: any[]): Promise<T[]> {
    const result = await pool.query(text, params);
    return result.rows;
  }

  static async queryOne<T = any>(text: string, params?: any[]): Promise<T | null> {
    const rows = await this.query<T>(text, params);
    return rows[0] || null;
  }

  static async transaction<T>(callback: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  // Collection methods
  static async upsertCollection(data: {
    address: string;
    name?: string;
    description?: string;
    image_url?: string;
    total_supply?: number;
  }): Promise<Collection> {
    const result = await this.queryOne<Collection>(
      `INSERT INTO collections (address, name, description, image_url, total_supply, indexed_at)
       VALUES ($1, $2, $3, $4, $5, NOW())
       ON CONFLICT (address) DO UPDATE SET
         name = COALESCE($2, collections.name),
         description = COALESCE($3, collections.description),
         image_url = COALESCE($4, collections.image_url),
         total_supply = COALESCE($5, collections.total_supply),
         indexed_at = NOW()
       RETURNING *`,
      [data.address, data.name, data.description, data.image_url, data.total_supply]
    );
    return result!;
  }

  // NFT methods
  static async upsertNFT(data: {
    address: string;
    collection_id?: number;
    token_id?: string;
    owner?: string;
    name?: string;
    description?: string;
    image_url?: string;
    content_uri?: string;
    metadata?: Record<string, any>;
  }): Promise<NFT> {
    const result = await this.queryOne<NFT>(
      `INSERT INTO nfts (
         address, collection_id, token_id, owner, name, description,
         image_url, content_uri, metadata, indexed_at
       )
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
       ON CONFLICT (address) DO UPDATE SET
         collection_id = COALESCE($2, nfts.collection_id),
         token_id = COALESCE($3, nfts.token_id),
         owner = COALESCE($4, nfts.owner),
         name = COALESCE($5, nfts.name),
         description = COALESCE($6, nfts.description),
         image_url = COALESCE($7, nfts.image_url),
         content_uri = COALESCE($8, nfts.content_uri),
         metadata = COALESCE($9, nfts.metadata),
         indexed_at = NOW()
       RETURNING *`,
      [
        data.address,
        data.collection_id,
        data.token_id,
        data.owner,
        data.name,
        data.description,
        data.image_url,
        data.content_uri,
        data.metadata,
      ]
    );
    return result!;
  }

  // Listing methods
  static async upsertListing(data: {
    nft_address: string;
    market: string;
    price: string;
    price_usd?: string;
    seller: string;
    listing_url?: string;
    sale_contract_address?: string;
  }): Promise<Listing> {
    const result = await this.queryOne<Listing>(
      `INSERT INTO listings (
         nft_address, market, price, price_usd, seller, listing_url,
         sale_contract_address, is_active, indexed_at
       )
       VALUES ($1, $2, $3, $4, $5, $6, $7, true, NOW())
       ON CONFLICT (nft_address, market, sale_contract_address) DO UPDATE SET
         price = $3,
         price_usd = $4,
         seller = $5,
         listing_url = $6,
         is_active = true,
         indexed_at = NOW()
       RETURNING *`,
      [
        data.nft_address,
        data.market,
        data.price,
        data.price_usd,
        data.seller,
        data.listing_url,
        data.sale_contract_address || data.nft_address, // fallback to nft_address
      ]
    );
    return result!;
  }

  static async deactivateListings(nft_address: string, market: string): Promise<void> {
    await this.query(
      `UPDATE listings SET is_active = false WHERE nft_address = $1 AND market = $2`,
      [nft_address, market]
    );
  }

  static async getNFTsWithListings(limit: number = 100, offset: number = 0) {
    return await this.query(
      `SELECT
         n.*,
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
       LEFT JOIN listings l ON l.nft_address = n.address AND l.is_active = true
       GROUP BY n.id
       ORDER BY n.id DESC
       LIMIT $1 OFFSET $2`,
      [limit, offset]
    );
  }
}
