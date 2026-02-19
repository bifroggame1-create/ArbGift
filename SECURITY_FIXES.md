# Pending Security Tasks (auto-updated)

- Add commit/reveal flow using `game_rounds` for Plinko/PvP/Solo. Hash returned before bet, seed revealed after.
- Add ledger payout for PvP auto-spin (service or main) and ensure no direct service writes.
- Add rate limiting to all game services (slowapi) similar to main.
- Apply migrations: `20260218_0001_add_balance_operations_and_user_stats.py`, `20260218_0002_add_game_rounds.py` after env setup.
- Set env for prod: TELEGRAM_API_ID/HASH, TELEGRAM_BOT_TOKEN, ADMIN_SECRET_KEY, INTERNAL_API_KEY, ALLOWED_ORIGINS.
- Frontend now calls main API for PvP/Solo; rebuild frontend to pick changes.
