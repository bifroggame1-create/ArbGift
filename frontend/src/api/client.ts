/**
 * API client for TON Gift Aggregator backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  rarity?: string
  model?: string
  backdrop?: string
  pattern?: string
  symbol?: string
  is_on_sale?: boolean
  min_price?: number
  max_price?: number
  sort?: string
  limit?: number
  offset?: number
}) => {
  const response = await api.get('/api/v1/gifts', { params })
  return response.data
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

const SOLO_GAMES_BASE = import.meta.env.VITE_SOLO_GAMES_URL || 'http://localhost:8007'

export interface GonkaBuyRequest {
  amount: number
  mode: string
  client_seed: string
  nonce: number
  user_id: string
}

export interface GonkaBuyResponse {
  cell_index: number
  mode: string
  multiplier: number
  balls: number
  payout: number
  profit: number
  server_seed: string
  server_seed_hash: string
  nonce: number
}

export const gonkaPlay = async (data: GonkaBuyRequest): Promise<GonkaBuyResponse> => {
  const response = await axios.post(`${SOLO_GAMES_BASE}/api/solo-race-game/buy/ton`, data)
  return response.data
}

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
  const response = await axios.post(`${SOLO_GAMES_BASE}/api/solo-escape-game/buy/ton`, data)
  return response.data
}

// === PVP GIFT ROULETTE ===

const PVP_BASE = import.meta.env.VITE_PVP_URL || 'http://localhost:8009'

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
  const resp = await axios.post(`${PVP_BASE}/api/pvp/rooms`, params)
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
  const resp = await axios.post(`${PVP_BASE}/api/pvp/rooms/${roomCode}/bet`, data, { headers })
  return resp.data
}

export const pvpGetRoom = async (roomCode: string): Promise<PvPRoomState> => {
  const resp = await axios.get(`${PVP_BASE}/api/pvp/rooms/${roomCode}`)
  return resp.data
}

export const pvpListRooms = async (status?: string, limit = 20): Promise<{ total: number; rooms: PvPRoom[] }> => {
  const resp = await axios.get(`${PVP_BASE}/api/pvp/rooms`, { params: { status, limit } })
  return resp.data
}

export const pvpGetInventory = async (walletAddress: string): Promise<InventoryNFT[]> => {
  const resp = await axios.get(`${PVP_BASE}/api/pvp/inventory/user/${walletAddress}`)
  return resp.data
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
