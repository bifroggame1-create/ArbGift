# Gift Transfer Service

Microservice for Telegram Gift NFT operations via MTProto API (Telethon).

## Features

- **Gift Inventory Sync**: Fetch user's gifts from Telegram
- **Gift Transfers**: Transfer gifts between users via MTProto
- **Ownership Verification**: Verify gift ownership on-chain
- **Gift Details**: Get detailed metadata about gifts

## Setup

### 1. Get Telegram API Credentials

1. Visit https://my.telegram.org
2. Login with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy `api_id` and `api_hash`

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890
ADMIN_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ton_gifts
```

### 3. First-Time Authorization

MTProto requires user account authorization (not bot):

```bash
cd services/gift-transfer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run authorization script
python -c "from app.core.telethon_client import get_telethon_client; import asyncio; asyncio.run(get_telethon_client())"

# Enter the code sent to your Telegram
```

Session will be saved to `gift_transfer_session.session` file.

### 4. Run Service

```bash
python app/main.py
```

Or with Docker:
```bash
docker build -t gift-transfer .
docker run -p 8010:8010 --env-file .env gift-transfer
```

## API Endpoints

All endpoints require `X-Admin-Key` header for authentication.

### POST /sync-user-gifts

Fetch user's gift inventory from Telegram.

**Request:**
```json
{
  "telegram_user_id": 123456789,
  "limit": 100
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 123456789,
  "gifts_count": 5,
  "gifts": [
    {
      "msg_id": 12345,
      "slug": "delicious_cake_unique_00001",
      "title": "Delicious Cake",
      "num": 1,
      "transfer_stars": 0,
      "can_upgrade": false,
      "can_export": true
    }
  ]
}
```

### POST /transfer-gift

Transfer gift ownership between users.

**Request:**
```json
{
  "from_user_id": 123456789,
  "to_user_id": 987654321,
  "gift_msg_id": 12345
}
```

**Response:**
```json
{
  "success": true,
  "msg_id": 12345,
  "from_user_id": 123456789,
  "to_user_id": 987654321,
  "timestamp": "2026-02-19T12:00:00"
}
```

### POST /verify-ownership

Verify user owns a gift.

**Request:**
```json
{
  "user_id": 123456789,
  "gift_slug": "delicious_cake_unique_00001"
}
```

**Response:**
```json
{
  "user_id": 123456789,
  "gift_slug": "delicious_cake_unique_00001",
  "owns_gift": true
}
```

### POST /gift-details

Get detailed gift information.

**Request:**
```json
{
  "user_id": 123456789,
  "gift_msg_id": 12345
}
```

**Response:**
```json
{
  "success": true,
  "gift": {
    "msg_id": 12345,
    "slug": "delicious_cake_unique_00001",
    "title": "Delicious Cake",
    "gift_id": 1,
    "owner_id": 123456789
  }
}
```

## Integration with Main API

Main API calls this service for gift operations:

```python
import httpx

GIFT_TRANSFER_URL = "http://localhost:8010"
ADMIN_KEY = os.getenv("ADMIN_SECRET_KEY")

# Sync user gifts
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{GIFT_TRANSFER_URL}/sync-user-gifts",
        json={"telegram_user_id": user.telegram_id, "limit": 100},
        headers={"X-Admin-Key": ADMIN_KEY},
    )
    data = response.json()
    gifts = data["gifts"]
```

## Security Notes

- **Never share your API credentials** - they are tied to your Telegram account
- **Session file** contains authorization - keep it secure
- **Admin key** should be strong and match main API
- Service runs as a **user account**, not a bot (MTProto limitation)

## Troubleshooting

**"First-time authorization required" error:**
- Run the authorization script manually (see step 3)
- Session file will be created
- Restart service

**"Invalid admin key" error:**
- Check `ADMIN_SECRET_KEY` matches main API
- Include `X-Admin-Key` header in all requests

**Connection timeout:**
- Check Telegram is not blocking your IP
- Try using MTProto proxy
- Verify `api_id` and `api_hash` are correct

## References

- [Telegram MTProto API - Gifts](https://core.telegram.org/api/gifts)
- [Telethon Documentation](https://docs.telethon.dev/)
- [TransferStarGiftRequest](https://tl.telethon.dev/methods/payments/transfer_star_gift.html)
- [GetSavedStarGiftsRequest](https://tl.telethon.dev/methods/payments/get_saved_star_gifts.html)

**Sources:**
- [Telegram Gift API](https://core.telegram.org/api/gifts)
- [Telethon TelegramClient](https://docs.telethon.dev/en/stable/modules/client.html)
- [Signing In with Telethon](https://docs.telethon.dev/en/stable/basic/signing-in.html)
