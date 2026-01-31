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
  rarity?: string
  backdrop?: string
  model?: string
  collection_id: number
  collection_name?: string
  is_on_sale: boolean
  min_price_ton?: string
  listings_count: number
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

// === COLLECTIONS ===

export const getCollections = async () => {
  const response = await api.get('/api/v1/collections')
  return response.data
}

// === MARKETS ===

export const getMarkets = async () => {
  const response = await api.get('/api/v1/markets')
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

export const autocomplete = async (query: string) => {
  const response = await api.get('/api/v1/search/autocomplete', { params: { q: query } })
  return response.data
}

// === STATS ===

export const getStats = async () => {
  const response = await api.get('/api/v1/stats')
  return response.data
}

// === CONTRACTS GAME ===

export interface CreateContractRequest {
  gift_ids: number[]
  risk_level: 'safe' | 'normal' | 'risky'
  client_seed: string
}

export interface CreateContractResponse {
  contract_id: string
  server_seed_hash: string
  estimated_probability: number
  potential_payout: string
}

export interface ExecuteContractResponse {
  success: boolean
  won: boolean
  multiplier: number
  payout_value: string
  reward_gift_id?: number
  server_seed: string
  proof: {
    server_seed_hash: string
    server_seed: string
    client_seed: string
    nonce: number
    risk_level: string
  }
}

export interface ContractHistoryItem {
  id: string
  risk_level: string
  won: boolean
  total_input_value_ton: string
  payout_value_ton?: string
  created_at: string
  resolved_at?: string
}

export const createContract = async (data: CreateContractRequest): Promise<CreateContractResponse> => {
  const response = await api.post('/api/contracts/create', data)
  return response.data
}

export const executeContract = async (contractId: string): Promise<ExecuteContractResponse> => {
  const response = await api.post(`/api/contracts/${contractId}/execute`)
  return response.data
}

export const getContractHistory = async (params?: {
  limit?: number
  offset?: number
}) => {
  const response = await api.get('/api/contracts/history', { params })
  return response.data
}

export const verifyContract = async (contractId: string) => {
  const response = await api.get(`/api/contracts/${contractId}/verify`)
  return response.data
}

// === UPGRADE GAME ===

export interface CalculateUpgradeRequest {
  input_gift_id: number
  target_gift_id: number
}

export interface CalculateUpgradeResponse {
  input_value: string
  target_value: string
  success_probability: number
  wheel_sectors: {
    success_angle: number
    fail_angle: number
  }
  expected_value: string
}

export interface CreateUpgradeRequest {
  input_gift_id: number
  target_gift_id: number
  client_seed: string
}

export interface CreateUpgradeResponse {
  upgrade_id: string
  server_seed_hash: string
  probability: number
  wheel_sectors: {
    success_angle: number
    fail_angle: number
  }
}

export interface SpinWheelResponse {
  success: boolean
  won: boolean
  result_angle: number
  server_seed: string
  animation_duration: number
}

export interface UpgradeHistoryItem {
  id: string
  won: boolean
  input_gift_value_ton: string
  target_gift_value_ton: string
  success_probability: number
  created_at: string
  resolved_at?: string
}

export const calculateUpgrade = async (data: CalculateUpgradeRequest): Promise<CalculateUpgradeResponse> => {
  const response = await api.post('/api/upgrade/calculate', data)
  return response.data
}

export const createUpgrade = async (data: CreateUpgradeRequest): Promise<CreateUpgradeResponse> => {
  const response = await api.post('/api/upgrade/create', data)
  return response.data
}

export const spinWheel = async (upgradeId: string): Promise<SpinWheelResponse> => {
  const response = await api.post(`/api/upgrade/${upgradeId}/spin`)
  return response.data
}

export const getUpgradeHistory = async (params?: {
  limit?: number
  offset?: number
}) => {
  const response = await api.get('/api/upgrade/history', { params })
  return response.data
}

// === SOLO GAMES (Plinko, Gonka, Ball Escape) ===

const SOLO_GAMES_BASE = import.meta.env.VITE_SOLO_GAMES_URL || 'http://localhost:8007'

export interface PlinkoBuyRequest {
  amount: number
  client_seed: string
  nonce: number
  user_id: string
}

export interface PlinkoBuyResponse {
  landing_slot: number
  slot_label: string
  multiplier: number
  payout: number
  profit: number
  path: [number, number][]
  server_seed: string
  server_seed_hash: string
  nonce: number
}

export const plinkoPlay = async (data: PlinkoBuyRequest): Promise<PlinkoBuyResponse> => {
  const response = await axios.post(`${SOLO_GAMES_BASE}/api/solo-plinko-game/buy/ton`, data)
  return response.data
}

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
