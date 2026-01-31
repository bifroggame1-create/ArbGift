# TON NFT Marketplaces Research & Integration Guide

Полное исследование как работают TON NFT маркетплейсы и как их индексировать в нашей системе.

---

## 🎯 Обзор маркетплейсов

### 1. **GetGems** (https://getgems.io/)
**Статус:** Первый и крупнейший NFT маркетплейс TON
**API:** GraphQL + TON API
**Endpoint:** `https://api.getgems.io/graphql`

#### Особенности:
- Decentralized sale contracts (каждый листинг = отдельный смарт-контракт)
- Поддержка аукционов и фиксированных цен
- Официальная площадка Telegram Gifts
- Комиссия: 5% с продаж

#### Как индексировать:
**Метод 1: GraphQL API (прямой)**
```graphql
query GetCollectionSales($collectionAddress: String!) {
  alphaNftItemsByCollection(
    address: $collectionAddress
    saleType: ON_SALE
    first: 1000
  ) {
    items {
      nft {
        address
        name
        owner { address }
        sale {
          fullPrice      # в nanotons
          seller { address }
          saleContract   # адрес sale контракта
        }
      }
    }
  }
}
```

**Метод 2: TON API fallback (через tonapi.io)**
```typescript
// tonapi.io уже парсит GetGems sales
GET /v2/nfts/collections/{collection}/items

Response:
{
  "nft_items": [{
    "address": "EQ...",
    "sale": {
      "address": "EQ...sale_contract",
      "market": { "name": "getgems" },
      "price": { "value": "1500000000" },  // 1.5 TON
      "owner": { "address": "seller..." }
    }
  }]
}
```

**Преимущества TON API метода:**
- Уже агрегирован
- Не нужно GraphQL клиент
- Rate limit выше (если есть ключ)

---

### 2. **Fragment** (https://fragment.com/)
**Статус:** Официальный маркетплейс Telegram для username/числ
**API:** Telegram API (collectibles methods)
**Особенности:**
- Только usernames и phone numbers
- Все транзакции в TON
- $350M+ в продажах

#### Как индексировать:

**Метод 1: Telegram API (официальный)**
```typescript
// Используя Telegram Bot API / MTProto
fragment.getCollectibleInfo({
  collectible: {
    _: 'inputCollectibleUsername',
    username: 'durov'
  }
})

Response:
{
  purchase_date: 1234567890,
  currency: 'TON',
  amount: 15000000000,  // 15 TON
  crypto_currency: 'TON',
  crypto_amount: 15000000000
}
```

**Метод 2: TON blockchain parsing**
```typescript
// Fragment sale contracts имеют уникальную структуру
// Можно парсить через TON API:
GET /v2/blockchain/accounts/{fragment_contract}/transactions

// Фильтровать по методам:
- buy_username
- sell_username
```

**Метод 3: Web scraping (last resort)**
```typescript
// Fragment.com отдаёт HTML с встроенным JSON
// Можно парсить через Playwright:
await page.goto('https://fragment.com/username/selling');
const data = await page.evaluate(() => {
  return JSON.parse(document.querySelector('#data').textContent);
});
```

---

### 3. **TON Diamonds** (https://ton.diamonds/)
**Статус:** DAO-driven маркетплейс
**API:** Аналог GetGems (TON sale contracts)

#### Как индексировать:
```typescript
// TON Diamonds тоже использует sale contracts
// Метод идентичен GetGems:
GET /v2/nfts/collections/{collection}/items

// Фильтр по market.name = "ton.diamonds"
if (nft.sale?.market.name === 'ton.diamonds') {
  // ...
}
```

---

### 4. **Portals.tg** (https://portals.tg/)
**Статус:** Telegram Mini App маркетплейс
**Технология:** Web3 + TON Connect
**Особенности:** Интеграция прямо в Telegram

#### Предварительные выводы (агент еще исследует):
- Скорее всего использует TON Connect для wallet связи
- Backend API вероятно закрытый
- Индексация через TON blockchain events

---

### 5. **Major.tg** (https://major.tg/marketplace)
**Статус:** Gaming + NFT платформа
**Особенности:** In-game items как NFT

---

### 6. **MarketApp.ws** (https://marketapp.ws/)
**Статус:** Telegram Mini App
**Особенности:** Мобильный-first интерфейс

---

## 🛠 Универсальная стратегия индексации

### Уровень 1: TON API (tonapi.io) — рекомендуется
**Покрытие:** GetGems, Fragment, TON Diamonds, остальные
**Преимущество:** Один источник для всех маркетов

```typescript
// Все маркеты уже агрегированы в tonapi.io
GET /v2/nfts/collections/{collection}/items

// Response включает sales от всех маркетов:
{
  "nft_items": [{
    "sale": {
      "market": { "name": "getgems" | "fragment" | "ton.diamonds" }
    }
  }]
}
```

### Уровень 2: Прямые API маркетов
**Когда использовать:** для специфичных данных (история аукционов, bids)

