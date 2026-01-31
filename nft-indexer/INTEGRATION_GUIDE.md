# NFT Marketplace Integration Guide

Полное руководство по интеграции мульти-маркет NFT индексатора с фронтендом Telegram Mini App.

---

## 🎯 Что реализовано

### ✅ Backend (NFT Indexer)

1. **Адаптеры для всех маркетов:**
   - ✅ **TonApiAdapter** — основной (GetGems, Fragment, TON Diamonds через tonapi.io)
   - ✅ **GetGemsAdapter** — GraphQL API для дополнительных данных
   - ✅ **MajorAdapter** — Major.tg публичный API (без аутентификации)
   - ✅ **PortalsAdapter** — Portals.tg с TMA аутентификацией

2. **UnifiedMarketAdapter:**
   - Объединяет все источники
   - Автоматическая деактивация устаревших listings
   - Методы для сравнения цен, трендов, price alerts

3. **REST API Endpoints:**
   ```
   GET /api/collections — все коллекции с floor price
   GET /api/nfts?on_sale=true — NFT на продаже с listings
   GET /api/nfts/:address — конкретный NFT
   GET /api/listings — все активные listings
   GET /api/markets — статистика по маркетам
   GET /api/nfts/:address/market-compare — сравнение цен
   GET /api/trending — топ NFT по продажам
   GET /api/price-drops — NFT с падением цены
   GET /health — health check
   ```

4. **База данных:**
   - ✅ Таблица `markets` с метаданными всех маркетплейсов
   - ✅ Seed data для GetGems, Fragment, Major, Portals, TON Diamonds
   - ✅ Индексы для производительности
   - ✅ Full-text search

### ✅ Frontend (Telegram Mini App)

1. **MarketView (Portals.tg 1:1 Clone):**
   - 🎨 Точный дизайн как у Portals.tg
   - 🔍 Поиск по имени/адресу NFT
   - 🏷️ Фильтры: цена, свежесть, маркет
   - 📱 Табы для каждого маркета (Все, GetGems, Fragment, Major, Portals)
   - 💳 Быстрая покупка (открывает ссылку на маркет)
   - 🎯 Telegram Mini App UI patterns
   - 📦 Подключён к real backend API

2. **Компоненты:**
   - Gift cards с градиентными фонами по маркету
   - Market badges (показывает откуда листинг)
   - Адаптивная сетка (2 колонки на мобильном)
   - Loading states, empty states
   - Haptic feedback для всех действий

---

## 🚀 Запуск системы

### 1. Backend (NFT Indexer)

```bash
cd nft-indexer

# Установить зависимости
npm install

# Создать .env файл
cat > .env << EOF
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nft_indexer

# TON API
TONAPI_KEY=your_tonapi_key_here
TONAPI_BASE_URL=https://tonapi.io/v2

# GetGems
GETGEMS_GRAPHQL_URL=https://api.getgems.io/graphql

# Portals (опционально, для TMA auth)
PORTALS_INIT_DATA=query_id=AAH...

# Collections
GIFT_COLLECTIONS=EQDdjI1sqfrZGSjV2PY19Jv6hWzT2qJmPRuJUfXu0YXYZZ8f

# Server
API_PORT=3001
INDEX_INTERVAL=300000
EOF

# Создать базу данных
createdb nft_indexer

# Применить схему
psql nft_indexer < db/schema.sql

# Запустить сервер
npm run dev
```

### 2. Первая индексация

```bash
# Вручную запустить индексацию
npm run job:index-collections

# Или через API
curl -X POST http://localhost:3001/api/admin/index
```

### 3. Frontend

```bash
cd ../frontend

# Добавить переменную окружения
echo "VITE_API_URL=http://localhost:3001" >> .env

# Запустить
npm run dev
```

### 4. Проверить результаты

