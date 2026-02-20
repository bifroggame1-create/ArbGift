# Gift NFT Betting Integration Guide

This guide explains how to integrate Gift NFT betting into any game view.

## Architecture Overview

### Backend (Already implemented ✅)
- **UserGiftInventory** model tracks gift ownership
- **BalanceOperation** supports `BetCurrency.GIFT`
- **Gift Transfer Service** handles MTProto transfers
- **Inventory API** provides lock/unlock/get methods

### Frontend Pattern

All game integrations follow this 4-step pattern:

## Step-by-Step Integration

### 1. Import Inventory API

```typescript
import {
  inventoryGetMy,
  inventoryLock,
  inventoryUnlock,
  type InventoryItem
} from '@/api/client'
```

### 2. Setup State

Replace direct gift loading with inventory:

```typescript
// OLD: const userGifts = ref<Gift[]>([])
// NEW:
const inventoryItems = ref<InventoryItem[]>([])

// Map to Gift format for existing components
const userGifts = computed(() => {
  return inventoryItems.value
    .filter(item => item.is_available_for_betting)
    .map(item => ({
      ...item.gift,
      inventory_id: item.id,  // IMPORTANT: Add for tracking
      min_price_ton: item.current_floor_price_ton,
    }))
})
```

### 3. Load Inventory

```typescript
const loadGifts = async () => {
  try {
    loading.value = true
    inventoryItems.value = await inventoryGetMy(true) // only available
  } catch (error) {
    console.error('Failed to load inventory:', error)
    inventoryItems.value = []
  } finally {
    loading.value = false
  }
}
```

### 4. Lock Gifts Before Bet

```typescript
const placeBet = async () => {
  // Lock all selected gifts
  for (const inventoryId of selectedGifts.value) {
    try {
      await inventoryLock(inventoryId, 'game_bet') // reason: pvp_bet, contract_input, etc.
    } catch (error) {
      console.error(`Failed to lock gift ${inventoryId}:`, error)
      // Rollback: unlock previously locked
      for (const prevId of selectedGifts.value) {
        if (prevId === inventoryId) break
        await inventoryUnlock(prevId)
      }
      return // Abort bet
    }
  }

  // Proceed with game logic...
}
```

### 5. Unlock After Game

```typescript
// On success or error:
for (const inventoryId of selectedGifts.value) {
  await inventoryUnlock(inventoryId).catch(() => {})
}
```

## Complete Example: PvP Integration

See [PvPView.vue](frontend/src/views/PvPView.vue):

```typescript
// 1. Import
import { inventoryGetMy, inventoryLock, inventoryUnlock, type InventoryItem } from '@/api/client'
import GiftBetModal from '@/components/GiftBetModal.vue'

// 2. State
const inventoryItems = ref<InventoryItem[]>([])
const showBetModal = ref(false)

// 3. Load
onMounted(async () => {
  inventoryItems.value = await inventoryGetMy(true)
})

// 4. Handle Bet
const handleGiftBet = async (item: InventoryItem) => {
  try {
    await inventoryLock(item.id, 'pvp_bet')

    const result = await pvp.placeBet(
      roomCode.value,
      {
        user_id: userId,
        gift_address: item.gift.address,
        gift_value_ton: Number(item.current_floor_price_ton),
      },
      tonConnect.address.value,
    )

    if (!result) {
      await inventoryUnlock(item.id)
    }
  } catch (error) {
    await inventoryUnlock(item.id)
  }
}
```

## Complete Example: Contracts Integration

See [ContractsView.vue](frontend/src/views/ContractsView.vue):

```typescript
// 1. Import
import { inventoryGetMy, inventoryLock, inventoryUnlock, type InventoryItem } from '../api/client'

// 2. State - track inventory_id, not gift_id
const selectedGifts = ref<number[]>([]) // inventory IDs
const inventoryItems = ref<InventoryItem[]>([])

const userGifts = computed(() => {
  return inventoryItems.value
    .filter(item => item.is_available_for_betting)
    .map(item => ({
      ...item.gift,
      inventory_id: item.id,
      min_price_ton: item.current_floor_price_ton,
    }))
})

// 3. Load
const loadGifts = async () => {
  inventoryItems.value = await inventoryGetMy(true)
}

// 4. Execute with locks
const executeContract = async () => {
  // Lock all
  for (const inventoryId of selectedGifts.value) {
    try {
      await inventoryLock(inventoryId, 'contract_input')
    } catch (error) {
      // Rollback
      for (const prevId of selectedGifts.value) {
        if (prevId === inventoryId) break
        await inventoryUnlock(prevId)
      }
      return
    }
  }

  // Execute game...

  // Unlock all after
  for (const inventoryId of selectedGifts.value) {
    await inventoryUnlock(inventoryId).catch(() => {})
  }
}
```