- GetGems GraphQL: `https://api.getgems.io/graphql`
- Fragment API: Telegram collectibles methods
- Остальные: TON blockchain parsing

### Уровень 3: On-chain parsing
**Когда использовать:** для новых/неподдерживаемых маркетов

```typescript
// Парсинг sale contracts через TON API
GET /v2/blockchain/accounts/{nft_address}/methods/get_sale_data

// Или через ton-core:
import { TonClient } from '@ton/ton';

const client = new TonClient({
  endpoint: 'https://toncenter.com/api/v2/jsonRPC'
});

const sale = await client.runMethod(saleContract, 'get_sale_data');
```

---

## 📊 Архитектура нашего индексатора (обновлённая)

```
TON Blockchain
    ↓
┌─────────────────────────────────┐
│  TON API (tonapi.io)            │ ← Основной источник
│  - NFT Collections              │
│  - Sales from ALL markets       │
│  - Metadata                     │
└─────────────────┬───────────────┘
                  │
┌─────────────────▼──────────────────────┐
│  Market Adapters (параллельно)         │
│  ┌──────────────────────────────────┐  │
│  │ 1. TON API Adapter (primary)     │  │
│  │    - Получает все sales          │  │
│  │    - Нормализует данные          │  │
│  │                                  │  │
│  │ 2. GetGems GraphQL (дополнение) │  │
│  │    - Аукционы                    │  │
│  │    - Bids history                │  │
│  │                                  │  │
│  │ 3. Fragment Scraper             │  │
│  │    - Username listings           │  │
│  │                                  │  │
│  │ 4. Blockchain Parser            │  │
│  │    - Новые/неизвестные маркеты  │  │
│  └──────────────────────────────────┘  │
└─────────────────┬──────────────────────┘
                  │
┌─────────────────▼─────────────────┐
│  Unified Database                 │
│  - nfts (все NFT)                │
│  - listings (агрегированные)     │
│  - markets (метаданные маркетов) │
└───────────────────────────────────┘
```

---

## 💻 Реализация: Multi-Market Adapter

### Структура нового адаптера:

```typescript
// src/services/markets/UnifiedMarketAdapter.ts

import { TonApiAdapter } from './TonApiAdapter';
import { GetGemsAdapter } from './GetGemsAdapter';
import { FragmentAdapter } from './FragmentAdapter';

export class UnifiedMarketAdapter {
  private tonApi: TonApiAdapter;
  private getgems: GetGemsAdapter;
  private fragment: FragmentAdapter;

  async fetchAllListings(collectionAddress: string) {
    // 1. Primary: TON API (все маркеты сразу)
    const tonApiListings = await this.tonApi.fetchListings(collectionAddress);

    // 2. Дополнительно: GetGems GraphQL (для аукционов)
    const getgemsAuctions = await this.getgems.fetchAuctions(collectionAddress);

    // 3. Fragment (если это username collection)
    if (this.isFragmentCollection(collectionAddress)) {
      const fragmentListings = await this.fragment.fetchUsernames();
      return [...tonApiListings, ...fragmentListings];
    }

    // 4. Merge и deduplicate
    return this.mergeListings([
      ...tonApiListings,
      ...getgemsAuctions
    ]);
  }

  private mergeListings(listings: Listing[]): Listing[] {
    // Группируем по nft_address + sale_contract
    const map = new Map<string, Listing>();

    for (const listing of listings) {
      const key = `${listing.nft_address}:${listing.sale_contract_address}`;

      // Приоритет: GetGems GraphQL > TON API
      // (GraphQL даёт больше деталей)
      if (!map.has(key) || listing.source === 'getgems_graphql') {
        map.set(key, listing);
      }
    }

    return Array.from(map.values());
  }
}
```

---

## 🔌 Новые API эндпоинты

### GET `/api/markets`
Список всех поддерживаемых маркетов

```typescript
app.get('/api/markets', async (req, res) => {
  const markets = await DB.query(`
    SELECT
      market,
      COUNT(DISTINCT nft_address) as listings_count,
      AVG(price::numeric) as avg_price,
      MIN(price::numeric) as floor_price
    FROM listings
    WHERE is_active = true
    GROUP BY market
  `);

  res.json({ markets });
});
```

**Response:**
```json
{
  "markets": [
    {
      "market": "getgems",
      "listings_count": 1250,
      "avg_price": "3.45",
      "floor_price": "0.50"
    },
    {
      "market": "fragment",
      "listings_count": 85,
      "avg_price": "15.00",
      "floor_price": "5.00"
    }
  ]
}
```

### GET `/api/nfts/:address/market-compare`
Сравнение цен на одном NFT на разных маркетах