```bash
# Все маркеты
curl http://localhost:3001/api/markets

# NFT на продаже
curl 'http://localhost:3001/api/nfts?on_sale=true&limit=10'

# Сравнение цен
curl http://localhost:3001/api/nfts/EQ.../market-compare
```

---

## 📊 Архитектура потока данных

```
┌─────────────────────────────────────────────────────┐
│  TON Blockchain                                     │
│  - GetGems sale contracts                           │
│  - Fragment usernames                               │
│  - TON Diamonds listings                            │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│  Market Adapters (Parallel Indexing)                │
│  ┌────────────────────────────────────────────────┐ │
│  │ TonApiAdapter (tonapi.io)                      │ │
│  │ ✓ GetGems, Fragment, TON Diamonds              │ │
│  ├────────────────────────────────────────────────┤ │
│  │ MajorAdapter (major.tg/api/v1)                 │ │
│  │ ✓ No auth required                             │ │
│  ├────────────────────────────────────────────────┤ │
│  │ PortalsAdapter (portal-market.com/api)         │ │
│  │ ✓ Requires TMA auth                            │ │
│  ├────────────────────────────────────────────────┤ │
│  │ GetGemsAdapter (api.getgems.io/graphql)        │ │
│  │ ✓ Auctions, bids                               │ │
│  └────────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│  UnifiedMarketAdapter                               │
│  - Merge & deduplicate listings                     │
│  - Deactivate stale listings                        │
│  - Market comparison                                │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│  PostgreSQL Database                                │
│  - collections                                      │
│  - nfts                                             │
│  - listings (multi-market)                          │
│  - sales                                            │
│  - markets (metadata)                               │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│  REST API Server (Express)                          │
│  - GET /api/nfts                                    │
│  - GET /api/markets                                 │
│  - GET /api/nfts/:id/market-compare                 │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│  Frontend (Telegram Mini App)                       │
│  - MarketView (Portals.tg clone)                    │
│  - Real-time listings                               │
│  - Multi-market filtering                           │
│  - Quick buy integration                            │
└─────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Design System

### Цвета по маркетам:

```typescript
const marketColors = {
  getgems: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',      // Синий
  fragment: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',     // Фиолетовый
  major: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',        // Зелёный
  portals: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',      // Розовый
  'ton.diamonds': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', // Оранжевый
}
```

### Telegram Mini App UI:

- Фон: `#0e0f14`
- Карточки: `#1a1b23`
- Текст: `#ffffff`
- Вторичный текст: `#9ca3af`
- Границы: `#2a2b35`

---

## 🔧 Настройка Portals.tg Auth (Опционально)

Для индексации Portals.tg нужен TMA initData:

### 1. Получить initData

```javascript
// В Telegram Mini App (JavaScript)
const initData = window.Telegram.WebApp.initData

// Или через Playwright (автоматизация)
const page = await browser.newPage()
await page.goto('https://portals.tg')

const initData = await page.evaluate(() => {
  return window.Telegram.WebApp.initData
})
```

### 2. Добавить в .env

```bash
PORTALS_INIT_DATA="query_id=AAH...&user=%7B%22id%22...&hash=abc123..."
```

### 3. Использовать в коде

```typescript
import { UnifiedMarketAdapter } from './services/markets/UnifiedMarketAdapter'

const adapter = new UnifiedMarketAdapter(process.env.PORTALS_INIT_DATA)
await adapter.indexAllMarkets()
```

---

## 📈 Production Monitoring

### SQL запросы для мониторинга:

