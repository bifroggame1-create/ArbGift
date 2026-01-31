# TON NFT Market Indexer

Production-ready система индексации NFT в сети TON с агрегацией маркетплейсов (GetGems, Fragment, и др.).

## 🏗 Архитектура

```
TON Blockchain
    ↓
TON API (tonapi.io)
    ↓
NFT Indexer Service
    ├─ NFT Scanner (каждые 5 мин)
    ├─ Metadata Resolver (IPFS → HTTP)
    └─ Market Adapters
        ├─ GetGems (GraphQL + TON API)
        ├─ Fragment (в разработке)
        └─ TON Diamonds (в разработке)
    ↓
PostgreSQL + Redis
    ↓
REST API
    ↓
Frontend (Telegram Mini App / Web)
```

## 📦 Структура проекта

```
nft-indexer/
├── src/
│   ├── config/           # Конфигурация (env vars)
│   ├── db/              # PostgreSQL models & queries
│   │   └── schema.sql   # Database schema
│   ├── services/
│   │   ├── ton/
│   │   │   ├── NFTIndexer.ts       # Сканирование NFT через TON API
│   │   │   └── MetadataResolver.ts # IPFS → HTTP resolver
│   │   └── markets/
│   │       └── GetGemsAdapter.ts   # GetGems маркет адаптер
│   ├── jobs/
│   │   └── indexCollections.ts     # CRON job для индексации
│   ├── api/
│   │   └── server.ts               # REST API endpoints
│   └── index.ts                    # Main entry point
├── db/
│   └── schema.sql                  # SQL схема БД
├── docker-compose.yml              # Docker setup (PostgreSQL + Redis + App)
├── Dockerfile
├── package.json
└── .env.example
```

## 🚀 Быстрый старт

### 1. Prerequisites

- Node.js 20+
- Docker & Docker Compose (для локального запуска БД)
- PostgreSQL 15+ (если без Docker)

### 2. Установка

```bash
# Клонировать проект
cd nft-indexer

# Установить зависимости
npm install

# Создать .env из примера
cp .env.example .env

# Заполнить .env реальными значениями (см. ниже)
```

### 3. Настройка .env

```bash
# TON API ключ (опционально, но рекомендуется)
# Регистрация: https://tonapi.io/
TONAPI_KEY=your_key_here

# Адреса коллекций Telegram Gifts
# Найти на: https://getgems.io/collection/telegram-gifts
GIFT_COLLECTIONS=EQDdjI1sqfrZGSjV2PY19Jv6hWzT2qJmPRuJUfXu0YXYZZ8f,EQAnotherCollection
```

### 4. Запуск с Docker

```bash
# Запустить PostgreSQL + Redis + Indexer
docker-compose up -d

# Проверить логи
docker-compose logs -f indexer

# Проверить health
curl http://localhost:3001/health
```

### 5. Запуск без Docker

```bash
# 1. Запустить PostgreSQL
# 2. Создать базу данных
createdb ton_nft_market

# 3. Применить схему
psql ton_nft_market < db/schema.sql

# 4. Запустить Redis
redis-server

# 5. Запустить индексатор
npm run dev
```

## 📊 Database Schema

### Таблицы

#### `collections`
Коллекции NFT (Telegram Gifts коллекции)
- `address` - TON адрес коллекции (уникальный)
- `name`, `description`, `image_url`
- `total_supply` - количество NFT
- `floor_price` - минимальная цена на маркете

#### `nfts`
Отдельные NFT элементы
- `address` - TON адрес NFT контракта (уникальный)
- `collection_id` - ссылка на коллекцию
- `token_id` - ID внутри коллекции
- `owner` - текущий владелец
- `metadata` - JSONB с traits и attributes
- `image_url` - resolved HTTP URL изображения

#### `listings`
Активные листинги на маркетплейсах
- `nft_address` - ссылка на NFT
- `market` - 'getgems', 'fragment', etc
- `price` - цена в TON
- `seller` - адрес продавца
- `is_active` - флаг активности

#### `sales`
История продаж
- `nft_address`, `price`, `seller`, `buyer`
- `sold_at` - timestamp продажи

## 🔌 API Endpoints

### GET `/api/collections`
Получить все коллекции

**Response:**
```json
{
  "collections": [
    {
      "id": 1,
      "address": "EQD...",
      "name": "Telegram Gifts",
      "total_supply": 5000,
      "floor_price": "1.50000000",
      "indexed_at": "2025-01-31T12:00:00Z"
    }
  ]
}
```

### GET `/api/nfts?collection_address=...&on_sale=true&limit=100`
Получить NFT с фильтрами

**Query params:**
- `collection_address` - фильтр по коллекции
- `owner` - фильтр по владельцу
- `on_sale` - `true/false` - только NFT с active listings
- `limit`, `offset` - пагинация

