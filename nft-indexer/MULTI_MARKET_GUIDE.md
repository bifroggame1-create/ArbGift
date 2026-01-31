# Multi-Market Integration Guide

Полное руководство по работе с мульти-маркетплейс системой.

---

## 🎯 Что умеет система

### ✅ Индексация

- **GetGems** — GraphQL + TON API
- **Fragment** — Telegram usernames & numbers
- **TON Diamonds** — через TON API
- **Другие маркеты** — автоматически через tonapi.io

### ✅ API Features

1. **Market Comparison** — сравнение цен на одном NFT
2. **Trending NFTs** — самые активные по продажам
3. **Price Alerts** — уведомления о падении цены
4. **Market Stats** — статистика по каждому маркету

---

## 🚀 Quick Start

### 1. Запуск с Docker

```bash
cd nft-indexer
docker-compose up -d

# Проверить логи
docker-compose logs -f indexer
```

### 2. Первая индексация

```bash
# Добавить адреса коллекций в .env
GIFT_COLLECTIONS=EQDdjI1sqfrZGSjV2PY19Jv6hWzT2qJmPRuJUfXu0YXYZZ8f

# Запустить manual index
npm run job:index-collections
```

### 3. Проверить результаты

```bash
# Все маркеты
curl http://localhost:3001/api/markets

# NFT с listings
curl http://localhost:3001/api/nfts?on_sale=true&limit=10

# Market comparison для NFT
curl http://localhost:3001/api/nfts/EQA.../market-compare
```

---

## 📡 API Examples

### 1. Получить все маркеты

```bash
GET /api/markets
```

**Response:**
```json
{
  "markets": [
    {
      "market": "getgems",
      "display_name": "GetGems",
      "listings_count": 1250,
      "floor_price": "0.50",
      "avg_price": "3.45",
      "total_volume": "125000.00"
    },
    {
      "market": "fragment",
      "display_name": "Fragment",
      "listings_count": 85,
      "floor_price": "5.00",
      "avg_price": "15.00",
      "total_volume": "45000.00"
    }
  ]
}
```

### 2. Market Comparison для NFT

```bash
GET /api/nfts/EQA.../market-compare
```

**Response:**
```json
{
  "listings": [
    {
      "market": "getgems",
      "price": "2.50",
      "seller": "EQ...",
      "listing_url": "https://getgems.io/nft/...",
      "indexed_at": "2026-01-31T12:00:00Z"
    },
    {
      "market": "ton.diamonds",
      "price": "2.80",
      "seller": "EQ...",
      "listing_url": "https://ton.diamonds/nft/...",
      "indexed_at": "2026-01-31T12:05:00Z"
    }
  ],
  "bestDeal": {
    "market": "getgems",
    "price": "2.50",
    "listing_url": "https://getgems.io/nft/..."
  },
  "savings": 0.30
}
```

**Frontend use case:**
```tsx
function NFTCard({ nftAddress }) {
  const { data } = useFetch(`/api/nfts/${nftAddress}/market-compare`);

  return (
    <div>
      <h3>Available on {data.listings.length} markets</h3>
      {data.bestDeal && (
        <div className="best-deal">
          💰 Best price: {data.bestDeal.price} TON on {data.bestDeal.market}
          {data.savings > 0 && <span>Save {data.savings} TON!</span>}
        </div>
      )}
      {data.listings.map(listing => (
        <a href={listing.listing_url} target="_blank">
          Buy on {listing.market} - {listing.price} TON
        </a>
      ))}
    </div>
  );
}
```

### 3. Trending NFTs

```bash
GET /api/trending?limit=20
```

**Response:**
```json
{
  "trending": [
    {
      "nft_address": "EQ...",
      "name": "Gift #1234",
      "image_url": "https://...",
      "sales_count": 15,
      "avg_price": "5.50",
      "floor_price": "4.20",
      "markets_available": 3
    }
  ]
}
```

### 4. Price Drops Alert

```bash
GET /api/price-drops?threshold=15
```

**Response:**
```json
{
  "drops": [
    {
      "nft_address": "EQ...",
      "name": "Gift #5678",
      "old_price": "10.00",
      "new_price": "8.00",
      "drop_percent": 20.0,
      "market": "getgems"
    }
  ]
}
```

**Use case:** Price Alert Bot
```typescript
setInterval(async () => {
  const { drops } = await fetch('/api/price-drops?threshold=10').then(r => r.json());

  for (const drop of drops) {
    await sendTelegramNotification({
      message: `🚨 Price drop alert!
        ${drop.name} dropped ${drop.drop_percent}%
        Was: ${drop.old_price} TON
        Now: ${drop.new_price} TON
        Market: ${drop.market}`
    });
  }
}, 5 * 60 * 1000); // каждые 5 минут
```

---

## 🏗 Architecture Diagram

```
┌──────────────────────────────────┐
│  Frontend (TG Mini App / Web)    │
│  - NFT Grid with Market Badges   │
│  - Price Comparison Widget       │
│  - Best Deal Highlighter         │
│  - Price Drop Alerts             │
└──────────────┬───────────────────┘
               │
               │ HTTP REST API
               │
┌──────────────▼───────────────────┐
│  API Server (Express)            │
│  - GET /api/markets              │
│  - GET /api/nfts/:id/compare     │
│  - GET /api/trending             │
│  - GET /api/price-drops          │
└──────────────┬───────────────────┘
               │
┌──────────────▼───────────────────┐
│  UnifiedMarketAdapter            │
│  ┌────────────────────────────┐  │
│  │ TonApiAdapter (primary)    │  │
│  │ - GetGems                  │  │
│  │ - Fragment                 │  │
│  │ - TON Diamonds             │  │
│  │ - Others                   │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ GetGemsAdapter (secondary) │  │
│  │ - GraphQL API              │  │
│  │ - Auctions                 │  │
│  │ - Bids history             │  │
│  └────────────────────────────┘  │
└──────────────┬───────────────────┘
               │
┌──────────────▼───────────────────┐
│  PostgreSQL Database             │
│  - collections                   │
│  - nfts                          │
│  - listings (multi-market)       │
│  - sales                         │
│  - markets (metadata)            │
└──────────────────────────────────┘
```

