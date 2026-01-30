# CLAUDE.md

This file provides guidance to Claude Code when working with the TON Gift Aggregator codebase.

## Project Overview

TON Gift Aggregator is a full-stack platform for aggregating Telegram Gift NFTs from multiple TON marketplaces with integrated gaming features. Built with FastAPI backend microservices and Vue 3 + TypeScript frontend as a Telegram Mini App.

**Main API Entry Point:** `app/main.py`
**Frontend Entry Point:** `frontend/src/main.ts`

## Architecture

### Microservices Structure
The project follows a microservices architecture with domain-separated services:

- **Main API** (Port 8000): Gift aggregation, WebSocket, Search
- **Aviator Game** (Port 8001): Crash betting game
- **Roulette Game** (Port 8002): Classic + Gift roulette
- **Stars Service** (Port 8003): Buy Telegram Stars with TON
- **Contracts Game** (Port 8004): Risk-based gift gambling
- **Upgrade Game** (Port 8005): Gift transformation with probability wheel
- **Frontend** (Port 3000): Vue.js Telegram Mini App

Each service has its own FastAPI app, database schema, and dependencies managed independently.

### Frontend Architecture

**Gaming Hub Pattern:**
All game modes are accessed through a central Gaming Hub (TopUpView.vue) rather than separate top-level routes. This provides a unified game selection experience.

```
BottomNavigation (TabBar)
  ├── Home (GiftsView)
  ├── Search (SearchView)
  ├── Games (TopUpView) ← CENTER BUTTON
  ├── Profile (ProfileView)
  └── More (MoreView)

TopUpView (Gaming Hub)
  ├── Contracts Card → /contracts
  ├── Upgrade Card → /upgrade
  ├── Aviator Card → /aviator
  ├── Roulette Card → /roulette
  └── Stars Card → /stars
```

The center tab bar button navigates to `/topup` which displays the Gaming Hub with cards for each game mode.

### Database Layer
- **ORM**: SQLAlchemy 2.0+ with async support
- **Migrations**: Alembic
- **Connection Pooling**: Configured in database/session.py
- **Models**: Domain models in `app/models/` for main API, separate models in each service

### Real-time Communication
- **WebSocket**: Redis Pub/Sub for price updates
- **Channels**:
  - `/ws/prices` - All price updates
  - `/ws/collection/{id}` - Collection-specific
  - `/ws/gift/{id}` - Single gift updates

### Search
- **Engine**: Meilisearch
- **Indexed Fields**: NFT names, descriptions, metadata
- **Features**: Full-text search, autocomplete, typo tolerance

## Game Interface Standards

### Design System
All game interfaces must adhere to the design system documented in `/docs/STYLE_GUIDE.md`. Key principles:

**Risk Theme Colors:**
- Safe Mode: `#10B981` (green) with `#34D399` accents
- Normal Mode: `#3B82F6` (blue) with `#60A5FA` accents
- Risky Mode: `#EF4444` (red) with `#F97316` (orange), includes flame pulse animations

**Component Library:**
- **REQUIRED**: Use `@telegram-apps/telegram-ui` for all UI components
- Import patterns: `import { Section, Card, Button, Modal } from '@telegram-apps/telegram-ui'`
- Never create custom components that duplicate TelegramUI functionality

