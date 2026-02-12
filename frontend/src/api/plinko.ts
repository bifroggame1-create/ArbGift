import axios from 'axios'

const PLINKO_BASE = import.meta.env.VITE_PLINKO_URL || ''

const plinkoApi = axios.create({
  baseURL: PLINKO_BASE,
  timeout: 10000,
})

// Types
export interface DropResult {
  id: string
  path: number[][]
  landing_slot: number
  multiplier: number
  bet_amount: number
  payout: number
  profit: number
  server_seed_hash: string
  server_seed: string
  client_seed: string
  nonce: number
  risk_level: string
  row_count: number
  created_at: string
}

export interface PlayResponse {
  drops: DropResult[]
  new_balance_stars: number
  total_payout: number
  total_profit: number
}

export interface PlinkoConfig {
  multiplier_sets: Record<string, Record<string, number[]>>
  min_bet_stars: number
  max_bet_stars: number
  max_balls_per_play: number
  valid_risk_levels: string[]
  valid_row_counts: number[]
}

export interface HistoryItem {
  id: string
  landing_slot: number
  multiplier: number
  bet_amount: number
  payout: number
  profit: number
  risk_level: string
  row_count: number
  created_at: string
}

export interface VerifyResponse {
  valid: boolean
  landing_slot: number
  multiplier: number
  path: number[][]
}

// API functions

export async function plinkoGetConfig(): Promise<PlinkoConfig> {
  const { data } = await plinkoApi.get('/api/v1/config')
  return data
}

export async function plinkoPlay(params: {
  userId: string
  betAmountStars: number
  riskLevel: string
  rowCount: number
  ballCount: number
  clientSeed?: string
}): Promise<PlayResponse> {
  const { data } = await plinkoApi.post('/api/v1/play', {
    bet_amount_stars: params.betAmountStars,
    risk_level: params.riskLevel,
    row_count: params.rowCount,
    ball_count: params.ballCount,
    client_seed: params.clientSeed,
  }, {
    params: { user_id: params.userId },
  })
  return data
}

export async function plinkoVerify(params: {
  serverSeed: string
  clientSeed: string
  nonce: number
  betAmount: number
  riskLevel: string
  rowCount: number
}): Promise<VerifyResponse> {
  const { data } = await plinkoApi.post('/api/v1/verify', {
    server_seed: params.serverSeed,
    client_seed: params.clientSeed,
    nonce: params.nonce,
    bet_amount: params.betAmount,
    risk_level: params.riskLevel,
    row_count: params.rowCount,
  })
  return data
}

export async function plinkoGetHistory(userId: string, limit = 50): Promise<HistoryItem[]> {
  const { data } = await plinkoApi.get('/api/v1/history', {
    params: { user_id: userId, limit },
  })
  return data
}

export async function plinkoGetStats(userId: string) {
  const { data } = await plinkoApi.get('/api/v1/stats', {
    params: { user_id: userId },
  })
  return data
}
