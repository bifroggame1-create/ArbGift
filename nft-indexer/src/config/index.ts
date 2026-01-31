import { config } from 'dotenv';
config();

export const CONFIG = {
  // PostgreSQL
  DB_HOST: process.env.DB_HOST || 'localhost',
  DB_PORT: parseInt(process.env.DB_PORT || '5432'),
  DB_NAME: process.env.DB_NAME || 'ton_nft_market',
  DB_USER: process.env.DB_USER || 'postgres',
  DB_PASSWORD: process.env.DB_PASSWORD || 'postgres',

  // Redis
  REDIS_HOST: process.env.REDIS_HOST || 'localhost',
  REDIS_PORT: parseInt(process.env.REDIS_PORT || '6379'),

  // TON API (tonapi.io - бесплатный tier до 1 req/sec)
  TONAPI_KEY: process.env.TONAPI_KEY || '', // опционально для higher limits
  TONAPI_BASE_URL: 'https://tonapi.io/v2',

  // IPFS Gateways (fallback chain)
  IPFS_GATEWAYS: [
    'https://cloudflare-ipfs.com/ipfs',
    'https://ipfs.io/ipfs',
    'https://gateway.pinata.cloud/ipfs'
  ],

  // Известные коллекции Telegram Gifts
  GIFT_COLLECTIONS: [
    'EQDdjI1sqfrZGSjV2PY19Jv6hWzT2qJmPRuJUfXu0YXYZZ8f' // пример адреса
  ],

  // GetGems GraphQL
  GETGEMS_GRAPHQL_URL: 'https://api.getgems.io/graphql',

  // Интервалы обновления (мс)
  INDEX_INTERVAL: 5 * 60 * 1000, // 5 минут
  LISTINGS_UPDATE_INTERVAL: 2 * 60 * 1000, // 2 минуты
  METADATA_RESOLVE_BATCH_SIZE: 50,

  // API Server
  API_PORT: parseInt(process.env.API_PORT || '3001'),

  // Cache TTL (секунды)
  CACHE_TTL_METADATA: 7 * 24 * 60 * 60, // 7 дней
  CACHE_TTL_LISTINGS: 60, // 1 минута
  CACHE_TTL_NFT: 5 * 60, // 5 минут
};
