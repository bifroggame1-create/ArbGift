<template>
  <div class="trading-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 20" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="trading-header">
      <button class="header-back" @click="$router.push('/solo')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="header-title">
        <span class="title-main">Trading</span>
        <span class="title-badge">CRASH</span>
      </div>
      <div class="header-balance">
        <span class="balance-icon">💎</span>
        <span class="balance-value">{{ balance.toFixed(2) }}</span>
        <button class="balance-add">+</button>
      </div>
    </header>

    <!-- Connection Status -->
    <div class="connection-bar">
      <div class="connection-status connected">
        <span class="status-dot"></span>
        <span>Connected</span>
      </div>
      <div class="game-info">
        <span>ИГРА #{{ gameNumber }}</span>
        <span class="hash-text">{{ currentHash }}</span>
      </div>
    </div>

    <!-- Chart Container with Candlesticks -->
    <div class="chart-container">
      <!-- SVG Candlestick Chart -->
      <svg class="candlestick-chart" :viewBox="`0 0 ${chartWidth} ${chartHeight}`" preserveAspectRatio="none">
        <!-- Grid lines -->
        <line v-for="i in 5" :key="'h'+i"
          x1="0" :y1="chartHeight * i / 5"
          :x2="chartWidth" :y2="chartHeight * i / 5"
          stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
        <line v-for="i in 8" :key="'v'+i"
          :x1="chartWidth * i / 8" y1="0"
          :x2="chartWidth * i / 8" :y2="chartHeight"
          stroke="rgba(255,255,255,0.03)" stroke-width="1"/>

        <!-- Candlesticks -->
        <g v-for="(candle, i) in visibleCandles" :key="i">
          <!-- Wick (high-low line) -->
          <line
            :x1="getCandleX(i) + candleWidth / 2"
            :y1="priceToY(candle.high)"
            :x2="getCandleX(i) + candleWidth / 2"
            :y2="priceToY(candle.low)"
            :stroke="candle.close >= candle.open ? '#22c55e' : '#ef4444'"
            stroke-width="1"
          />
          <!-- Body -->
          <rect
            :x="getCandleX(i)"
            :y="priceToY(Math.max(candle.open, candle.close))"
            :width="candleWidth - 2"
            :height="Math.max(2, Math.abs(priceToY(candle.open) - priceToY(candle.close)))"
            :fill="candle.close >= candle.open ? '#22c55e' : '#ef4444'"
            rx="1"
          />
        </g>

        <!-- Current price line -->
        <line
          v-if="gameStatus === 'active'"
          x1="0" :y1="priceToY(currentMultiplier)"
          :x2="chartWidth" :y2="priceToY(currentMultiplier)"
          stroke="#3b82f6" stroke-width="1" stroke-dasharray="4,4"
          opacity="0.7"
        />

        <!-- Price curve overlay -->
        <path
          v-if="pricePath"
          :d="pricePath"
          fill="none"
          :stroke="gameStatus === 'crashed' ? '#ef4444' : '#22c55e'"
          stroke-width="2"
          stroke-linecap="round"
        />

        <!-- Glow effect for curve -->
        <path
          v-if="pricePath && gameStatus === 'active'"
          :d="pricePath"
          fill="none"
          stroke="#22c55e"
          stroke-width="6"
          stroke-linecap="round"
          opacity="0.3"
          filter="blur(4px)"
        />
      </svg>

      <!-- Multiplier Display -->
      <div class="multiplier-overlay" :class="{ crashed: gameStatus === 'crashed' }">
        <div v-if="gameStatus === 'active'" class="multiplier-active">
          <span class="multiplier-value" :class="{ high: currentMultiplier >= 2 }">
            {{ currentMultiplier.toFixed(2) }}x
          </span>
          <span class="multiplier-label">МНОЖИТЕЛЬ</span>
        </div>
        <div v-else-if="gameStatus === 'crashed'" class="multiplier-crashed">
          <span class="crash-value">{{ crashPoint.toFixed(2) }}x</span>
          <span class="crash-label">CRASHED!</span>
          <span class="next-game">Следующая игра через {{ nextGameTimer }}с</span>
        </div>
        <div v-else class="multiplier-waiting">
          <span class="waiting-text">Ожидание игроков...</span>
          <span class="waiting-sub">Сделайте ставку</span>
        </div>
      </div>

      <!-- Y-axis labels -->
      <div class="y-axis">
        <span v-for="i in 5" :key="i" class="y-label">{{ (maxPrice - (maxPrice - minPrice) * (i - 1) / 4).toFixed(2) }}x</span>
      </div>
    </div>

    <!-- Recent Crashes Strip -->
    <div class="crashes-strip">
      <div
        v-for="(crash, i) in recentCrashes"
        :key="i"
        :class="['crash-badge', crash >= 2 ? 'high' : 'low']"
      >
        {{ crash.toFixed(2) }}x
      </div>
    </div>

    <!-- Traders Panel -->
    <div class="traders-panel">
      <div class="traders-header">
        <span class="traders-title">Игроки</span>
        <span class="traders-count">{{ traders.length }}</span>
      </div>
      <div class="traders-list">
        <div v-for="trader in traders" :key="trader.id" class="trader-item">
          <div class="trader-avatar" :style="{ background: trader.color }">
            {{ trader.name.charAt(0).toUpperCase() }}
          </div>
          <div class="trader-info">
            <span class="trader-name">@{{ trader.name }}</span>
            <span class="trader-bet">{{ trader.bet }} TON</span>
          </div>
          <div class="trader-status" :class="trader.status">
            <span v-if="trader.status === 'won'" class="status-won">+{{ trader.profit?.toFixed(2) }}</span>
            <span v-else-if="trader.status === 'playing'">{{ trader.multiplier?.toFixed(2) }}x</span>
            <span v-else class="status-waiting">⏳</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bet Controls -->
    <div class="bet-controls">
      <!-- Bet Amount Selection -->
      <div class="bet-amounts">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          :class="['bet-amount', { active: selectedBetAmount === amount }]"
          @click="selectedBetAmount = amount"
        >
          <span class="amount-value">{{ amount }}</span>
          <span class="amount-icon">💎</span>
        </button>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button
          class="btn-buy"
          :disabled="gameStatus !== 'pending' || isPlacingBet"
          @click="placeBet"
        >
          <span class="btn-icon">📈</span>
          <span class="btn-text">
            {{ isPlacingBet ? 'Покупаем...' : `Купить ${selectedBetAmount} TON` }}
          </span>
        </button>
        <button
          class="btn-sell"
          :disabled="!activeBet || gameStatus !== 'active' || isCashingOut"
          @click="cashOut"
        >
          <span class="btn-icon">📉</span>
          <span class="btn-text">
            {{ isCashingOut ? 'Продаём...' : activeBet ? `Продать +${((activeBet.amount * currentMultiplier) - activeBet.amount).toFixed(2)}` : 'Продать' }}
          </span>
        </button>
      </div>

      <!-- Auto Cashout -->
      <div class="auto-cashout">
        <span class="auto-label">Авто-продажа:</span>
        <div class="auto-options">
          <button
            v-for="mult in autoMultipliers"
            :key="mult"
            :class="['auto-btn', { active: autoMultiplier === mult }]"
            @click="autoMultiplier = autoMultiplier === mult ? null : mult"
          >
            {{ mult }}x
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/pvp" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4l4 4m8 8l4 4M4 20l4-4m8-8l4-4M12 12l-8 8m16 0l-8-8m0 0l8-8M4 4l8 8"/>
        </svg>
        <span>ПвП</span>
      </router-link>
      <router-link to="/solo" class="nav-item active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        <span>Соло</span>
      </router-link>
      <router-link to="/inventory" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M3 9h18M9 21V9"/>
        </svg>
        <span>Инвентарь</span>
      </router-link>
      <router-link to="/shop" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>Магазин</span>
      </router-link>
      <router-link to="/profile" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>Профиль</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Candle {
  open: number
  high: number
  low: number
  close: number
  time: number
}

