# 🚀 Quick Start — TON Gift Aggregator

Запуск полной системы за 5 минут: NFT индексатор + Telegram Mini App.

---

## ⚡ Быстрый старт (Development)

### 1. Backend — NFT Indexer

```bash
cd nft-indexer

# Автоматическая установка и запуск
./start.sh

# Или вручную:
npm install
cp .env.example .env
# Отредактировать .env
createdb nft_indexer
psql nft_indexer < db/schema.sql
npm run dev
```

**Сервер запустится на:** `http://localhost:3001`

### 2. Индексация NFT

В новом терминале:

```bash
cd nft-indexer

# Индексировать коллекции из .env
npm run job:index-collections

# Или API запрос
curl -X POST http://localhost:3001/api/admin/index
```

### 3. Тестирование API

```bash
# Проверить все endpoints
./test-api.sh

# Или вручную
curl http://localhost:3001/api/markets
curl http://localhost:3001/api/nfts?on_sale=true&limit=10
```

### 4. Frontend — Telegram Mini App

```bash
cd ../frontend

# Настроить API URL
echo "VITE_API_URL=http://localhost:3001" >> .env

# Запустить
npm run dev
```

**Frontend откроется на:** `http://localhost:5173`

Открой в браузере `/market` чтобы увидеть маркетплейс с реальными NFT!

---

## 🐳 Docker Production (Рекомендуется)

### Вариант 1: Docker Compose (Всё в одном)

```bash
cd nft-indexer

# Запустить всю систему (PostgreSQL + Indexer + API)
docker-compose up -d

# Проверить логи
docker-compose logs -f

# Остановить
docker-compose down
```

### Вариант 2: Отдельные контейнеры

```bash
# PostgreSQL
docker run -d \
  --name nft-postgres \
  -e POSTGRES_PASSWORD=mysecret \
  -e POSTGRES_DB=nft_indexer \
  -p 5432:5432 \
  postgres:14

# NFT Indexer
docker build -t nft-indexer .
docker run -d \
  --name nft-indexer-api \
  --link nft-postgres \
  -e DATABASE_URL=postgresql://postgres:mysecret@nft-postgres:5432/nft_indexer \
  -e TONAPI_KEY=your_key \
  -p 3001:3000 \
  nft-indexer
```

---

## 🔧 Конфигурация

### `.env` файл (Backend)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nft_indexer

# TON API (получить на tonapi.io)
TONAPI_KEY=AE...
TONAPI_BASE_URL=https://tonapi.io/v2

# GetGems GraphQL
GETGEMS_GRAPHQL_URL=https://api.getgems.io/graphql

# Portals (опционально для TMA auth)
PORTALS_INIT_DATA=query_id=AAH...

# Коллекции для индексации (через запятую)
GIFT_COLLECTIONS=EQDdjI1sqfrZGSjV2PY19Jv6hWzT2qJmPRuJUfXu0YXYZZ8f

# Server
API_PORT=3001
INDEX_INTERVAL=300000
```

### `.env` файл (Frontend)

```bash
# Backend API URL
VITE_API_URL=http://localhost:3001

# Telegram Bot Token (для Mini App)
VITE_BOT_TOKEN=your_bot_token
```

---

## 📊 Проверка работы системы

### 1. Health Check

```bash
curl http://localhost:3001/health
# {"status":"ok","timestamp":"2026-01-31T..."}
```

### 2. Проверить маркеты

```bash
curl http://localhost:3001/api/markets | jq
```

**Ожидаемый результат:**
```json
{
  "markets": [
    {
      "market": "getgems",
      "display_name": "GetGems",
      "listings_count": 150,
      "floor_price": "0.5",
      "avg_price": "3.2",
      "total_volume": "12500.00"
    },
    {
      "market": "major",
      "display_name": "Major.tg",
      "listings_count": 42,
      ...
    }
  ]
}
```

### 3. Проверить NFT на продаже

```bash
curl 'http://localhost:3001/api/nfts?on_sale=true&limit=5' | jq '.nfts[0]'
```

### 4. Сравнение цен

```bash
curl http://localhost:3001/api/nfts/EQ.../market-compare | jq
```

---

## 🎯 API Endpoints (Полный список)

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/health` | GET | Health check |
| `/api/collections` | GET | Все коллекции с floor price |
| `/api/nfts` | GET | NFT (фильтры: on_sale, limit, offset) |
| `/api/nfts/:address` | GET | Конкретный NFT с listings |
| `/api/listings` | GET | Все активные listings |
| `/api/markets` | GET | Статистика по всем маркетам |
| `/api/nfts/:address/market-compare` | GET | Сравнение цен на NFT |
| `/api/trending` | GET | Топ NFT по продажам (7 дней) |
| `/api/price-drops` | GET | NFT с падением цены |
| `/api/search` | GET | Полнотекстовый поиск |

**Примеры:**

```bash
# Все NFT на продаже
GET /api/nfts?on_sale=true&limit=20&offset=0

# Фильтр по коллекции
GET /api/nfts?collection_address=EQ...&on_sale=true

# Фильтр по владельцу
GET /api/nfts?owner=EQ...

# Listings конкретного маркета
GET /api/listings?market=getgems&sort=price_asc

# Trending NFTs
GET /api/trending?limit=20

# Price drops (падение >15%)
GET /api/price-drops?threshold=15

# Поиск
GET /api/search?q=gift&limit=50
```

---

## 🔄 Автоматическая индексация (CRON)

### Создать CRON job файл:

```typescript
// jobs/autoIndex.ts
import { UnifiedMarketAdapter } from '../src/services/markets/UnifiedMarketAdapter'
import { CONFIG } from '../src/config'

async function runIndexer() {
  console.log('[CRON] Starting indexation...')

  const adapter = new UnifiedMarketAdapter(process.env.PORTALS_INIT_DATA)

  // Индексация всех маркетов
  await adapter.indexAllMarkets()

  // Индексация конкретных коллекций
  for (const addr of CONFIG.GIFT_COLLECTIONS) {
    await adapter.indexCollection(addr)
  }

  console.log('[CRON] ✅ Complete')
}

// Запуск каждые 5 минут
setInterval(runIndexer, 5 * 60 * 1000)
runIndexer() // Сразу при старте
```

### Запуск:

```bash
# Development
npm run job:auto-index

# Production (PM2)
pm2 start jobs/autoIndex.ts --name "nft-indexer-cron"
pm2 logs nft-indexer-cron

# Docker
docker run -d nft-indexer npm run job:auto-index
```

---

## 🐛 Troubleshooting

### Проблема: "Cannot connect to database"

```bash
# Проверить PostgreSQL запущен
psql -l

# Проверить DATABASE_URL в .env
echo $DATABASE_URL

# Пересоздать БД
dropdb nft_indexer && createdb nft_indexer
psql nft_indexer < db/schema.sql
```

### Проблема: "TON API rate limit"

```bash
# Увеличить задержку в TonApiAdapter.ts
await this.sleep(2000) # вместо 1100

# Или получить платный ключ на tonapi.io
```

### Проблема: "Frontend показывает пустой список"

```bash
# 1. Проверить backend работает
curl http://localhost:3001/health

# 2. Проверить есть данные
curl http://localhost:3001/api/nfts?on_sale=true

# 3. Проверить VITE_API_URL в frontend/.env
cat frontend/.env | grep VITE_API_URL

# 4. Проверить CORS
curl -I -H "Origin: http://localhost:5173" http://localhost:3001/api/markets
# Должен быть Access-Control-Allow-Origin: *
```

### Проблема: "Portals adapter fails"

```bash
# Portals требует TMA initData
# Временно отключить:
# В .env удалить PORTALS_INIT_DATA

# Или получить initData:
# 1. Открыть Portals.tg в Telegram
# 2. DevTools → Network → найти запрос с Authorization header
# 3. Скопировать WebAppInitData
```

---

## 📚 Дополнительная документация

- [README.md](nft-indexer/README.md) — Основная документация индексатора
- [MARKETPLACES_RESEARCH.md](nft-indexer/MARKETPLACES_RESEARCH.md) — Исследование маркетплейсов
- [MULTI_MARKET_GUIDE.md](nft-indexer/MULTI_MARKET_GUIDE.md) — Гайд по мульти-маркет API
- [INTEGRATION_GUIDE.md](nft-indexer/INTEGRATION_GUIDE.md) — Полное руководство интеграции

---

## ✅ Checklist готовности

**Backend:**
- [ ] PostgreSQL установлен и запущен
- [ ] `.env` создан с валидными credentials
- [ ] База данных создана (`createdb nft_indexer`)
- [ ] Схема применена (`psql ... < db/schema.sql`)
- [ ] API сервер запущен (`npm run dev`)
- [ ] Health check работает (`curl .../health`)
- [ ] Индексация запущена (`npm run job:index-collections`)

**Frontend:**
- [ ] `.env` создан с `VITE_API_URL`
- [ ] Dependencies установлены (`npm install`)
- [ ] Dev server запущен (`npm run dev`)
- [ ] MarketView показывает NFT
- [ ] Поиск работает
- [ ] Фильтры работают

**Production:**
- [ ] Docker images собраны
- [ ] docker-compose.yml настроен
- [ ] Secrets в .env (не коммитить!)
- [ ] CRON jobs настроены
- [ ] Monitoring настроен (логи, метрики)
- [ ] Backup БД настроен

---

**Вопросы?** См. документацию выше или открой issue на GitHub.

**Готово!** 🎉 Система запущена и индексирует NFT со всех TON маркетплейсов.