## Using GiftBetModal Component

For single-gift selection (like PvP), use the pre-built modal:

```vue
<template>
  <button @click="showBetModal = true">Bet Gift</button>

  <GiftBetModal
    :open="showBetModal"
    :items="inventoryItems"
    :loading="inventoryLoading"
    :server-seed-hash="serverHash"
    @close="showBetModal = false"
    @confirm="handleGiftBet"
  />
</template>

<script setup>
import GiftBetModal from '@/components/GiftBetModal.vue'
import { inventoryGetMy, type InventoryItem } from '@/api/client'

const inventoryItems = ref<InventoryItem[]>([])
const showBetModal = ref(false)

onMounted(async () => {
  inventoryItems.value = await inventoryGetMy(true)
})

const handleGiftBet = async (item: InventoryItem) => {
  // Lock, bet, unlock...
}
</script>
```

## Key Points

### ✅ DO:
- Always use `inventoryGetMy(true)` to get only available gifts
- Lock gifts BEFORE sending bet to backend
- Unlock gifts after game completes OR on error
- Track `inventory_id`, not `gift_id` for selections
- Use `current_floor_price_ton` for valuation
- Add rollback logic if any lock fails

### ❌ DON'T:
- Don't use `getGifts()` - that's for marketplace, not inventory
- Don't skip locking - prevents double-betting
- Don't forget to unlock on errors - gifts get stuck
- Don't use `gift_id` for tracking - use `inventory_id`
- Don't allow betting locked/staked gifts - check `is_available_for_betting`

## Game-Specific Reasons

Use descriptive `locked_reason` for better UX:

| Game | Reason |
|------|--------|
| PvP Roulette | `pvp_bet` |
| Contracts | `contract_input` |
| Plinko | `plinko_bet` |
| Trading | `trading_bet` |
| Upgrade | `upgrade_input` |
| Staking | (uses `is_staked` flag, not locked) |

## API Reference

### `inventoryGetMy(availableOnly?: boolean): Promise<InventoryItem[]>`

Fetch user's gift inventory.

**Parameters:**
- `availableOnly` - If true, only returns gifts where `is_available_for_betting=true`

**Returns:** Array of inventory items with gift details and floor prices.

### `inventoryLock(inventoryId: number, reason: string): Promise<void>`

Lock a gift for active bet/game.

**Parameters:**
- `inventoryId` - ID from UserGiftInventory (NOT gift_id!)
- `reason` - Why locked (e.g., "pvp_bet", "contract_input")

**Throws:** Error if gift already locked, staked, or not found.

### `inventoryUnlock(inventoryId: number): Promise<void>`

Unlock a gift after game completion.

**Parameters:**
- `inventoryId` - ID from UserGiftInventory

**Note:** Safe to call multiple times (idempotent).

## Testing Checklist

When integrating into a new game, verify:

- [ ] Loads inventory on mount
- [ ] Shows only available gifts (not locked/staked)
- [ ] Locks gifts before bet
- [ ] Unlocks gifts after win/loss
- [ ] Unlocks gifts on error
- [ ] Prevents double-betting same gift
- [ ] Shows current floor prices
- [ ] Handles empty inventory gracefully
- [ ] Works with both TON and Gift betting
- [ ] Updates inventory after game completion

## Integration Status

| Game | Status | Notes |
|------|--------|-------|
| **PvP Roulette** | ✅ Complete | Uses GiftBetModal, single gift betting |
| **Contracts** | ✅ Complete | Multi-gift selection (2-10), lock/unlock all |
| **Plinko** | ⏳ Pending | Single gift, similar to PvP pattern |
| **Trading** | ⏳ Pending | Single gift crash betting |
| **Upgrade** | ⏳ Pending | Gift transformation, 1 input → 1 output |
| **Staking** | ⏳ Pending | Uses `is_staked` flag, different pattern |
| **Solo Games** | ⏳ Pending | Game-specific implementations |

## Next Steps

1. Complete remaining game integrations
2. Add backend gift transfer on win/loss
3. Test with real Telegram MTProto transfers
4. Add P2P internal market
5. Production deployment

For questions or issues, check:
- [app/api/v1/inventory.py](app/api/v1/inventory.py) - Backend inventory API
- [app/models/inventory.py](app/models/inventory.py) - UserGiftInventory model
- [frontend/src/components/GiftBetModal.vue](frontend/src/components/GiftBetModal.vue) - Reusable modal
- [services/gift-transfer/README.md](services/gift-transfer/README.md) - MTProto service