interface Trader {
  id: number
  name: string
  bet: number
  color: string
  status: 'waiting' | 'playing' | 'won' | 'lost'
  multiplier?: number
  profit?: number
}

// Chart dimensions
const chartWidth = 340
const chartHeight = 180

// State
const balance = ref(4.16)
const currentMultiplier = ref(1.00)
const gameStatus = ref<'pending' | 'active' | 'crashed'>('pending')
const crashPoint = ref(0)
const nextGameTimer = ref(5)
const gameNumber = ref(28392)
const currentHash = ref('3d07...f8da')

// Candlestick data
const candles = ref<Candle[]>([])
const priceHistory = ref<number[]>([])
const candleWidth = 16
const maxVisibleCandles = Math.floor(chartWidth / candleWidth) - 2

// Generate initial candles
const generateInitialCandles = () => {
  const result: Candle[] = []
  let price = 1.0
  for (let i = 0; i < 15; i++) {
    const open = price
    const change = (Math.random() - 0.45) * 0.3
    const close = Math.max(0.5, price + change)
    const high = Math.max(open, close) + Math.random() * 0.1
    const low = Math.min(open, close) - Math.random() * 0.1
    result.push({ open, high, low, close, time: Date.now() - (15 - i) * 5000 })
    price = close
  }
  return result
}