**Gift Card Design:**
Gift cards must match the portals.tg reference design:
- 3D model/icon centered in card (70% width/height)
- Gradient background based on rarity (common: gray, rare: blue, epic: purple, legendary: gold)
- Rounded corners: 16px
- Price badge at bottom with 💎 icon
- Serial number display (format: #156891)
- Selection state: checkmark overlay with green tint
- Aspect ratio: 1:1 (square cards)

**Typography Scale (from TelegramUI):**
- Title1: 28px, weight 700 (headers)
- Title2: 24px, weight 600 (section headers)
- Headline: 18px, weight 600 (card titles)
- Body: 16px, weight 400 (main text)
- Caption: 12px, weight 400 (metadata)

**Spacing Grid:**
- Base unit: 4px
- Card padding: 16px
- Gap between cards: 12px
- Section margins: 24px

**Animations:**
```css
/* Flame effect for Risky mode */
@keyframes flame-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }
  50% { box-shadow: 0 0 40px rgba(239, 68, 68, 0.8); }
}

/* Wheel spin for Upgrade mode */
@keyframes wheel-spin {
  /* 3 full rotations + final angle */
  /* Use cubic-bezier(0.25, 0.1, 0.25, 1) easing */
  /* Duration: 3000ms */
}

/* Success confetti */
@keyframes confetti-fall {
  /* Particle animation for win states */
}
```

### Haptic Feedback (Telegram WebApp SDK)
All interactive elements MUST provide haptic feedback:

```typescript
import { useTelegram } from '@/composables/useTelegram'

const { hapticImpact } = useTelegram()

// Light: UI selections, toggles
hapticImpact('light')

// Medium: Button presses, navigation
hapticImpact('medium')

// Heavy: Confirmations, game execution
hapticImpact('heavy')
```

### Loading States
All async operations require visual loading feedback:
- Buttons: Use `:loading` prop from TelegramUI Button component
- Page loads: Full-page spinner or skeleton screens
- Data fetches: Skeleton cards matching final layout

### Error Handling
- Display user-friendly error messages in TelegramUI Toast/Alert components
- Never show raw API errors or stack traces to users
- Log errors to console for debugging
- Provide actionable recovery options (retry buttons)

### Responsive Design
- Design mobile-first (Telegram Mini Apps are primarily mobile)
- Test at 360px, 390px, 428px widths
- Use viewport units (vh, vw) sparingly due to iOS Safari issues
- Bottom navigation must account for iOS safe area

### Accessibility
- Maintain 4.5:1 contrast ratio minimum
- Touch targets: minimum 44x44px
- Provide text alternatives for icon-only buttons
- Support dark mode (Telegram's native theme)

## Development Commands

### Backend Development
```bash
# Start main API (development)
uvicorn app.main:app --reload --port 8000

# Start specific game service
cd services/contracts
uvicorn app.main:app --reload --port 8004

# Run Celery worker for background tasks
celery -A app.workers.celery_app worker -l info

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Seed initial data
python scripts/seed_markets.py
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

### Docker Development
```bash
# Start infrastructure only (postgres, redis, meilisearch)
docker-compose up -d postgres redis meilisearch

# Full stack deployment
docker-compose -f docker-compose.full.yml up -d

# View logs
docker-compose -f docker-compose.full.yml logs -f api

# Rebuild specific service
docker-compose -f docker-compose.full.yml build contracts-api
```

## Configuration

### Environment Variables
Key variables in `.env`:

```env
# Main API
TONAPI_KEY=<from tonconsole.com>
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://localhost:6379/0
MEILISEARCH_API_KEY=<master key>

# Game Services
CONTRACTS_SECRET_KEY=<random string>
UPGRADE_SECRET_KEY=<random string>

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Market Adapters
Marketplace adapters in `app/adapters/`:
- GetGems: GraphQL API
- Fragment: TON API based
- MRKT: REST with Telegram auth
- Tonnel: REST API
- TON API Sales: Blockchain event fallback

Each adapter implements `BaseMarketAdapter` interface with rate limiting and error handling.

## Common Development Tasks

### Adding a New Game Mode

1. **Create service directory:**
   ```bash
   mkdir -p services/new-game/app/{models,services,api}
   ```

2. **Define models** in `services/new-game/app/models/game.py`:
   ```python
   from app.database.base import Base, TimestampMixin
   from sqlalchemy import Column, Integer, String, Enum

   class Game(Base, TimestampMixin):
       __tablename__ = "games"
       id = Column(Integer, primary_key=True)
       # ... fields
   ```

3. **Create game engine** in `services/new-game/app/services/engine.py`:
   ```python
   class GameEngine:
       def calculate_result(self, params):
           # Implement provably fair algorithm
           pass
   ```

4. **Define API endpoints** in `services/new-game/app/api/game.py`:
   ```python
   from fastapi import APIRouter

   router = APIRouter()

   @router.post("/create")
   async def create_game():
       pass
   ```

5. **Create Vue component** in `frontend/src/views/NewGameView.vue`:
   ```vue
   <template>
     <div class="new-game-view">
       <Section header="New Game">
         <!-- Use TelegramUI components -->
       </Section>
     </div>
   </template>
   ```

6. **Add to Gaming Hub** in `frontend/src/views/TopUpView.vue`:
   ```vue
   <GameCard
     title="New Game"
     icon="🎮"
     description="Description"
     @click="router.push('/new-game')"
   />
   ```

7. **Update docker-compose.full.yml:**
   ```yaml
   new-game-api:
     build: ./services/new-game
     ports:
       - "8006:8000"
     environment:
       DATABASE_URL: postgresql+asyncpg://...
   ```

8. **Configure nginx routing** in `nginx/nginx.conf`:
   ```nginx
   location /api/new-game/ {
       proxy_pass http://new-game-api:8000;
   }
   ```

### Adding a Marketplace Adapter

1. **Create adapter file** in `app/adapters/new_market.py`:
   ```python
   from app.adapters.base import BaseMarketAdapter
   from decimal import Decimal

   class NewMarketAdapter(BaseMarketAdapter):
       def __init__(self):
           super().__init__(
               slug="newmarket",
               name="New Market",
               base_url="https://api.newmarket.com",
               fee_buy_percent=Decimal("2.5"),
               fee_sell_percent=Decimal("2.5"),
           )

       async def fetch_listings(self, collection_address: str):
           # Implement API integration
           pass
   ```

2. **Register in adapter registry** (`app/adapters/__init__.py`):
   ```python
   from app.adapters.new_market import NewMarketAdapter

   def get_all_adapters():
       return [
           # ... existing adapters
           NewMarketAdapter(),
       ]
   ```

3. **Seed market data:**
   ```python
   # Add to scripts/seed_markets.py
   Market(
       slug="newmarket",
       name="New Market",
       url="https://newmarket.com",
       # ...
   )
   ```

### Implementing Provably Fair Algorithms

All gambling games must use provably fair algorithms:

```python
import hashlib
from decimal import Decimal

class ProvablyFairEngine:
    def generate_server_seed(self) -> str:
        """Generate cryptographically secure server seed"""
        import secrets
        return secrets.token_hex(64)

    def hash_server_seed(self, server_seed: str) -> str:
        """Hash server seed for client verification"""
        return hashlib.sha256(server_seed.encode()).hexdigest()

    def generate_result(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
    ) -> float:
        """Generate verifiable random number 0-1"""
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()

        # Use first 8 chars as random value
        random_value = int(hash_hex[:8], 16) / (16**8)
        return random_value

    def verify_result(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
        claimed_result: float,
    ) -> bool:
        """Allow client to verify result"""
        actual_result = self.generate_result(server_seed, client_seed, nonce)
        return abs(actual_result - claimed_result) < 0.0001
```

Server seed must be:
- Generated before client seed
- Hashed and shown to client before game
- Revealed to client after game completes
- Stored in database for verification

## Testing

### Backend Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_adapters.py -v
```

### Frontend Testing (Playwright)
```bash
cd frontend

# Run tests headless
npx playwright test

# Run tests with UI
npx playwright test --ui

# Generate test code
npx playwright codegen http://localhost:3000
```

Example test structure:
```typescript
import { test, expect } from '@playwright/test'

test('Contracts: Execute safe contract', async ({ page }) => {
  await page.goto('/contracts')

  // Select gifts
  await page.click('.gift-card-wrapper:nth-child(1)')
  await page.click('.gift-card-wrapper:nth-child(2)')

  // Select risk level
  await page.click('.risk-button.safe')

  // Execute
  await page.click('button:has-text("Execute Contract")')

  // Verify result modal
  await expect(page.locator('.result-content')).toBeVisible()
})
```

## Database Management

### Backup and Restore
```bash
# Export to JSON
python utils/db_json_manager.py export backup.json

# Import from JSON
python utils/db_json_manager.py import backup.json

# Import with overwrite (⚠️ destructive)
python utils/db_json_manager.py import backup.json --overwrite
```

### Migrations
```bash
# Create migration
alembic revision --autogenerate -m "add contracts table"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## Debugging

### Backend Debugging
- FastAPI auto-generated docs: `http://localhost:8000/docs`
- Redis monitoring: `redis-cli monitor`
- Database queries: Set `echo=True` in SQLAlchemy engine config
- Celery tasks: `celery -A app.workers.celery_app flower` (port 5555)

### Frontend Debugging
- Vue DevTools browser extension
- Vite dev server console output
- Network tab for API calls
- Telegram WebApp debug mode: `Telegram.WebApp.isVersionAtLeast('6.1')`

## Known Issues and Limitations

### TON API Rate Limits
TON API has rate limits. Implement exponential backoff in adapters:
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
async def fetch_with_retry(url: str):
    # API call
    pass
```

### Meilisearch Memory Usage
Meilisearch can use significant memory. For production:
- Allocate at least 2GB RAM
- Configure `--max-indexing-memory` and `--max-indexing-threads`
- Monitor with `GET /stats` endpoint

### WebSocket Connection Limits
Redis Pub/Sub can handle thousands of connections, but nginx needs configuration:
```nginx
worker_rlimit_nofile 40000;

events {
    worker_connections 8096;
}
```

### Telegram Mini App Quirks
- iOS Safari viewport height changes on scroll
- Back button must be handled via Telegram.WebApp.BackButton
- Haptic feedback only works in Telegram app (not web browser)
- File uploads require Telegram.WebApp.requestFileAccess()

## Security Considerations

### API Security
- All endpoints use rate limiting (via `slowapi`)
- Admin endpoints check user ID against `ADMIN_IDS` env var
- Database queries use parameterized queries (SQLAlchemy ORM)
- CORS configured for Telegram origins only

### Game Fairness
- Server seeds generated with `secrets` module (cryptographically secure)
- Seeds stored in database for post-game verification
- Client can verify results independently
- House edge clearly documented in API responses

### User Data
- Minimal data collection (Telegram ID, username only)
- No email or phone number storage
- TON wallet addresses stored for payment processing only
- GDPR compliance: users can request data deletion via admin

## Performance Optimization

### Backend
- Database connection pooling (20 connections, 10 overflow)
- Redis caching for expensive queries (TTL: 300s)
- Celery for async tasks (collection indexing, metadata updates)
- Batch database operations where possible

### Frontend
- Code splitting per route
- Image lazy loading
- Meilisearch for instant search (< 10ms)
- WebSocket for real-time updates (no polling)

### Infrastructure
- Nginx reverse proxy with caching
- Static asset CDN (optional, configurable)
- Docker multi-stage builds for smaller images
- Horizontal scaling via Docker Swarm/Kubernetes (future)

## Dependencies

### Backend (Python 3.11+)
- **fastapi** - Web framework
- **sqlalchemy** - ORM
- **alembic** - Database migrations
- **redis** - Caching and pub/sub
- **celery** - Background tasks
- **meilisearch-python** - Search client
- **tonapi** - TON blockchain API client

### Frontend
- **vue** 3.4+ - UI framework
- **typescript** 5.3+ - Type safety
- **vite** - Build tool
- **pinia** - State management
- **@telegram-apps/telegram-ui** - Component library
- **@telegram-apps/sdk** - Telegram Mini App SDK

## Deployment

### Production Checklist
- [ ] Set `DEBUG=false` in environment
- [ ] Generate secure `SECRET_KEY` for each service
- [ ] Configure PostgreSQL with SSL
- [ ] Set up Redis password authentication
- [ ] Configure Meilisearch master key
- [ ] Set up nginx with SSL certificates
- [ ] Enable Celery monitoring (Flower)
- [ ] Configure log aggregation
- [ ] Set up automated database backups
- [ ] Configure monitoring and alerting

### Deployment Commands
```bash
# Build all images
docker-compose -f docker-compose.full.yml build

# Start in detached mode
docker-compose -f docker-compose.full.yml up -d

# View logs
docker-compose -f docker-compose.full.yml logs -f

# Scale workers
docker-compose -f docker-compose.full.yml up -d --scale celery-worker=3

# Stop all services
docker-compose -f docker-compose.full.yml down
```

## Contributing

### Code Style
- **Python**: Follow PEP 8, use `black` formatter, `ruff` linter
- **TypeScript**: Follow Vue style guide, use Prettier, ESLint
- **Commits**: Conventional commits format (`feat:`, `fix:`, `docs:`)

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite
4. Update documentation if needed
5. Submit PR with description

### Review Criteria
- Code passes all tests
- No type errors (`mypy` for Python, `tsc` for TypeScript)
- Follows style guide
- Includes appropriate documentation
- Game interfaces follow design system

## Resources

- [TON Documentation](https://ton.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vue 3 Documentation](https://vuejs.org)
- [TelegramUI Components](https://github.com/Telegram-Web-Apps/telegram-ui)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)
- [Meilisearch Docs](https://docs.meilisearch.com)
