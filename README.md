# 🎁 TON Gift Aggregator

Full-stack platform for aggregating Telegram Gift NFTs from multiple TON marketplaces with integrated gaming features.

## 🚀 Quick Start

```bash
# 1. Clone and enter directory
cd ton-gift-aggregator

# 2. Configure environment
cp .env.example .env
# Edit .env and add your TONAPI_KEY from https://tonconsole.com/

# 3. Start infrastructure
docker-compose up -d postgres redis meilisearch

# 4. Run database migrations
alembic upgrade head

# 5. Seed initial data
python scripts/seed_markets.py

# 6. Start API server
uvicorn app.main:app --reload

# 7. Start Celery worker (in another terminal)
celery -A app.workers.celery_app worker -l info

# 8. Index your first collection
curl -X POST "http://localhost:8000/api/v1/admin/index-collection?collection_address=EQBTKUGf_2wz0mVji52re8oWcDZYUbCm2tAjAWYCODc2u5TP"
```

## 📦 Full Stack Deployment

```bash
# Deploy all services at once
docker-compose -f docker-compose.full.yml up -d

# View logs
docker-compose -f docker-compose.full.yml logs -f

# Stop all services
docker-compose -f docker-compose.full.yml down
```

## 🏗️ Architecture

- **Main API** (Port 8000): Gift aggregation, WebSocket, Search
- **Aviator Game** (Port 8001): Crash betting game
- **Roulette Game** (Port 8002): Classic + Gift roulette
- **Stars Service** (Port 8003): Buy Telegram Stars with TON
- **Frontend** (Port 3000): Vue.js Telegram Mini App

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## 🔌 Market Adapters

Currently integrated:
- ✅ **GetGems** - GraphQL API
- ✅ **Fragment** - TON API based
- ✅ **MRKT** - REST API with Telegram auth
- ✅ **Tonnel** - REST API
- ✅ **TON API Sales** - Fallback via blockchain events

## 🎮 Gaming Features

### Aviator Crash Game
Provably fair crash game where players bet on a growing multiplier and must cash out before it crashes.

```bash
# Access at http://localhost:8001
```

### Gift Roulette
Spin to win NFT gifts or TON prizes from a managed prize pool.

```bash
# Access at http://localhost:8002
```

## 🔍 API Endpoints

### Gifts
- `GET /api/v1/gifts` - List all gifts with filters
- `GET /api/v1/gifts/{id}` - Get gift details
- `GET /api/v1/gifts/{id}/listings` - Get all market listings

### Search
- `GET /api/v1/search?q=star` - Full-text search
- `GET /api/v1/search/autocomplete?q=blu` - Autocomplete suggestions

### Collections
- `GET /api/v1/collections` - List all collections

### Markets
- `GET /api/v1/markets` - List all marketplaces

### WebSocket
- `ws://host/ws/prices` - All price updates
- `ws://host/ws/collection/{id}` - Collection-specific updates
- `ws://host/ws/gift/{id}` - Single gift updates

### Admin
- `POST /api/v1/admin/index-collection?collection_address=EQ...` - Index collection
- `POST /api/v1/admin/sync-listings?market_slug=getgems` - Sync listings

## 📱 Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## 🔧 Configuration

Key environment variables:

```env
# Required
TONAPI_KEY=<get from tonconsole.com>
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...

# Optional
MEILISEARCH_API_KEY=<for search>
MRKT_INIT_DATA=<for MRKT adapter>
TELEGRAM_BOT_TOKEN=<for Stars service>
```

## 📊 Database Management

```bash
# Export to JSON
python utils/db_json_manager.py export backup.json

# Import from JSON
python utils/db_json_manager.py import backup.json

# Overwrite (⚠️ deletes existing data)
python utils/db_json_manager.py import backup.json --overwrite
```

## 🧪 Testing

```bash
# Run tests (TODO)
pytest

# Check types
mypy app/

# Lint code
ruff check app/
```

## 📈 Monitoring

- **API Health**: `GET /health`
- **Stats**: `GET /api/v1/stats`
- **Celery Flower**: `http://localhost:5555` (if enabled)

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit PR

## 📄 License

MIT License - see LICENSE file

## 🔗 Links

- [TON API](https://tonapi.io)
- [GetGems](https://getgems.io)
- [Fragment](https://fragment.com)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)

## 💡 Next Steps

- [ ] Add more marketplace adapters (Disintar, GetFragments)
- [ ] Implement price history charts
- [ ] Add email/Telegram notifications for price drops
- [ ] Build mobile apps (React Native)
- [ ] Add NFT portfolio tracking
- [ ] Integrate TON Connect for wallet features