---

## 🔧 Development

### Добавить новый маркетплейс

1. **Создать адаптер** в `src/services/markets/`

```typescript
// src/services/markets/NewMarketAdapter.ts

export class NewMarketAdapter {
  async fetchListings(collectionAddress: string) {
    // API call или blockchain parsing
    const listings = await fetchFromAPI();

    // Сохранить в БД
    for (const listing of listings) {
      await DB.upsertListing({
        nft_address: listing.address,
        market: 'new_market',
        price: listing.price,
        seller: listing.seller,
        listing_url: listing.url,
      });
    }
  }
}
```

2. **Добавить в UnifiedAdapter**

```typescript
// src/services/markets/UnifiedMarketAdapter.ts

private newMarket: NewMarketAdapter;

constructor() {
  this.tonApi = new TonApiAdapter();
  this.getgems = new GetGemsAdapter();
  this.newMarket = new NewMarketAdapter(); // <-- добавить
}

async indexCollection(collectionAddress: string) {
  await this.tonApi.fetchCollectionListings(collectionAddress);
  await this.getgems.fetchCollectionListings(collectionAddress);
  await this.newMarket.fetchListings(collectionAddress); // <-- добавить
}
```

3. **Добавить в таблицу markets**

```sql
INSERT INTO markets (name, display_name, website_url, commission_percent)
VALUES ('new_market', 'New Market', 'https://newmarket.com', 2.5);
```

---

## 📊 Production Monitoring

### Проверить статус индексации

```sql
-- Сколько listings на каждом маркете
SELECT market, COUNT(*) as count
FROM listings
WHERE is_active = true
GROUP BY market;

-- Последняя индексация
SELECT address, indexed_at
FROM collections
ORDER BY indexed_at DESC;

-- Stale listings (старше 1 часа)
SELECT market, COUNT(*) as stale_count
FROM listings
WHERE is_active = true
  AND indexed_at < NOW() - INTERVAL '1 hour'
GROUP BY market;
```

### Логи

```bash
# Индексация
docker-compose logs -f indexer | grep "Indexed"

# API запросы
docker-compose logs -f indexer | grep "API"

# Ошибки
docker-compose logs -f indexer | grep "Error"
```

---

## 🎨 Frontend Components Examples

### Multi-Market Price Widget

```tsx
function MultiMarketPriceWidget({ nftAddress }) {
  const [comparison, setComparison] = useState(null);

  useEffect(() => {
    fetch(`/api/nfts/${nftAddress}/market-compare`)
      .then(r => r.json())
      .then(setComparison);
  }, [nftAddress]);

  if (!comparison) return <Spinner />;

  return (
    <div className="market-widget">
      <div className="header">
        Available on {comparison.listings.length} markets
      </div>

      {comparison.listings.map((listing, i) => (
        <div key={listing.market} className={i === 0 ? 'best-deal' : ''}>
          <div className="market-logo">
            {getMarketLogo(listing.market)}
          </div>
          <div className="price">
            {listing.price} TON
            {i === 0 && comparison.savings > 0 && (
              <span className="savings">
                💰 Save {comparison.savings.toFixed(2)} TON
              </span>
            )}
          </div>
          <a href={listing.listing_url} target="_blank" className="buy-btn">
            Buy Now →
          </a>
        </div>
      ))}
    </div>
  );
}
```

### Market Stats Dashboard

```tsx
function MarketStats() {
  const [markets, setMarkets] = useState([]);

  useEffect(() => {
    fetch('/api/markets')
      .then(r => r.json())
      .then(data => setMarkets(data.markets));
  }, []);

  return (
    <div className="market-stats">
      {markets.map(market => (
        <div key={market.market} className="market-card">
          <h3>{market.display_name}</h3>
          <div className="stat">
            <span>Listings:</span>
            <span>{market.listings_count}</span>
          </div>
          <div className="stat">
            <span>Floor:</span>
            <span>{market.floor_price} TON</span>
          </div>
          <div className="stat">
            <span>Volume:</span>
            <span>{market.total_volume} TON</span>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔐 Security Best Practices

### API Rate Limiting

```typescript
// middleware/rateLimit.ts
import rateLimit from 'express-rate-limit';

export const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 минута
  max: 60, // 60 запросов per IP
  message: 'Too many requests, please try again later'
});

// server.ts
app.use('/api/', apiLimiter);
```

### Input Validation

```typescript
import { z } from 'zod';

const nftAddressSchema = z.string().regex(/^EQ[A-Za-z0-9_-]{46}$/);

app.get('/api/nfts/:address', (req, res) => {
  try {
    const address = nftAddressSchema.parse(req.params.address);
    // ...
  } catch {
    return res.status(400).json({ error: 'Invalid NFT address' });
  }
});
```

---

## 📚 References

- [TON API Documentation](https://tonapi.io/)
- [GetGems GraphQL](https://api.getgems.io/graphql)
- [Fragment API](https://core.telegram.org/api/fragment)
- [TON NFT Standard](https://github.com/ton-blockchain/token-contract)

---

**Последнее обновление:** 31 января 2026
**Версия:** 2.0 (Multi-Market)
