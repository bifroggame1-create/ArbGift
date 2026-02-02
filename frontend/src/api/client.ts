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
  pattern?: string
  symbol?: string
  collection_id: number
  collection_name?: string
  is_on_sale: boolean
  min_price_ton?: string
  listings_count: number
  tg_id?: number
  price?: number
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

export const soloPlinkoPlay = async (data: PlinkoBuyRequest): Promise<PlinkoBuyResponse> => {
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

// === PVP GIFT ROULETTE ===

const PVP_BASE = import.meta.env.VITE_PVP_URL || 'http://localhost:8009'

// Types

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

export interface PvPUserStats {
  user_id: number
  total_wins: number
  total_losses: number
  total_games: number
  total_wagered_ton: string
  total_won_ton: string
  total_profit_ton: string
  current_win_streak: number
  max_win_streak: number
  biggest_win_ton: string
}

export interface InventoryNFT {
  address: string
  name: string
  collection_name: string
  image_url?: string
  price_ton?: string
}

// API calls

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

export const pvpSpinWheel = async (roomCode: string, clientSeed?: string): Promise<PvPSpinResult> => {
  const resp = await axios.post(`${PVP_BASE}/api/pvp/rooms/${roomCode}/spin`, null, { params: { client_seed: clientSeed } })
  return resp.data
}

export const pvpVerify = async (roomCode: string, serverSeed: string, clientSeed: string, nonce = 0) => {
  const resp = await axios.post(`${PVP_BASE}/api/pvp/rooms/${roomCode}/verify`, null, {
    params: { server_seed: serverSeed, client_seed: clientSeed, nonce },
  })
  return resp.data
}

export const pvpGetUserStats = async (userId: number): Promise<PvPUserStats> => {
  const resp = await axios.get(`${PVP_BASE}/api/pvp/stats/${userId}`)
  return resp.data
}

export const pvpGetInventory = async (walletAddress: string): Promise<InventoryNFT[]> => {
  const resp = await axios.get(`${PVP_BASE}/api/pvp/inventory/user/${walletAddress}`)
  return resp.data
}

// === STAKING SERVICE ===

const STAKING_BASE = import.meta.env.VITE_STAKING_URL || 'http://localhost:8010'

export interface StakePeriod {
  period: string
  days: number
  apy_percent: string
}

export interface StakePreview {
  valid: boolean
  error?: string
  gift_value_ton: string
  period: string
  period_days: number
  apy_percent: string
  expected_reward_ton: string
  unlock_date: string
}

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

export interface UnstakeResult {
  stake_id: string
  status: string
  gift_value_ton: string
  reward_ton: string
  penalty_ton: string
  total_payout_ton: string
  early_withdrawal: boolean
}

export const stakingGetPeriods = async () => {
  const resp = await axios.get(`${STAKING_BASE}/api/staking/periods`)
  return resp.data as { periods: StakePeriod[]; min_stake_ton: string; early_withdrawal_penalty_percent: string }
}

export const stakingPreview = async (giftValueTon: number, period: string): Promise<StakePreview> => {
  const resp = await axios.post(`${STAKING_BASE}/api/staking/preview`, {
    gift_value_ton: giftValueTon,
    period,
  })
  return resp.data
}

export const stakingCreateStake = async (data: {
  user_id: number
  user_telegram_id: number
  user_name: string
  gift_address: string
  gift_name: string
  gift_image_url?: string
  gift_value_ton: number
  period: string
}): Promise<Stake> => {
  const resp = await axios.post(`${STAKING_BASE}/api/staking/stake`, data)
  return resp.data
}

export const stakingGetUserStakes = async (userId: number, status?: string, limit = 20): Promise<Stake[]> => {
  const resp = await axios.get(`${STAKING_BASE}/api/staking/stakes`, { params: { user_id: userId, status, limit } })
  return resp.data
}

export const stakingGetStake = async (stakeId: string): Promise<Stake> => {
  const resp = await axios.get(`${STAKING_BASE}/api/staking/stakes/${stakeId}`)
  return resp.data
}

export const stakingUnstake = async (stakeId: string, forceEarly = false): Promise<UnstakeResult> => {
  const resp = await axios.post(`${STAKING_BASE}/api/staking/stakes/${stakeId}/unstake`, { force_early: forceEarly })
  return resp.data
}

export const stakingGetStats = async (userId: number): Promise<StakingStats> => {
  const resp = await axios.get(`${STAKING_BASE}/api/staking/stats/${userId}`)
  return resp.data
}

export const stakingGetLeaderboard = async (limit = 10) => {
  const resp = await axios.get(`${STAKING_BASE}/api/staking/leaderboard`, { params: { limit } })
  return resp.data
}

// === TRADING/CRASH SERVICE ===

const TRADING_BASE = import.meta.env.VITE_TRADING_URL || 'http://localhost:8011'

export interface TradingGame {
  id: string
  game_number: number
  status: string
  current_multiplier: string
  server_seed_hash: string
  server_seed?: string
  crash_point?: string
  total_bets: number
  total_volume_ton: string
}

export interface TradingBet {
  id: string
  game_number: number
  bet_amount_ton: string
  cash_out_multiplier?: string
  profit_ton: string
  status: string
}

export interface TradingStats {
  user_id: number
  total_games: number
  total_wins: number
  total_losses: number
  total_wagered_ton: string
  total_won_ton: string
  total_profit_ton: string
  biggest_win_ton: string
  highest_multiplier: string
  win_rate: string
}

export const tradingGetCurrentGame = async (): Promise<TradingGame> => {
  const resp = await axios.get(`${TRADING_BASE}/api/trading/game/current`)
  return resp.data
}

export const tradingPlaceBet = async (data: {
  game_number: number
  user_id: number
  user_telegram_id: number
  user_name: string
  bet_amount_ton: number
}): Promise<TradingBet> => {
  const resp = await axios.post(`${TRADING_BASE}/api/trading/bet`, data)
  return resp.data
}

export const tradingCashOut = async (betId: string, userId: number): Promise<TradingBet> => {
  const resp = await axios.post(`${TRADING_BASE}/api/trading/cashout`, { bet_id: betId }, { params: { user_id: userId } })
  return resp.data
}

export const tradingGetHistory = async (limit = 20): Promise<TradingGame[]> => {
  const resp = await axios.get(`${TRADING_BASE}/api/trading/history`, { params: { limit } })
  return resp.data
}

export const tradingGetStats = async (userId: number): Promise<TradingStats> => {
  const resp = await axios.get(`${TRADING_BASE}/api/trading/stats/${userId}`)
  return resp.data
}

export const tradingVerify = async (gameId: string, serverSeed: string) => {
  const resp = await axios.post(`${TRADING_BASE}/api/trading/verify/${gameId}`, null, { params: { server_seed: serverSeed } })
  return resp.data
}

// Trading WebSocket URL
export const TRADING_WS_URL = import.meta.env.VITE_TRADING_WS_URL || 'ws://localhost:8011/api/trading/ws'

// === ROULETTE SERVICE ===

const ROULETTE_BASE = import.meta.env.VITE_ROULETTE_URL || 'http://localhost:8012'

export interface RouletteGame {
  id: string
  game_number: number
  status: string
  winning_number?: number
  winning_color?: string
  server_seed_hash: string
  server_seed?: string
  total_bets: number
  total_volume_ton: string
  created_at: string
}

export interface RouletteBet {
  id: string
  game_id: string
  bet_type: string
  bet_value: string
  bet_amount_ton: string
  payout_multiplier: string
  profit_ton: string
  status: string
}

export const rouletteGetCurrentGame = async (): Promise<RouletteGame> => {
  const resp = await axios.get(`${ROULETTE_BASE}/api/roulette/game/current`)
  return resp.data
}

export const roulettePlaceBet = async (data: {
  game_id: string
  user_id: number
  user_telegram_id: number
  user_name: string
  bet_type: string
  bet_value: string
  bet_amount_ton: number
}): Promise<RouletteBet> => {
  const resp = await axios.post(`${ROULETTE_BASE}/api/roulette/bet`, data)
  return resp.data
}

export const rouletteGetHistory = async (limit = 20): Promise<RouletteGame[]> => {
  const resp = await axios.get(`${ROULETTE_BASE}/api/roulette/history`, { params: { limit } })
  return resp.data
}

export const rouletteVerify = async (gameId: string, serverSeed: string) => {
  const resp = await axios.post(`${ROULETTE_BASE}/api/roulette/verify/${gameId}`, null, { params: { server_seed: serverSeed } })
  return resp.data
}

// === STARS SERVICE ===

const STARS_BASE = import.meta.env.VITE_STARS_URL || 'http://localhost:8013'

export interface StarsPackage {
  id: string
  name: string
  stars_amount: number
  price_ton: string
  bonus_percent: number
  is_popular: boolean
}

export interface StarsOrder {
  id: string
  user_id: number
  package_id: string
  stars_amount: number
  price_ton: string
  status: string
  payment_memo: string
  created_at: string
}

export const starsGetPackages = async (): Promise<StarsPackage[]> => {
  const resp = await axios.get(`${STARS_BASE}/api/stars/packages`)
  return resp.data
}

export const starsCreateOrder = async (data: {
  user_id: number
  user_telegram_id: number
  package_id: string
}): Promise<StarsOrder> => {
  const resp = await axios.post(`${STARS_BASE}/api/stars/orders`, data)
  return resp.data
}

export const starsGetOrder = async (orderId: string): Promise<StarsOrder> => {
  const resp = await axios.get(`${STARS_BASE}/api/stars/orders/${orderId}`)
  return resp.data
}

export const starsVerifyPayment = async (orderId: string): Promise<{ verified: boolean; order: StarsOrder }> => {
  const resp = await axios.post(`${STARS_BASE}/api/stars/orders/${orderId}/verify`)
  return resp.data
}

export const starsGetBalance = async (userId: number): Promise<{ user_id: number; balance: number }> => {
  const resp = await axios.get(`${STARS_BASE}/api/stars/balance/${userId}`)
  return resp.data
}

// === PLINKO SERVICE ===

const PLINKO_BASE = import.meta.env.VITE_PLINKO_URL || 'http://localhost:8014'

export interface PlinkoConfig {
  rows: number
  slots: number[]
  multipliers: number[]
  min_bet_ton: string
  max_bet_ton: string
}

export interface PlinkoDrop {
  id: string
  user_id: number
  bet_amount_ton: string
  landing_slot: number
  multiplier: string
  payout_ton: string
  profit_ton: string
  path: number[]
  server_seed: string
  server_seed_hash: string
  nonce: number
}

export const plinkoGetConfig = async (): Promise<PlinkoConfig> => {
  const resp = await axios.get(`${PLINKO_BASE}/api/plinko/config`)
  return resp.data
}

export const plinkoPlay = async (data: {
  user_id: number
  user_telegram_id: number
  user_name: string
  bet_amount_ton: number
  client_seed: string
}): Promise<PlinkoDrop> => {
  const resp = await axios.post(`${PLINKO_BASE}/api/plinko/play`, data)
  return resp.data
}

export const plinkoGetHistory = async (userId: number, limit = 20): Promise<PlinkoDrop[]> => {
  const resp = await axios.get(`${PLINKO_BASE}/api/plinko/history`, { params: { user_id: userId, limit } })
  return resp.data
}

export const plinkoVerify = async (dropId: string, serverSeed: string, clientSeed: string, nonce: number) => {
  const resp = await axios.post(`${PLINKO_BASE}/api/plinko/verify/${dropId}`, null, {
    params: { server_seed: serverSeed, client_seed: clientSeed, nonce },
  })
  return resp.data
}