// Initialize candles
candles.value = generateInitialCandles()

const visibleCandles = computed(() => {
  return candles.value.slice(-maxVisibleCandles)
})

// Price range for Y-axis
const minPrice = computed(() => {
  const prices = visibleCandles.value.flatMap(c => [c.low, c.high])
  if (priceHistory.value.length > 0) {
    prices.push(...priceHistory.value)
  }
  return Math.max(0.5, Math.min(...prices) - 0.2)
})

const maxPrice = computed(() => {
  const prices = visibleCandles.value.flatMap(c => [c.low, c.high])
  if (priceHistory.value.length > 0) {
    prices.push(...priceHistory.value)
  }
  return Math.max(...prices) + 0.5
})

const priceToY = (price: number) => {
  const range = maxPrice.value - minPrice.value
  return chartHeight - ((price - minPrice.value) / range) * chartHeight
}

const getCandleX = (index: number) => {
  return (index + 1) * candleWidth
}

// Price curve path
const pricePath = computed(() => {
  if (priceHistory.value.length < 2) return ''

  const startX = (visibleCandles.value.length + 1) * candleWidth
  const points = priceHistory.value.map((price, i) => {
    const x = startX + i * 3
    const y = priceToY(price)
    return `${x},${y}`
  })

  return `M ${points.join(' L ')}`
})

// Recent crashes for display
const recentCrashes = ref([2.34, 1.12, 5.67, 1.89, 3.21, 1.05, 8.92, 2.11])

// Traders
const traders = ref<Trader[]>([
  { id: 1, name: 'trader1', bet: 2.5, color: '#22c55e', status: 'playing', multiplier: 1.45 },
  { id: 2, name: 'winner99', bet: 1.0, color: '#3b82f6', status: 'won', profit: 1.8 },
  { id: 3, name: 'lucky_star', bet: 5.0, color: '#ec4899', status: 'waiting' },
])

// Bet state
const betAmounts = [0.5, 1, 2, 5]
const selectedBetAmount = ref(1)
const autoMultipliers = [1.5, 2, 3, 5, 10]
const autoMultiplier = ref<number | null>(null)
const activeBet = ref<{ amount: number } | null>(null)
const isPlacingBet = ref(false)
const isCashingOut = ref(false)