```typescript
app.get('/api/nfts/:address/market-compare', async (req, res) => {
  const listings = await DB.query(`
    SELECT market, price, seller, listing_url, indexed_at
    FROM listings
    WHERE nft_address = $1 AND is_active = true
    ORDER BY price ASC
  `, [req.params.address]);

  const bestDeal = listings[0];
  const savings = listings.length > 1
    ? (parseFloat(listings[1].price) - parseFloat(bestDeal.price))
    : 0;

  res.json({ listings, bestDeal, savings });
});
```

---

## 📈 Production Deployment

### 1. Обновить схему БД

```sql
-- Добавить таблицу markets для метаданных
CREATE TABLE markets (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  website_url TEXT,
  api_endpoint TEXT,
  commission_percent NUMERIC(5,2),
  is_active BOOLEAN DEFAULT true,
  last_indexed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Seed данные
INSERT INTO markets (name, display_name, website_url, commission_percent) VALUES
  ('getgems', 'GetGems', 'https://getgems.io', 5.0),
  ('fragment', 'Fragment', 'https://fragment.com', 0.0),
  ('ton.diamonds', 'TON Diamonds', 'https://ton.diamonds', 5.0),
  ('tondiamonds', 'TON Diamonds', 'https://ton.diamonds', 5.0);

-- Добавить foreign key в listings
ALTER TABLE listings
  ADD CONSTRAINT fk_market
  FOREIGN KEY (market)
  REFERENCES markets(name);
```

### 2. Environment Variables

```bash
# .env
# TON API
TONAPI_KEY=your_key_here
TONAPI_BASE_URL=https://tonapi.io/v2

# GetGems
GETGEMS_GRAPHQL_URL=https://api.getgems.io/graphql

# Fragment (опционально)
TELEGRAM_API_ID=your_id
TELEGRAM_API_HASH=your_hash

# Rate limits
TONAPI_REQUESTS_PER_SECOND=1
GETGEMS_REQUESTS_PER_SECOND=2
```

### 3. CRON Jobs обновление

```typescript
// jobs/updateAllMarkets.ts

export async function updateAllMarketsJob() {
  const adapter = new UnifiedMarketAdapter();

  for (const collection of CONFIG.GIFT_COLLECTIONS) {
    // Индексируем все маркеты за один проход
    await adapter.fetchAllListings(collection);
  }

  // Деактивируем старые listings
  await deactivateStaleListings();
}

// Запуск каждые 2 минуты
setInterval(updateAllMarketsJob, 2 * 60 * 1000);
```

---

## 🎨 Frontend Integration

### React Component Example

```typescript
import { useState, useEffect } from 'react';

export function NFTMarketCompare({ nftAddress }: { nftAddress: string }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/nfts/${nftAddress}/market-compare`)
      .then(r => r.json())
      .then(setData);
  }, [nftAddress]);

  if (!data) return <div>Loading...</div>;

  return (
    <div className="market-compare">
      <h3>Available on {data.listings.length} markets</h3>

      {data.listings.map(listing => (
        <div key={listing.market} className="market-row">
          <span className="market-name">{listing.market}</span>
          <span className="price">{listing.price} TON</span>
          <a href={listing.listing_url} target="_blank">
            Buy on {listing.market}
          </a>
        </div>
      ))}

      {data.savings > 0 && (
        <div className="savings-badge">
          💰 Save {data.savings.toFixed(2)} TON on {data.bestDeal.market}
        </div>
      )}
    </div>
  );
}
```

---

## 🔍 Источники

### Official APIs:
- [GetGems GraphQL Endpoint](https://api.getgems.io/graphql)
- [TonAPI Documentation](https://tonapi.io/)
- [Fragment Telegram API](https://core.telegram.org/api/fragment)

### GitHub Resources:
- [getgems-io/nft-contracts](https://github.com/getgems-io/nft-contracts) — GetGems смарт-контракты
- [ton-community/nft-sdk](https://github.com/ton-community/nft-sdk) — TON NFT SDK
- [toncenter/tonweb](https://github.com/toncenter/tonweb) — JavaScript SDK для TON
- [ndatg/toncenter-js](https://github.com/ndatg/toncenter-js) — TypeScript SDK для TON API

### Tutorials:
- [Requests to TON blockchain: How to fetch NFT data](https://medium.com/@romanovich.i.m/requests-to-the-ton-blockchain-using-js-how-to-fetch-nft-data-483e920cd160)
- [Step-by-Step NFT Marketplace Development on TON](https://rocknblock.medium.com/step-by-step-nft-marketplace-development-on-ton-blockchain-5e77771f47e3)

---

## ✅ Next Steps

1. ✅ TON API adapter (уже реализован в `NFTIndexer.ts`)
2. ⏳ GetGems GraphQL adapter (уже реализован в `GetGemsAdapter.ts`)
3. 🔜 Fragment adapter (TODO)
4. 🔜 Unified adapter для merge всех источников
5. 🔜 Frontend market comparison компонент
6. 🔜 Price alerts система (notify когда цена упала)

---

**Обновлено:** 31 января 2026
**Статус:** Production-ready для GetGems + TON API. Fragment в разработке.