```sql
-- Сколько listings на каждом маркете
SELECT market, COUNT(*) as count, MIN(price::numeric) as floor
FROM listings
WHERE is_active = true
GROUP BY market
ORDER BY count DESC;

-- Последняя индексация
SELECT m.display_name, m.last_indexed_at
FROM markets m
ORDER BY m.last_indexed_at DESC;

-- Stale listings (старше 1 часа)
SELECT market, COUNT(*) as stale_count
FROM listings
WHERE is_active = true
  AND indexed_at < NOW() - INTERVAL '1 hour'
GROUP BY market;

-- Топ NFT по количеству listings
SELECT
  n.name,
  n.address,
  COUNT(DISTINCT l.market) as markets_count,
  MIN(l.price::numeric) as best_price
FROM nfts n
JOIN listings l ON l.nft_address = n.address AND l.is_active = true
GROUP BY n.id, n.name, n.address
HAVING COUNT(DISTINCT l.market) > 1
ORDER BY markets_count DESC
LIMIT 20;
```

---

## 🔄 CRON Jobs (Автоматическая индексация)

### jobs/indexAllMarkets.ts

```typescript
import { UnifiedMarketAdapter } from '../src/services/markets/UnifiedMarketAdapter'
import { CONFIG } from '../src/config'

export async function indexAllMarketsJob() {
  console.log('[CRON] Starting global market index...')

  const adapter = new UnifiedMarketAdapter(process.env.PORTALS_INIT_DATA)

  // 1. Индексация всех маркетов глобально (Major)
  await adapter.indexAllMarkets()

  // 2. Индексация конкретных коллекций (TON API + GetGems)
  for (const collectionAddress of CONFIG.GIFT_COLLECTIONS) {
    await adapter.indexCollection(collectionAddress)
  }

  console.log('[CRON] ✅ Market index complete')
}

// Запуск каждые 5 минут
setInterval(indexAllMarketsJob, 5 * 60 * 1000)
```

### Запуск в Docker

```dockerfile
# Dockerfile для indexer job
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .

CMD ["node", "jobs/indexAllMarkets.ts"]
```

---

## 🛠 Troubleshooting

### Проблема: TON API rate limit

**Симптомы:** Ошибки 429 Too Many Requests

**Решение:**
```typescript
// Увеличить задержку в TonApiAdapter.ts
await this.sleep(2000) // 2 секунды вместо 1.1
```

### Проблема: IPFS metadata не резолвится

**Симптомы:** `image_url` пусто у NFT

**Решение:**
```typescript
// Проверить MetadataResolver fallback chain
const resolver = new MetadataResolver()
const httpUrl = await resolver.resolveIPFS('ipfs://QmXXX...')
```

### Проблема: Portals auth не работает

**Симптомы:** PortalsAdapter возвращает 401

**Решение:**
- Обновить initData (истекает через 24 часа)
- Проверить формат header: `X-Init-Data`
- Использовать только GET запросы (некоторые endpoints POST требуют доп. auth)

### Проблема: Frontend показывает пустой список

**Симптомы:** MarketView loading=false, но listings.length = 0

**Решение:**
```bash
# Проверить backend
curl http://localhost:3001/api/nfts?on_sale=true

# Проверить CORS
# Добавить в server.ts:
app.use(cors({ origin: '*' }))

# Проверить .env
echo $VITE_API_URL
```

---

## 📚 API Reference

См. полную документацию в:
- [MULTI_MARKET_GUIDE.md](./MULTI_MARKET_GUIDE.md) — примеры API, frontend компоненты
- [MARKETPLACES_RESEARCH.md](./MARKETPLACES_RESEARCH.md) — исследование всех маркетплейсов

---

## ✅ Checklist для Production

- [ ] Добавить rate limiting для API (`express-rate-limit`)
- [ ] Валидация входных параметров (zod)
- [ ] Логирование (winston или pino)
- [ ] Мониторинг (Prometheus + Grafana)
- [ ] Backup базы данных (pg_dump cron)
- [ ] SSL сертификаты для API
- [ ] Environment secrets в Vault/AWS Secrets Manager
- [ ] Horizontal scaling (multiple indexer workers)
- [ ] Redis cache для hot listings
- [ ] WebSocket для real-time updates

---

**Последнее обновление:** 31 января 2026
**Версия:** 3.0 (Full Multi-Market + TMA Frontend)