// Stars background
const getStarStyle = (_i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

// Game simulation
let gameInterval: number | null = null

const simulateGame = () => {
  gameStatus.value = 'active'
  currentMultiplier.value = 1.00
  priceHistory.value = [1.00]

  // Decide crash point (house edge)
  const rand = Math.random()
  const targetCrash = rand < 0.3 ? 1 + Math.random() * 0.5 : // 30% quick crash
                      rand < 0.7 ? 1.5 + Math.random() * 2 : // 40% medium
                      3 + Math.random() * 7 // 30% high

  gameInterval = window.setInterval(() => {
    if (gameStatus.value !== 'active') return

    // Increase multiplier with some variance
    const increase = 0.01 + Math.random() * 0.03
    currentMultiplier.value += increase
    priceHistory.value.push(currentMultiplier.value)

    // Update playing traders
    traders.value.forEach(t => {
      if (t.status === 'playing') {
        t.multiplier = currentMultiplier.value
      }
    })

    // Check crash
    if (currentMultiplier.value >= targetCrash) {
      crashGame()
    }

    // Auto cashout
    if (autoMultiplier.value && activeBet.value && currentMultiplier.value >= autoMultiplier.value) {
      cashOut()
    }
  }, 80)
}

const crashGame = () => {
  crashPoint.value = currentMultiplier.value
  gameStatus.value = 'crashed'

  // Add to recent crashes
  recentCrashes.value.unshift(crashPoint.value)
  recentCrashes.value = recentCrashes.value.slice(0, 10)

  // Add final candle
  const lastCandle = candles.value[candles.value.length - 1]
  candles.value.push({
    open: lastCandle?.close || 1,
    high: crashPoint.value,
    low: lastCandle?.close || 1,
    close: 1,
    time: Date.now()
  })

  // Reset active bet if still playing
  if (activeBet.value) {
    activeBet.value = null
  }

  if (gameInterval) clearInterval(gameInterval)

  // Countdown to next game
  nextGameTimer.value = 5
  const countdown = setInterval(() => {
    nextGameTimer.value--
    if (nextGameTimer.value <= 0) {
      clearInterval(countdown)
      gameStatus.value = 'pending'
      gameNumber.value++
      priceHistory.value = []
      currentHash.value = Math.random().toString(36).substring(2, 10)
      setTimeout(simulateGame, 2000)
    }
  }, 1000)
}

const placeBet = async () => {
  if (gameStatus.value !== 'pending') return

  isPlacingBet.value = true
  await new Promise(r => setTimeout(r, 300))

  activeBet.value = { amount: selectedBetAmount.value }
  balance.value -= selectedBetAmount.value

  // Add to traders list
  traders.value.unshift({
    id: Date.now(),
    name: 'you',
    bet: selectedBetAmount.value,
    color: '#facc15',
    status: 'waiting'
  })

  isPlacingBet.value = false
}

const cashOut = async () => {
  if (!activeBet.value || gameStatus.value !== 'active') return

  isCashingOut.value = true
  await new Promise(r => setTimeout(r, 200))

  const payout = activeBet.value.amount * currentMultiplier.value
  balance.value += payout

  // Update trader status
  const myTrader = traders.value.find(t => t.name === 'you')
  if (myTrader) {
    myTrader.status = 'won'
    myTrader.profit = payout - activeBet.value.amount
  }

  activeBet.value = null
  isCashingOut.value = false
}

onMounted(() => {
  setTimeout(simulateGame, 2000)
})

onUnmounted(() => {
  if (gameInterval) clearInterval(gameInterval)
})
</script>

<style scoped>
.trading-view {
  min-height: 100vh;
  background: #000;
  color: #fff;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 90px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
}

/* Stars */
.stars-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  background: #fff;
  border-radius: 50%;
  opacity: 0.3;
  animation: twinkle 3s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.3); }
}

/* Header */
.trading-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  position: relative;
  z-index: 10;
}

.header-back {
  width: 40px;
  height: 40px;
  background: #1c1c1e;
  border: none;
  border-radius: 12px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-main {
  font-size: 18px;
  font-weight: 700;
}

.title-badge {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}

.header-balance {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1c1c1e;
  padding: 8px 12px;
  border-radius: 12px;
}

.balance-icon { font-size: 14px; }
.balance-value { font-size: 14px; font-weight: 600; }

.balance-add {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 14px;
  margin-left: 4px;
}

/* Connection Bar */
.connection-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 12px;
  position: relative;
  z-index: 10;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4ade80;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4ade80;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.game-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11px;
  color: #6b7280;
}

.hash-text {
  font-family: monospace;
}

