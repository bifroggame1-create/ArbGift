# TON Gift Aggregator - System Architecture

## Overview

Full-stack platform for aggregating Telegram Gift NFTs from multiple TON marketplaces with gaming features.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENTS                                            │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐         │
│  │  Telegram Mini App  │  │      Web App        │  │    External APIs    │         │
│  │      (Vue.js)       │  │     (Next.js)       │  │    (3rd Party)      │         │
│  └──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘         │
└─────────────┼───────────────────────┼───────────────────────┼───────────────────────┘
              │                       │                       │
              ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              NGINX REVERSE PROXY                                     │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  /api/*        → API Service (8000)                                            │ │
│  │  /ws/*         → WebSocket Service (8000)                                      │ │
│  │  /aviator/*    → Aviator Game (8001)                                           │ │
│  │  /roulette/*   → Roulette Game (8002)                                          │ │
│  │  /stars/*      → Stars Service (8003)                                          │ │
│  │  /*            → Frontend (3000)                                               │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   SERVICES                                           │
│                                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐      │
│  │    MAIN API          │  │    AVIATOR GAME      │  │   ROULETTE GAME      │      │
│  │    (FastAPI)         │  │    (FastAPI)         │  │    (FastAPI)         │      │
│  │                      │  │                      │  │                      │      │
│  │  • Gift listings     │  │  • Crash game logic  │  │  • Spin logic        │      │
│  │  • Search            │  │  • Provably fair     │  │  • Prize pool        │      │
│  │  • Collections       │  │  • Real-time WS      │  │  • Provably fair     │      │
│  │  • WebSocket prices  │  │  • Bet management    │  │  • Gift prizes       │      │
│  │  • Market adapters   │  │                      │  │                      │      │
│  └──────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘      │
│             │                         │                         │                   │
│  ┌──────────┴───────────┐  ┌──────────┴───────────┐                                │
│  │   STARS SERVICE      │  │   CELERY WORKERS     │                                │
│  │   (FastAPI)          │  │                      │                                │
│  │                      │  │  • index_collection  │                                │
│  │  • Stars purchase    │  │  • sync_listings     │                                │
│  │  • TON payments      │  │  • resolve_metadata  │                                │
│  │  • Telegram Bot API  │  │  • update_prices     │                                │
│  └──────────────────────┘  └──────────────────────┘                                │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MARKET ADAPTERS                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ GetGems  │  │ Fragment │  │   MRKT   │  │  Tonnel  │  │ TON API  │             │
│  │ GraphQL  │  │ TON API  │  │  REST    │  │  REST    │  │  Sales   │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │             │             │                    │
│       └─────────────┴─────────────┴─────────────┴─────────────┘                    │
│                                   │                                                 │
│                                   ▼                                                 │
│                      ┌──────────────────────────┐                                   │
│                      │   NORMALIZED LISTINGS    │                                   │
│                      │   (Unified Data Model)   │                                   │
│                      └──────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                DATA LAYER                                            │
│                                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐      │
│  │     PostgreSQL       │  │        Redis         │  │     Meilisearch      │      │
│  │                      │  │                      │  │                      │      │
│  │  • collections       │  │  • Cache             │  │  • Full-text search  │      │
│  │  • nfts              │  │  • Sessions          │  │  • Filters           │      │
│  │  • listings          │  │  • Rate limits       │  │  • Autocomplete      │      │
│  │  • sales             │  │  • Pub/Sub           │  │  • Faceted search    │      │
│  │  • users             │  │  • Celery broker     │  │                      │      │
│  │  • game_history      │  │  • Real-time state   │  │                      │      │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘      │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                             EXTERNAL SERVICES                                        │
│                                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐      │
│  │      TON API         │  │   Telegram Bot API   │  │     IPFS Gateways    │      │
│  │    (tonapi.io)       │  │                      │  │                      │      │
│  │                      │  │  • Stars gifting     │  │  • cloudflare-ipfs   │      │
│  │  • NFT data          │  │  • Payments          │  │  • ipfs.io           │      │
│  │  • Sales events      │  │  • User auth         │  │  • pinata.cloud      │      │
│  │  • Blockchain state  │  │  • Notifications     │  │                      │      │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘      │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Services

### 1. Main API (Port 8000)
- Gift aggregation from multiple marketplaces
- Real-time price updates via WebSocket
- Full-text search with Meilisearch
- Collection management and indexing

### 2. Aviator Game (Port 8001)
- Crash-style betting game
- Provably fair algorithm
- Real-time multiplier via WebSocket
- Bet placement and cash-out

### 3. Roulette Game (Port 8002)
- Classic roulette (numbers, colors)
- Gift roulette (win NFT prizes)
- Provably fair spins
- Prize pool management

### 4. Stars Service (Port 8003)
- Buy Telegram Stars with TON
- TON payment verification
- Telegram Bot API integration
- Order management

### 5. Frontend (Port 3000)
- Vue.js Telegram Mini App
- Real-time price updates
- Gift browsing and filtering
- Game interfaces

## Data Flow

### Gift Indexing
```
TON Blockchain → TON API → Indexer → PostgreSQL → Meilisearch
                                   ↓
                            Market Adapters → Listings DB
```

### Real-time Updates
```
Market Adapters → Celery Worker → Redis Pub/Sub → WebSocket → Clients
```

### Game Flow (Aviator)
```
Player Bet → Redis Queue → Game Engine → Result → PostgreSQL
                              ↓
                         WebSocket Broadcast → All Players
```

## Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.full.yml up -d
```

## Environment Variables

```env
# Database
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://redis:6379/0

# Search
MEILISEARCH_API_KEY=your_master_key

# TON API
TONAPI_KEY=your_tonapi_key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Game Secrets
AVIATOR_SECRET_KEY=random_secret
ROULETTE_SECRET_KEY=random_secret

# URLs
API_URL=https://api.yourdomain.com
WS_URL=wss://api.yourdomain.com
```

## Scaling

### Horizontal Scaling
- API: Multiple instances behind load balancer
- Celery: Add more workers for different queues
- WebSocket: Redis pub/sub for cross-instance messaging

### Caching Strategy
- Redis for hot data (prices, game state)
- Meilisearch for search queries
- PostgreSQL for persistent storage

## Security

- All endpoints require authentication (except public listings)
- Provably fair algorithms for games
- Rate limiting on all APIs
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM
