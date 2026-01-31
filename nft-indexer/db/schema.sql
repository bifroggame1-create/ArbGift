-- TON NFT Market Indexer Database Schema

-- Коллекции NFT (Telegram Gifts коллекции)
CREATE TABLE collections (
  id SERIAL PRIMARY KEY,
  address VARCHAR(66) UNIQUE NOT NULL, -- TON адрес коллекции
  name VARCHAR(255),
  description TEXT,
  image_url TEXT,
  total_supply INTEGER DEFAULT 0,
  floor_price NUMERIC(20,9), -- в TON
  floor_price_usd NUMERIC(10,2),
  indexed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- NFT элементы (конкретные Gift NFT)
CREATE TABLE nfts (
  id SERIAL PRIMARY KEY,
  address VARCHAR(66) UNIQUE NOT NULL, -- TON адрес NFT контракта
  collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
  token_id VARCHAR(100), -- ID внутри коллекции
  owner VARCHAR(66), -- текущий владелец
  name VARCHAR(255),
  description TEXT,
  image_url TEXT, -- уже resolved IPFS → HTTP
  image_preview_url TEXT, -- 256x256 превью
  content_uri TEXT, -- оригинальный URI из контракта
  metadata JSONB, -- полные metadata (traits, attributes)
  rarity_rank INTEGER, -- редкость (1 = самый редкий)
  last_price NUMERIC(20,9), -- последняя цена продажи
  indexed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Листинги на маркетах
CREATE TABLE listings (
  id SERIAL PRIMARY KEY,
  nft_address VARCHAR(66) NOT NULL REFERENCES nfts(address) ON DELETE CASCADE,
  market VARCHAR(50) NOT NULL, -- 'getgems', 'fragment', 'tondiamonds', etc
  price NUMERIC(20,9) NOT NULL, -- цена в TON
  price_usd NUMERIC(10,2),
  seller VARCHAR(66) NOT NULL, -- адрес продавца
  listing_url TEXT, -- ссылка на листинг
  sale_contract_address VARCHAR(66), -- адрес sale контракта (для GetGems)
  is_active BOOLEAN DEFAULT true,
  indexed_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP, -- когда листинг истечёт
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(nft_address, market, sale_contract_address)
);

-- История продаж
CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  nft_address VARCHAR(66) NOT NULL REFERENCES nfts(address) ON DELETE CASCADE,
  market VARCHAR(50) NOT NULL,
  price NUMERIC(20,9) NOT NULL,
  price_usd NUMERIC(10,2),
  seller VARCHAR(66) NOT NULL,
  buyer VARCHAR(66) NOT NULL,
  tx_hash VARCHAR(66), -- хеш транзакции в TON
  sold_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Metadata cache (для быстрого резолва IPFS)
CREATE TABLE metadata_cache (
  id SERIAL PRIMARY KEY,
  uri TEXT UNIQUE NOT NULL, -- IPFS URI или HTTP
  content JSONB NOT NULL,
  cached_at TIMESTAMP DEFAULT NOW()
);

-- Маркетплейсы (метаданные о каждом маркете)
CREATE TABLE markets (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL, -- 'getgems', 'fragment', 'major', 'portals', etc
  display_name VARCHAR(100) NOT NULL, -- 'GetGems', 'Fragment', 'Major.tg', 'Portals.tg'
  website_url TEXT,
  api_endpoint TEXT,
  commission_percent NUMERIC(5,2), -- процент комиссии маркета
  is_active BOOLEAN DEFAULT true,
  requires_auth BOOLEAN DEFAULT false, -- требует ли TMA auth
  last_indexed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для производительности
CREATE INDEX idx_nfts_collection ON nfts(collection_id);
CREATE INDEX idx_nfts_owner ON nfts(owner);
CREATE INDEX idx_nfts_token_id ON nfts(collection_id, token_id);
CREATE INDEX idx_listings_nft ON listings(nft_address);
CREATE INDEX idx_listings_active_price ON listings(is_active, price) WHERE is_active = true;
CREATE INDEX idx_listings_market ON listings(market, is_active);
CREATE INDEX idx_sales_nft ON sales(nft_address);
CREATE INDEX idx_sales_sold_at ON sales(sold_at DESC);
CREATE INDEX idx_sales_market ON sales(market);
CREATE INDEX idx_nfts_metadata_gin ON nfts USING GIN(metadata jsonb_path_ops);
CREATE INDEX idx_metadata_cache_uri ON metadata_cache(uri);
CREATE INDEX idx_markets_name ON markets(name);

-- Full-text search для поиска по имени/описанию
CREATE INDEX idx_nfts_search ON nfts USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Функция автообновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_collections_updated_at BEFORE UPDATE ON collections
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_nfts_updated_at BEFORE UPDATE ON nfts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Добавление маркетплейсов (seed data)
INSERT INTO markets (name, display_name, website_url, api_endpoint, commission_percent, requires_auth) VALUES
  ('getgems', 'GetGems', 'https://getgems.io', 'https://api.getgems.io/graphql', 5.0, false),
  ('fragment', 'Fragment', 'https://fragment.com', 'https://core.telegram.org/api/fragment', 0.0, false),
  ('ton.diamonds', 'TON Diamonds', 'https://ton.diamonds', 'https://tonapi.io/v2', 5.0, false),
  ('tondiamonds', 'TON Diamonds', 'https://ton.diamonds', 'https://tonapi.io/v2', 5.0, false),
  ('major', 'Major.tg', 'https://major.tg/marketplace', 'https://major.tg/api/v1', 2.5, false),
  ('portals', 'Portals.tg', 'https://portals.tg', 'https://portal-market.com/api', 2.5, true)
ON CONFLICT (name) DO NOTHING;
