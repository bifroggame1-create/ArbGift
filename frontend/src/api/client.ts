/**
 * API client for TON Gift Aggregator backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Demo mode - use when API is unavailable
const DEMO_MODE = false

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add Telegram auth if available
    if (window.Telegram?.WebApp?.initData) {
      config.headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// ============================================================
// DEMO DATA - Used when API is unavailable
// ============================================================

const DEMO_GIFTS = [
  { id: 1, name: 'Delicious Cake', rarity: 'common', backdrop: 'Blue', model: 'Cake', symbol: '🎂', lowest_price_ton: 1.5, image_url: 'https://nft.fragment.com/gift-delicious-cake.webp', lottie_url: '/gifts/gift-1.webm' },
  { id: 2, name: 'Red Star', rarity: 'rare', backdrop: 'Red', model: 'Star', symbol: '⭐', lowest_price_ton: 3.2, image_url: 'https://nft.fragment.com/gift-red-star.webp', lottie_url: '/gifts/gift-2.webm' },
  { id: 3, name: 'Spooky Skull', rarity: 'rare', backdrop: 'Purple', model: 'Skull', symbol: '💀', lowest_price_ton: 5.8, image_url: 'https://nft.fragment.com/gift-spooky-skull.webp', lottie_url: '/gifts/gift-3.webm' },
  { id: 4, name: 'Crystal Ball', rarity: 'epic', backdrop: 'Blue', model: 'Crystal', symbol: '🔮', lowest_price_ton: 12.5, image_url: 'https://nft.fragment.com/gift-crystal-ball.webp', lottie_url: '/gifts/gift-4.webm' },
  { id: 5, name: 'Golden Trophy', rarity: 'legendary', backdrop: 'Gold', model: 'Trophy', symbol: '🏆', lowest_price_ton: 45.0, image_url: 'https://nft.fragment.com/gift-golden-trophy.webp', lottie_url: '/gifts/gift-5.webm' },
  { id: 6, name: 'Love Potion', rarity: 'common', backdrop: 'Pink', model: 'Potion', symbol: '💘', lowest_price_ton: 2.1, image_url: 'https://nft.fragment.com/gift-love-potion.webp', lottie_url: '/gifts/gift-6.webm' },
  { id: 7, name: 'Magic Wand', rarity: 'rare', backdrop: 'Purple', model: 'Wand', symbol: '🪄', lowest_price_ton: 4.7, image_url: 'https://nft.fragment.com/gift-magic-wand.webp', lottie_url: '/gifts/gift-7.webm' },
  { id: 8, name: 'Lucky Clover', rarity: 'epic', backdrop: 'Green', model: 'Clover', symbol: '🍀', lowest_price_ton: 18.3, image_url: 'https://nft.fragment.com/gift-lucky-clover.webp', lottie_url: '/gifts/gift-8.webm' },
  { id: 9, name: 'Diamond Ring', rarity: 'legendary', backdrop: 'Blue', model: 'Ring', symbol: '💍', lowest_price_ton: 89.9, image_url: 'https://nft.fragment.com/gift-diamond-ring.webp', lottie_url: '/gifts/gift-9.webm' },
  { id: 10, name: 'Party Balloon', rarity: 'common', backdrop: 'Rainbow', model: 'Balloon', symbol: '🎈', lowest_price_ton: 0.8, image_url: 'https://nft.fragment.com/gift-party-balloon.webp', lottie_url: '/gifts/gift-10.webm' },
  { id: 11, name: 'Durov Cap', rarity: 'mythic', backdrop: 'Blue', model: 'Cap', symbol: '🧢', lowest_price_ton: 250.0, image_url: 'https://nft.fragment.com/gift-durov-cap.webp', lottie_url: '/gifts/gift-11.webm' },
  { id: 12, name: 'Rocket Ship', rarity: 'epic', backdrop: 'Space', model: 'Rocket', symbol: '🚀', lowest_price_ton: 15.5, image_url: 'https://nft.fragment.com/gift-rocket-ship.webp', lottie_url: '/gifts/gift-12.webm' },
]

const DEMO_FILTERS = {
  gift_types: [
    { value: 'Delicious Cake', count: 1500, floor_price: 1.5 },
    { value: 'Red Star', count: 800, floor_price: 3.2 },
    { value: 'Spooky Skull', count: 500, floor_price: 5.8 },
    { value: 'Crystal Ball', count: 200, floor_price: 12.5 },
    { value: 'Golden Trophy', count: 50, floor_price: 45.0 },
  ],
  models: [
    { value: 'Cake', count: 1500 },
    { value: 'Star', count: 800 },
    { value: 'Skull', count: 500 },
    { value: 'Crystal', count: 200 },
    { value: 'Trophy', count: 50 },
  ],
  backdrops: [
    { value: 'Blue', count: 2000 },
    { value: 'Red', count: 800 },
    { value: 'Purple', count: 600 },
    { value: 'Gold', count: 100 },
    { value: 'Rainbow', count: 300 },
  ],
  symbols: [
    { value: '🎂', count: 1500 },
    { value: '⭐', count: 800 },
    { value: '💀', count: 500 },
    { value: '🔮', count: 200 },
    { value: '🏆', count: 50 },
  ],
  patterns: [],
  rarities: [
    { value: 'common', count: 3000 },
    { value: 'rare', count: 1500 },
    { value: 'epic', count: 500 },
    { value: 'legendary', count: 100 },
    { value: 'mythic', count: 10 },
  ],
  price_range: { min: 0.5, max: 500 },
}

// === USER BALANCE ===

export interface UserBalance {
  balance_ton: number
  balance_stars: number
}

export const getUserBalance = async (): Promise<UserBalance> => {
  // Return demo balance in demo mode
  if (DEMO_MODE) {
    return { balance_ton: 10, balance_stars: 1000 }
  }

  try {
    const response = await api.get('/api/v1/user/balance')
    return response.data
  } catch (error) {
    console.warn('API unavailable, using demo balance')
    return { balance_ton: 10, balance_stars: 1000 }
  }
}

// === GIFTS ===

export interface Gift {
  id: number
  address: string
  name: string
  description?: string
  image_url?: string
  animation_url?: string
  rarity?: string
  backdrop?: string
  model?: string
  pattern?: string
  symbol?: string
  collection_id: number
  collection_name?: string
  collection_slug?: string
  is_on_sale: boolean
  lowest_price_ton?: string | number
  lowest_price_market?: string
  attributes?: Array<{ type?: string; trait_type?: string; value: string }>
  listings?: Listing[]
  lottie_url?: string
  min_price_ton?: string
  tg_id?: number
  price?: number
  index?: number
}

export interface Listing {
  id: number
  nft_id: number
  market_slug: string
  market_name: string
  price_ton: string
  seller_address: string
  listing_url: string
  is_active: boolean
}

export const getGifts = async (params?: {
  collection_id?: number
  gift_type?: string
  rarity?: string
  model?: string
  backdrop?: string
  pattern?: string
  symbol?: string
  is_on_sale?: boolean
  price_min?: number
  price_max?: number
  sort_by?: string
  limit?: number
  offset?: number
  search?: string
}) => {
  // Try API first, fallback to demo data
  if (DEMO_MODE) {
    console.log('🎮 [API] Using DEMO_MODE for gifts')
    // Filter and sort demo data
    let items = [...DEMO_GIFTS]

    // Apply filters
    if (params?.gift_type) {
      const types = params.gift_type.split(',')
      items = items.filter(g => types.includes(g.name))
    }
    if (params?.model) {
      const models = params.model.split(',')
      items = items.filter(g => models.includes(g.model || ''))
    }
    if (params?.backdrop) {
      const backdrops = params.backdrop.split(',')
      items = items.filter(g => backdrops.includes(g.backdrop || ''))
    }
    if (params?.price_min) {
      items = items.filter(g => (g.lowest_price_ton || 0) >= params.price_min!)
    }
    if (params?.price_max) {
      items = items.filter(g => (g.lowest_price_ton || 0) <= params.price_max!)
    }

    // Sort
    if (params?.sort_by === 'price asc') {
      items.sort((a, b) => (a.lowest_price_ton || 0) - (b.lowest_price_ton || 0))
    } else if (params?.sort_by === 'price desc') {
      items.sort((a, b) => (b.lowest_price_ton || 0) - (a.lowest_price_ton || 0))
    }

    // Pagination
    const offset = params?.offset || 0
    const limit = params?.limit || 50
    const paginatedItems = items.slice(offset, offset + limit)

    return {
      items: paginatedItems,
      total: items.length,
    }
  }

  try {
    const response = await api.get('/api/v1/gifts', { params })
    return response.data
  } catch (error) {
    console.warn('API unavailable, using demo data')
    return { items: DEMO_GIFTS, total: DEMO_GIFTS.length }
  }
}

export interface FilterOption {
  value: string
  count: number
  floor_price?: number
  image_url?: string
}

export interface FiltersData {
  gift_types: FilterOption[]
  models: FilterOption[]
  backdrops: FilterOption[]
  symbols: FilterOption[]
  patterns: FilterOption[]
  rarities: FilterOption[]
  price_range: { min: number; max: number }
}

export const getFilters = async (params?: {
  gift_type?: string
  is_on_sale?: boolean
}): Promise<FiltersData> => {
  // Use demo data in demo mode
  if (DEMO_MODE) {
    console.log('🎮 [API] Using DEMO_MODE for filters')
    return DEMO_FILTERS as FiltersData
  }

  try {
    const response = await api.get('/api/v1/gifts/filters', { params })
    return response.data
  } catch (error) {
    console.warn('API unavailable, using demo filters')
    return DEMO_FILTERS as FiltersData
  }
}

export const getGift = async (id: number) => {
  const response = await api.get(`/api/v1/gifts/${id}`)
  return response.data
}

export const getGiftListings = async (id: number) => {
  const response = await api.get(`/api/v1/gifts/${id}/listings`)
  return response.data
}

// === SEARCH ===

export const searchGifts = async (query: string, params?: {
  rarity?: string
  price_max?: number
  collection_id?: number
  limit?: number
}) => {
  const response = await api.get('/api/v1/search', { params: { q: query, ...params } })
  return response.data
}

// === STATS ===

export const getStats = async () => {
  const response = await api.get('/api/v1/stats')
  return response.data
}

// === SOLO GAMES (Gonka, Ball Escape) ===

export interface EscapeBuyRequest {
  amount: number
  client_seed: string
  nonce: number
  user_id: string
}

export interface EscapeBuyResponse {
  escaped: boolean
  duration_ms: number
  multiplier: number
  payout: number
  profit: number
  server_seed: string
  server_seed_hash: string
  nonce: number
}

export const escapePlay = async (data: EscapeBuyRequest): Promise<EscapeBuyResponse> => {
  const response = await api.post(`/api/v1/games/solo/escape/play`, data)
  return response.data
}

// === PVP GIFT ROULETTE ===

export interface PvPRoom {
  room_code: string
  room_type: string
  status: string
  total_pool_ton: string
  total_bets: number
  total_players: number
  server_seed_hash: string
  max_players: number
  min_bet_ton: string
  online_count: number
}

export interface PvPBetInfo {
  bet_id: number
  user_id: number
  user_name: string
  user_avatar?: string
  gift_name: string
  gift_image_url?: string
  gift_value_ton: string
  tickets_count: number
  win_chance_percent: string
}

export interface PvPRoomState {
  room_code: string
  room_type: string
  status: string
  total_pool_ton: string
  total_bets: number
  total_players: number
  bets: PvPBetInfo[]
  server_seed_hash: string
  countdown_seconds: number
  online_count: number
}

export interface PvPSpinResult {
  room_code: string
  winner_user_id: number
  winner_user_name: string
  winning_ticket: number
  total_tickets: number
  spin_degree: string
  winnings_ton: string
  house_fee_ton: string
  server_seed: string
}

export interface InventoryNFT {
  address: string
  name: string
  collection_name: string
  image_url?: string
  price_ton?: string
}

export const pvpCreateRoom = async (params: {
  room_type?: string
  min_bet_ton?: number
  max_bet_ton?: number
  max_players?: number
}) => {
  const resp = await api.post(`/api/v1/games/pvp/rooms`, params)
  return resp.data as { room_code: string; server_seed_hash: string; status: string; countdown_seconds: number }
}

export const pvpPlaceBet = async (roomCode: string, data: {
  user_id: number
  user_telegram_id: number
  user_name: string
  user_avatar?: string
  gift_address: string
  gift_name: string
  gift_image_url?: string
  gift_value_ton: number
}, walletAddress?: string) => {
  const headers: Record<string, string> = {}
  if (walletAddress) headers['X-Wallet-Address'] = walletAddress
  const resp = await api.post(`/api/v1/games/pvp/rooms/${roomCode}/bet`, data, { headers })
  return resp.data
}

export const pvpGetRoom = async (roomCode: string): Promise<PvPRoomState> => {
  const resp = await api.get(`/api/v1/games/pvp/rooms/${roomCode}`)
  return resp.data
}

export const pvpListRooms = async (status?: string, limit = 20): Promise<{ total: number; rooms: PvPRoom[] }> => {
  const resp = await api.get(`/api/v1/games/pvp/rooms`, { params: { status, limit } })
  return resp.data
}

export const pvpGetInventory = async (walletAddress: string): Promise<InventoryNFT[]> => {
  const resp = await api.get(`/api/v1/games/pvp/inventory`, { params: { wallet_address: walletAddress } })
  return resp.data
}

// === INVENTORY (MAIN API) ===

export interface InventoryItem {
  id: number
  gift_id: number
  gift: Gift
  telegram_msg_id?: number
  telegram_slug?: string
  acquired_at: string
  source: string
  floor_price_ton_at_acquisition: number
  current_floor_price_ton: number
  profit_loss_ton: number
  is_staked: boolean
  is_locked: boolean
  locked_reason?: string
  is_transferable: boolean
  transfer_fee_stars: number
  is_available_for_betting: boolean
}

export interface InventorySummary {
  total_gifts: number
  total_value_ton: number
  available_for_betting: number
  staked_count: number
  locked_count: number
  total_profit_loss_ton: number
}

export const inventoryGetMy = async (availableOnly = false): Promise<InventoryItem[]> => {
  const resp = await api.get('/api/v1/inventory/me', { params: { available_only: availableOnly } })
  return resp.data
}

export const inventoryGetSummary = async (): Promise<InventorySummary> => {
  const resp = await api.get('/api/v1/inventory/me/summary')
  return resp.data
}

export const inventoryLock = async (inventoryId: number, reason = 'pvp_bet') => {
  const resp = await api.post('/api/v1/inventory/lock', { inventory_id: inventoryId, reason })
  return resp.data
}

export const inventoryUnlock = async (inventoryId: number) => {
  const resp = await api.post(`/api/v1/inventory/unlock/${inventoryId}`)
  return resp.data
}

// === PROVABLY FAIR REVEAL ===
export const revealRound = async (roundId: string) => {
  const resp = await api.get(`/api/v1/games/reveal/${roundId}`)
  return resp.data as { round_id: string; server_seed_hash: string; server_seed: string }
}

// === STAKING SERVICE ===

const STAKING_BASE = import.meta.env.VITE_STAKING_URL || 'http://localhost:8010'

export interface Stake {
  id: string
  user_id: number
  gift_address: string
  gift_name: string
  gift_image_url?: string
  gift_value_ton: string
  period: string
  period_days: number
  apy_percent: string
  expected_reward_ton: string
  status: string
  created_at: string
  unlocks_at: string
  days_remaining: number
  is_unlockable: boolean
}

export interface StakingStats {
  total_stakes: number
  active_stakes: number
  completed_stakes: number
  total_staked_ton: string
  currently_staked_ton: string
  total_rewards_earned_ton: string
  total_penalties_paid_ton: string
  net_profit_ton: string
}

export const stakingGetUserStakes = async (userId: number, status?: string, limit = 20): Promise<Stake[]> => {
  const resp = await axios.get(`${STAKING_BASE}/api/staking/stakes`, { params: { user_id: userId, status, limit } })
  return resp.data
}

export const stakingGetStats = async (userId: number): Promise<StakingStats> => {
  const resp = await axios.get(`${STAKING_BASE}/api/staking/stats/${userId}`)
  return resp.data
}