**Response:**
```json
{
  "nfts": [
    {
      "id": 1,
      "address": "EQA...",
      "name": "Gift #1234",
      "image_url": "https://cloudflare-ipfs.com/ipfs/Qm...",
      "owner": "EQB...",
      "collection_name": "Telegram Gifts",
      "listings": [
        {
          "market": "getgems",
          "price": "2.50000000",
          "seller": "EQC...",
          "listing_url": "https://getgems.io/nft/..."
        }
      ]
    }
  ],
  "count": 100
}
```

### GET `/api/nfts/:address`
Получить конкретный NFT с полной информацией

**Response:**
```json
{
  "nft": {
    "address": "EQA...",
    "name": "Gift #1234",
    "description": "...",
    "image_url": "https://...",
    "metadata": {
      "attributes": [
        {"trait_type": "Rarity", "value": "Legendary"}
      ]
    },
    "collection_name": "Telegram Gifts"
  },
  "listings": [...],
  "sales": [...]
}
```

### GET `/api/listings?market=getgems&sort=price_asc`
Получить все активные листинги

**Query params:**
- `market` - фильтр по маркету
- `sort` - `price_asc` | `price_desc` | `recent`
- `limit`, `offset`

### GET `/api/search?q=legendary`
Полнотекстовый поиск по NFT

**Response:**
```json
{
  "nfts": [...],
  "count": 25
}
```

## 🔄 CRON Jobs

### Index Collections Job
**Периодичность:** каждые 5 минут (настраивается в `CONFIG.INDEX_INTERVAL`)

**Действия:**
1. Сканирует все NFT из `CONFIG.GIFT_COLLECTIONS`
2. Обновляет metadata (IPFS → HTTP)
3. Подтягивает active listings с GetGems
4. Обновляет floor price коллекций

**Запуск вручную:**
```bash
npm run job:index-collections
```

## 🎯 Production Considerations

### Масштабирование

1. **Rate Limiting TON API:**
   - Free tier: 1 req/sec
   - Paid tier: до 10 req/sec
   - Используем `sleep(1100)` между запросами

2. **PostgreSQL индексы:**
   - Все критичные поля проиндексированы (см. `schema.sql`)
   - GIN index на `metadata` JSONB для быстрого поиска по traits
   - Full-text search index на `name + description`

3. **Redis кеширование:**
   - Metadata cache (7 дней TTL)
   - NFT cache (5 минут TTL)
   - Listings cache (1 минута TTL)

4. **Оптимизации:**
   - Batch insert NFT (до 1000 за раз)
   - Параллельный resolve IPFS URLs
   - Deduplication через `ON CONFLICT`

### Мониторинг

```bash
# Health check
curl http://localhost:3001/health

# PostgreSQL connections
psql ton_nft_market -c "SELECT count(*) FROM nfts"

# Индексация статус
psql ton_nft_market -c "SELECT address, indexed_at FROM collections"
```

### Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U postgres ton_nft_market > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres ton_nft_market < backup.sql
```

## 🔌 Интеграция с Frontend

### React / Vue example:

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:3001/api';

// Получить NFT с active listings
const { data } = await axios.get(`${API_BASE}/nfts`, {
  params: {
    collection_address: 'EQD...',
    on_sale: true,
    limit: 50
  }
});

// Отобразить карточки
data.nfts.forEach(nft => {
  console.log(nft.name, nft.image_url);
  console.log('Listings:', nft.listings);
});
```

## 📝 TODO / Roadmap

- [ ] Добавить Fragment adapter
- [ ] Добавить TON Diamonds adapter
- [ ] Реализовать WebSocket для real-time обновлений цен
- [ ] Добавить rarity score calculation (по traits)
- [ ] Добавить price history charts
- [ ] Добавить уведомления о price drops
- [ ] Добавить GraphQL API (опционально)
- [ ] Добавить Meilisearch для advanced search

## 🐛 Troubleshooting

### "Connection refused" ошибка

```bash
# Проверить что PostgreSQL запущен
docker-compose ps

# Перезапустить сервисы
docker-compose restart
```

### "Rate limit exceeded" от TON API

```bash
# Увеличить интервал между запросами в src/services/ton/NFTIndexer.ts
await this.sleep(2000); // вместо 1100
```

### Медленная индексация

```bash
# Проверить количество NFT в коллекции
# Для коллекции с 10k NFT = ~3 часа на полную индексацию (free tier TON API)
# Solution: использовать TON API paid tier или несколько API ключей
```

## 📄 License

MIT

## 🤝 Contributing

1. Форк проекта
2. Создать feature branch
3. Commit изменения
4. Push в branch
5. Создать Pull Request

---

**Built with ❤️ for TON NFT ecosystem**