/* Chart Container */
.chart-container {
  margin: 0 16px 12px;
  background: linear-gradient(180deg, #0a1628 0%, #0f172a 100%);
  border-radius: 20px;
  height: 200px;
  position: relative;
  z-index: 10;
  overflow: hidden;
  border: 1px solid #1e3a5f;
}

.candlestick-chart {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.y-axis {
  position: absolute;
  right: 8px;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 0;
  pointer-events: none;
}

.y-label {
  font-size: 9px;
  color: #4b5563;
  font-family: monospace;
}

/* Multiplier Overlay */
.multiplier-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 5;
  pointer-events: none;
}

.multiplier-overlay.crashed {
  background: rgba(0, 0, 0, 0.8);
  padding: 20px 40px;
  border-radius: 16px;
  backdrop-filter: blur(4px);
}

.multiplier-active {
  text-align: center;
}

.multiplier-value {
  display: block;
  font-size: 48px;
  font-weight: 800;
  color: #3b82f6;
  text-shadow: 0 0 40px rgba(59, 130, 246, 0.5);
  transition: color 0.3s;
}

.multiplier-value.high {
  color: #22c55e;
  text-shadow: 0 0 40px rgba(34, 197, 94, 0.5);
}

.multiplier-label {
  display: block;
  font-size: 10px;
  color: #6b7280;
  letter-spacing: 2px;
  margin-top: 4px;
}

.multiplier-crashed {
  text-align: center;
}

.crash-value {
  display: block;
  font-size: 42px;
  font-weight: 800;
  color: #ef4444;
  text-shadow: 0 0 40px rgba(239, 68, 68, 0.5);
}

.crash-label {
  display: block;
  font-size: 14px;
  color: #ef4444;
  font-weight: 700;
  margin-top: 4px;
}

.next-game {
  display: block;
  font-size: 11px;
  color: #6b7280;
  margin-top: 8px;
}

.multiplier-waiting {
  text-align: center;
}

.waiting-text {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.waiting-sub {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* Crashes Strip */
.crashes-strip {
  display: flex;
  gap: 6px;
  padding: 0 16px;
  margin-bottom: 12px;
  overflow-x: auto;
  position: relative;
  z-index: 10;
}

.crash-badge {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.crash-badge.high {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.crash-badge.low {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

/* Traders Panel */
.traders-panel {
  margin: 0 16px 12px;
  background: #1c1c1e;
  border-radius: 16px;
  padding: 12px;
  position: relative;
  z-index: 10;
}

.traders-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.traders-title {
  font-size: 14px;
  font-weight: 600;
}

.traders-count {
  background: #27272a;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 12px;
  color: #6b7280;
}

.traders-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 100px;
  overflow-y: auto;
}

.trader-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: #27272a;
  border-radius: 10px;
}

.trader-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.trader-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.trader-name {
  font-size: 11px;
  font-weight: 500;
}

.trader-bet {
  font-size: 10px;
  color: #6b7280;
}

.trader-status {
  font-size: 11px;
  font-weight: 600;
}

.status-won { color: #4ade80; }
.status-waiting { opacity: 0.5; }

/* Bet Controls */
.bet-controls {
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.bet-amounts {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.bet-amount {
  flex: 1;
  background: #1c1c1e;
  border: 2px solid transparent;
  border-radius: 12px;
  padding: 10px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.2s;
}

.bet-amount.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.15);
}

.amount-value {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.amount-icon {
  font-size: 11px;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.btn-buy, .btn-sell {
  flex: 1;
  border: none;
  border-radius: 14px;
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-buy {
  background: linear-gradient(135deg, #16a34a, #22c55e);
  color: #fff;
}

.btn-buy:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-sell {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: #fff;
}

.btn-sell:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 14px;
}

/* Auto Cashout */
.auto-cashout {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #1c1c1e;
  border-radius: 12px;
}

.auto-label {
  font-size: 11px;
  color: #6b7280;
  white-space: nowrap;
}

.auto-options {
  display: flex;
  gap: 6px;
  flex: 1;
  overflow-x: auto;
}

.auto-btn {
  padding: 6px 10px;
  background: #27272a;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.auto-btn.active {
  border-color: #facc15;
  background: rgba(250, 204, 21, 0.15);
  color: #facc15;
}

/* Bottom Nav */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #000;
  border-top: 1px solid #1c1c1e;
  display: flex;
  padding: 8px 0 24px;
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  text-decoration: none;
  font-size: 10px;
}

.nav-item.active { color: #fff; }
.nav-item svg { width: 22px; height: 22px; }
</style>
