<template>
  <div class="trading-view">
    <!-- Game Plate Background -->
    <div class="game-plate trading-plate">
      <div class="plate-title">Gift Trading</div>
    </div>

    <!-- Tournament Banner -->
    <div class="tournament-banner" @click="$router.push('/tournament')">
      <span class="banner-emoji">&#127942;</span>
      <span class="banner-text">Трейдинг Мега Турнир</span>
      <span class="banner-timer">{{ tournamentTimer }}</span>
    </div>

    <!-- Top Bar -->
    <div class="top-bar">
      <div class="top-left">
        <button class="icon-btn" @click="$router.push('/history?sorting=solo_trading')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </button>
        <button class="icon-btn" @click="showHelp = true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </button>
      </div>
      <div class="balance-pill" @click="$router.push('/deposit')">
        <svg class="ton-icon" width="16" height="16" viewBox="0 0 56 56" fill="none">
          <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z" fill="#0098EA"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
        </svg>
        <span class="balance-value">{{ balance.toFixed(2) }}</span>
        <span class="balance-add">+</span>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="chart-wrapper">
      <div class="chart-container" ref="chartContainerRef">
        <!-- Ping Indicator -->
        <div class="ping-indicator">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path opacity="0.5" d="M5 1.17C6.76 1.17 8.45 1.86 9.75 3.11C9.91 3.26 9.92 3.51 9.77 3.67C9.61 3.83 9.36 3.84 9.2 3.69C8.04 2.58 6.54 1.97 5 1.97C3.46 1.97 1.96 2.58 0.8 3.69C0.64 3.84 0.39 3.83 0.23 3.67C0.08 3.51 0.09 3.26 0.25 3.11C1.55 1.86 3.24 1.17 5 1.17Z" fill="white"/>
            <path opacity="0.5" d="M5.02 3.46C6.21 3.46 7.36 3.91 8.26 4.73C8.43 4.87 8.44 5.13 8.29 5.29C8.15 5.45 7.89 5.47 7.73 5.32C6.96 4.63 6 4.26 5.02 4.26C4.03 4.26 3.07 4.63 2.31 5.32C2.14 5.47 1.89 5.45 1.74 5.29C1.59 5.13 1.61 4.87 1.77 4.73C2.68 3.91 3.83 3.46 5.02 3.46Z" fill="white"/>
            <path opacity="0.5" d="M5 5.74C5.62 5.74 6.22 5.95 6.72 6.33C6.89 6.47 6.92 6.72 6.79 6.9C6.66 7.07 6.4 7.1 6.23 6.97C5.87 6.69 5.44 6.54 5 6.54C4.57 6.54 4.14 6.69 3.78 6.97C3.6 7.1 3.35 7.07 3.21 6.9C3.08 6.72 3.11 6.47 3.29 6.33C3.78 5.95 4.38 5.74 5 5.74Z" fill="white"/>
            <circle opacity="0.5" cx="5" cy="8.43" r="0.4" fill="white"/>
          </svg>
          <span>{{ ping }}ms</span>
        </div>

        <!-- Multiplier Display -->
        <div class="multiplier-display" :class="multiplierClass" :style="multiplierStyle">
          <span class="multiplier-value">{{ displayMultiplier }}</span>
        </div>

        <!-- Price Line (animated dashed) -->
        <div v-if="gameState === 'active'" class="price-line" :style="{ top: priceLineTop + 'px' }"></div>

        <!-- Crash Overlay -->
        <div v-if="gameState === 'crashed'" class="crash-overlay">
          <div class="crash-skulls">
            <span>&#128128;</span>
            <span>&#128128;</span>
            <span>&#128128;</span>
          </div>
        </div>

        <!-- Countdown Overlay -->
        <div v-if="gameState === 'countdown'" class="countdown-overlay">
          <span class="countdown-value">{{ countdownSeconds.toFixed(1) }}s</span>
        </div>
      </div>
    </div>

    <!-- Recent Games Strip - MyBalls style -->
    <div class="recent-games">
      <span class="recent-label">Последние игры</span>
      <div class="recent-list">
        <div v-for="(game, idx) in recentGames" :key="idx" class="recent-item">
          <div class="mini-chart" :class="getMiniChartClass(game.maxMult)">
            <svg viewBox="0 0 50 60" preserveAspectRatio="none">
              <path :d="game.path" fill="none" :stroke="game.maxMult >= 2 ? '#09D76D' : game.maxMult >= 1.3 ? '#85FFB2' : '#FB2C36'" stroke-width="2"/>
            </svg>
          </div>
          <span class="recent-mult" :class="{ high: game.maxMult >= 1.3, low: game.maxMult < 1.3 }">{{ game.maxMult.toFixed(2) }}x</span>
        </div>
      </div>
    </div>

    <!-- Traders Panel - MyBalls style -->
    <div class="traders-panel">
      <!-- Gradient border effect -->
      <div class="panel-border"></div>

      <div class="traders-header">
        <div class="traders-title">
          <span class="title-text">Трейдеры</span>
          <span class="traders-count">({{ traders.length }})</span>
        </div>
      </div>

      <div class="traders-list" v-if="traders.length > 0">
        <div v-for="trader in traders" :key="trader.id"
             class="trader-card"
             :class="{ exited: trader.exited, playing: !trader.exited && gameState === 'active' }">
          <div class="trader-left">
            <!-- Level badge -->
            <div class="level-badge">
              <span class="level-num">{{ trader.level || Math.floor(Math.random() * 50) + 1 }}</span>
            </div>
            <!-- Avatar -->
            <div class="trader-avatar" :style="{ background: trader.color }">
              <span class="avatar-letter">{{ trader.name.charAt(0).toUpperCase() }}</span>
            </div>
            <!-- Name + Status -->
            <div class="trader-name-block">
              <span class="trader-name">@{{ trader.name }}</span>
              <span v-if="trader.exited" class="status-badge exited">Вышел</span>
              <span v-else-if="gameState === 'active'" class="status-badge playing">В игре</span>
            </div>
          </div>

          <div class="trader-right">
            <!-- Profit/Loss display -->
            <div class="profit-display" :class="{ positive: trader.profit >= 0, negative: trader.profit < 0 }">
              <span class="profit-value">{{ trader.profit >= 0 ? '+' : '' }}{{ trader.profit.toFixed(2) }}</span>
              <svg class="ton-mini" width="10" height="10" viewBox="0 0 16 16" fill="currentColor">
                <path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z"/>
              </svg>
            </div>
            <!-- Bet amount -->
            <div class="bet-display">
              <span class="bet-value">{{ trader.bet.toFixed(0) }}</span>
              <svg class="ton-mini" width="10" height="10" viewBox="0 0 16 16" fill="currentColor">
                <path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Game info footer -->
      <div class="panel-footer">
        <span class="game-number">Игра #{{ gameNumber }}</span>
        <button class="hash-btn">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
            <path d="M4.75016 9.48047H3.16683C1.33766 9.48047 0.520996 8.6638 0.520996 6.83464V5.2513C0.520996 3.42214 1.33766 2.60547 3.16683 2.60547H4.41683C4.58766 2.60547 4.72933 2.74714 4.72933 2.91797C4.72933 3.0888 4.58766 3.23047 4.41683 3.23047H3.16683C1.67516 3.23047 1.146 3.75964 1.146 5.2513V6.83464C1.146 8.3263 1.67516 8.85547 3.16683 8.85547H4.75016C6.24183 8.85547 6.771 8.3263 6.771 6.83464V5.58464C6.771 5.4138 6.91266 5.27214 7.0835 5.27214C7.25433 5.27214 7.396 5.4138 7.396 5.58464V6.83464C7.396 8.6638 6.57933 9.48047 4.75016 9.48047Z"/>
          </svg>
          <span>Hash: {{ gameHash }}</span>
        </button>
      </div>
    </div>

    <!-- Bet Controls -->
    <div class="bet-controls">
      <!-- Bet Amount Pills -->
      <div class="bet-amounts">
        <button v-for="amount in betAmounts" :key="amount"
          class="bet-pill" :class="{ active: selectedBet === amount }"
          @click="selectedBet = amount">
          <svg class="pill-diamond" width="12" height="12" viewBox="0 0 56 56" fill="currentColor">
            <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z" fill="currentColor" opacity="0.3"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="currentColor"/>
          </svg>
          {{ amount }}
        </button>
        <button class="bet-pill max-pill" @click="selectedBet = Math.floor(balance * 10) / 10">Макс</button>
        <button class="bet-pill edit-pill">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
      </div>

      <!-- Action Buttons Row -->
      <div class="action-row">
        <button class="swap-btn" @click="$router.push('/swap')">
          <svg class="swap-icon" width="20" height="20" viewBox="0 0 56 56" fill="#0098EA">
            <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
          </svg>
          <span>Сменить</span>
          <img src="/icons/stars.png" alt="Stars" class="swap-star-icon" width="14" height="14" />
        </button>

        <!-- Buy / Sell Button -->
        <button v-if="!playerBet" class="buy-btn" :disabled="!canBuy" @click="placeBet">
          <svg class="btn-diamond" width="18" height="18" viewBox="0 0 56 56" fill="currentColor">
            <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z" opacity="0.3"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z"/>
          </svg>
          <span class="btn-text">
            <span class="btn-label">Купить</span>
            <span class="btn-amount">
              <svg class="btn-ton-icon" width="12" height="12" viewBox="0 0 56 56" fill="none">
                <circle cx="28" cy="28" r="28" fill="#0098EA"/>
                <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
              </svg>
              {{ selectedBet.toFixed(1) }} TON
            </span>
          </span>
        </button>
        <button v-else class="sell-btn" :disabled="!canSell" @click="cashOut">
          <span class="btn-text">
            <span class="btn-label">Продать</span>
            <span class="btn-percent" :class="{ positive: currentPLPercent >= 0, negative: currentPLPercent < 0 }">
              {{ currentPLPercent >= 0 ? '+' : '' }}{{ currentPLPercent.toFixed(0) }}%
            </span>
          </span>
        </button>

        <button class="deposit-btn" @click="$router.push('/deposit')">
          <span class="deposit-plus">+</span>
          <span>Отправить</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { createChart, CandlestickSeries, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts'

interface Candle {
  time: number
  open: number
  high: number
  low: number
  close: number
}

interface Trader {
  id: number
  name: string
  bet: number
  color: string
  exited: boolean
  profit: number
  level?: number
}

interface RecentGame {
  maxMult: number
  path: string
}

// Chart refs
const chartContainerRef = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
let candleSeries: ISeriesApi<'Candlestick'> | null = null

// Chart dimensions
const chartHeight = ref(220)
const priceLineTop = ref(100)

// Game state
const gameState = ref<'waiting' | 'active' | 'crashed' | 'countdown'>('waiting')
const currentMultiplier = ref(1.0)
const countdownSeconds = ref(5)
const gameNumber = ref(30772)
const gameHash = ref('2b2c...c667')
const ping = ref(73)
const tournamentTimer = ref('14:13:24:13')
const showHelp = ref(false)

// Candle data
const candles = ref<Candle[]>([])
const currentCandle = ref<Candle | null>(null)
let candleIndex = 0

// Player state
const balance = ref(3.66)
const selectedBet = ref(0.5)
const playerBet = ref<number | null>(null)
const betAmounts = [0.5, 1, 5, 10]

// Traders
const traders = ref<Trader[]>([])

// Recent games
const recentGames = ref<RecentGame[]>([
  { maxMult: 1.76, path: generateMiniPath() },
  { maxMult: 2.33, path: generateMiniPath() },
  { maxMult: 1.01, path: generateMiniPath() },
  { maxMult: 5.87, path: generateMiniPath() },
])

// Computed
const displayMultiplier = computed(() => {
  if (gameState.value === 'crashed') return '0.000x'
  return currentMultiplier.value.toFixed(3) + 'x'
})

const multiplierClass = computed(() => {
  if (gameState.value === 'crashed') return 'crashed'
  if (currentMultiplier.value < 1.0) return 'negative'
  if (currentMultiplier.value >= 2) return 'high'
  return 'normal'
})

const multiplierStyle = computed(() => {
  // Position multiplier based on price
  const containerHeight = chartHeight.value
  const minY = 0.5
  const maxY = Math.max(2.5, currentMultiplier.value + 0.5)
  const range = maxY - minY
  const normalized = (currentMultiplier.value - minY) / range
  const top = containerHeight - (normalized * containerHeight * 0.8) - 40

  return {
    top: Math.max(20, Math.min(containerHeight - 60, top)) + 'px',
    color: gameState.value === 'crashed' ? '#FB2C36' :
           currentMultiplier.value < 1.0 ? '#FB2C36' :
           currentMultiplier.value >= 2 ? '#09D76D' : '#FFFFFF'
  }
})

const currentPLPercent = computed(() => {
  return (currentMultiplier.value - 1) * 100
})

const canBuy = computed(() => {
  return (gameState.value === 'waiting' || gameState.value === 'countdown' || gameState.value === 'active') &&
         !playerBet.value && balance.value >= selectedBet.value
})

const canSell = computed(() => {
  return gameState.value === 'active' && playerBet.value !== null
})

// Generate mini chart path for recent games
function generateMiniPath(): string {
  const points: string[] = []
  let y = 50 // Start near bottom
  for (let x = 0; x <= 50; x += 5) {
    y -= (Math.random() * 8) // Go up mostly
    y = Math.max(5, Math.min(55, y))
    points.push(`${x},${y}`)
  }
  return `M ${points.join(' L ')}`
}

// Get CSS class for mini chart border color
function getMiniChartClass(mult: number): string {
  if (mult >= 2) return 'green'
  if (mult >= 1.3) return 'bright-green'
  return 'red'
}

// Initialize TradingView Lightweight Chart (MyBalls style)
const initChart = () => {
  if (!chartContainerRef.value) return

  const container = chartContainerRef.value

  chart = createChart(container, {
    width: container.clientWidth,
    height: container.clientHeight,
    layout: {
      background: { type: ColorType.Solid, color: 'transparent' },
      textColor: 'rgba(255, 255, 255, 0.5)',
      fontFamily: "'SF Pro Text', -apple-system, sans-serif",
      fontSize: 11,
    },
    grid: {
      vertLines: { visible: false },
      horzLines: { color: 'rgba(255, 255, 255, 0.06)', style: 1 },
    },
    crosshair: {
      mode: 0, // Disabled
    },
    rightPriceScale: {
      visible: false,
    },
    leftPriceScale: {
      visible: true,
      borderVisible: false,
      scaleMargins: { top: 0.05, bottom: 0.05 },
      entireTextOnly: true,
    },
    timeScale: {
      visible: false,
      borderVisible: false,
      rightOffset: 5,
      barSpacing: 8,
      fixLeftEdge: true,
      fixRightEdge: false,
    },
    handleScroll: false,
    handleScale: false,
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#09D76D',
    downColor: '#FB2C36',
    borderUpColor: '#09D76D',
    borderDownColor: '#FB2C36',
    wickUpColor: '#09D76D',
    wickDownColor: '#FB2C36',
    priceScaleId: 'left',
  })

  // Set fixed price scale 0-5 like MyBalls
  candleSeries.priceScale().applyOptions({
    autoScale: false,
    scaleMargins: { top: 0.02, bottom: 0.02 },
  })

  // Fix visible range to 0-5
  chart.priceScale('left').applyOptions({
    autoScale: false,
  })
}

// Update chart with new candle data
const updateChart = () => {
  if (!candleSeries || !currentCandle.value) return

  const candleData = {
    time: currentCandle.value.time as any,
    open: currentCandle.value.open,
    high: currentCandle.value.high,
    low: currentCandle.value.low,
    close: currentCandle.value.close,
  }

  candleSeries.update(candleData)

  // Update price line position
  updatePriceLinePosition()
}

const updatePriceLinePosition = () => {
  if (!chart) return
  // Approximate price line position calculation
  const containerHeight = chartHeight.value
  const price = currentMultiplier.value
  const minPrice = Math.min(0.5, ...candles.value.map(c => c.low), price)
  const maxPrice = Math.max(2.0, ...candles.value.map(c => c.high), price)
  const range = maxPrice - minPrice
  const normalized = (price - minPrice) / range
  priceLineTop.value = containerHeight - (normalized * containerHeight * 0.85) - 10
}

// Player actions
const placeBet = () => {
  if (!canBuy.value) return
  playerBet.value = selectedBet.value
  balance.value -= selectedBet.value

  traders.value.push({
    id: Date.now(),
    name: 'you',
    bet: selectedBet.value,
    color: '#0098EA',
    exited: false,
    profit: 0
  })
}

const cashOut = () => {
  if (!canSell.value || !playerBet.value) return

  const payout = playerBet.value * currentMultiplier.value
  const profit = payout - playerBet.value
  balance.value += payout

  const me = traders.value.find(t => t.name === 'you')
  if (me) {
    me.exited = true
    me.profit = profit
  }

  playerBet.value = null
}

// Game simulation
let gameInterval: number | null = null
let countdownInterval: number | null = null
let tickCount = 0
let momentum = 0

const VOLATILITY = 0.025
const DRIFT = -0.0008
const MOMENTUM_DECAY = 0.92
const TICKS_PER_CANDLE = 18

const startGame = () => {
  gameState.value = 'active'
  currentMultiplier.value = 1.0
  tickCount = 0
  momentum = 0
  candleIndex = Date.now()

  // Clear old data
  candles.value = []
  if (candleSeries) {
    candleSeries.setData([])
  }

  // Initialize first candle
  currentCandle.value = {
    time: candleIndex,
    open: 1.0,
    high: 1.0,
    low: 1.0,
    close: 1.0,
  }

  // Add initial candle
  if (candleSeries) {
    candleSeries.update({
      time: candleIndex as any,
      open: 1.0,
      high: 1.0,
      low: 1.0,
      close: 1.0,
    })
  }

  // Simulate other traders joining
  setTimeout(() => {
    if (gameState.value === 'active') {
      const names = ['vomki', 'Kweer_gg', 'lucky_star', 'whale_99']
      const name = names[Math.floor(Math.random() * names.length)]
      const amount = 0.1 + Math.random() * 0.5
      traders.value.push({
        id: Date.now(),
        name,
        bet: amount,
        color: `hsl(${Math.random() * 360}, 70%, 50%)`,
        exited: false,
        profit: 0
      })
    }
  }, 500 + Math.random() * 1000)

  gameInterval = window.setInterval(() => {
    if (gameState.value !== 'active') return

    tickCount++

    // Volatile price movement
    const downProb = 0.50 + tickCount * 0.0003
    const momentumBias = momentum * 0.3
    const effectiveDownProb = Math.max(0.3, Math.min(0.7, downProb - momentumBias))
    const direction = Math.random() > effectiveDownProb ? 1 : -1
    const magnitude = Math.random() * VOLATILITY
    const priceChange = (direction * magnitude) + DRIFT

    momentum = momentum * MOMENTUM_DECAY + (direction * 0.015 * Math.random())
    currentMultiplier.value = Math.max(0, currentMultiplier.value + priceChange)

    // Update current candle
    if (currentCandle.value) {
      currentCandle.value.close = currentMultiplier.value
      currentCandle.value.high = Math.max(currentCandle.value.high, currentMultiplier.value)
      currentCandle.value.low = Math.min(currentCandle.value.low, currentMultiplier.value)
      updateChart()
    }

    // New candle every N ticks
    if (tickCount >= TICKS_PER_CANDLE) {
      if (currentCandle.value) {
        candles.value.push({ ...currentCandle.value })
      }

      candleIndex++
      currentCandle.value = {
        time: candleIndex,
        open: currentMultiplier.value,
        high: currentMultiplier.value,
        low: currentMultiplier.value,
        close: currentMultiplier.value,
      }
      tickCount = 0
    }

    // Fake trader activity
    if (Math.random() < 0.012) {
      const names = ['lucky_star', 'moon_boy', 'diamond_h', 'whale_99']
      const action = Math.random() > 0.4 ? 'buy' : 'sell'
      const name = names[Math.floor(Math.random() * names.length)]

      if (action === 'sell') {
        const trader = traders.value.find(t => t.name === name && !t.exited)
        if (trader) {
          trader.exited = true
          trader.profit = trader.bet * currentMultiplier.value - trader.bet
        }
      } else {
        traders.value.push({
          id: Date.now() + Math.random(),
          name,
          bet: 0.1 + Math.random() * 0.5,
          color: `hsl(${Math.random() * 360}, 70%, 50%)`,
          exited: false,
          profit: 0
        })
      }
    }

    // Crash at 0.000x
    if (currentMultiplier.value <= 0.001) {
      crashGame()
    }
  }, 80)
}

const crashGame = () => {
  if (gameInterval) {
    clearInterval(gameInterval)
    gameInterval = null
  }

  const maxReached = Math.max(...candles.value.map(c => c.high), currentCandle.value?.high || 1, 1)
  gameState.value = 'crashed'
  currentMultiplier.value = 0

  // Final candle update
  if (currentCandle.value && candleSeries) {
    currentCandle.value.close = 0
    currentCandle.value.low = 0
    candleSeries.update({
      time: currentCandle.value.time as any,
      open: currentCandle.value.open,
      high: currentCandle.value.high,
      low: 0,
      close: 0,
    })
  }

  // Update recent games
  recentGames.value.unshift({ maxMult: maxReached, path: generateMiniPath() })
  recentGames.value = recentGames.value.slice(0, 6)

  // Liquidate player if still in
  if (playerBet.value) {
    const me = traders.value.find(t => t.name === 'you')
    if (me) {
      me.exited = true
      me.profit = -me.bet
    }
    playerBet.value = null
  }

  setTimeout(startCountdown, 3000)
}

const startCountdown = () => {
  gameState.value = 'countdown'
  countdownSeconds.value = 5
  gameNumber.value++
  gameHash.value = Math.random().toString(36).substring(2, 6) + '...' + Math.random().toString(36).substring(2, 6)
  traders.value = []
  candles.value = []

  countdownInterval = window.setInterval(() => {
    countdownSeconds.value -= 0.05
    if (countdownSeconds.value <= 0) {
      if (countdownInterval) {
        clearInterval(countdownInterval)
        countdownInterval = null
      }
      startGame()
    }
  }, 50)
}

// Lifecycle
onMounted(() => {
  nextTick(() => {
    initChart()
  })

  // Ping simulation
  setInterval(() => {
    ping.value = Math.floor(50 + Math.random() * 80)
  }, 3000)

  // Start first game
  setTimeout(startGame, 1500)

  // Handle resize
  const resizeObserver = new ResizeObserver(() => {
    if (chart && chartContainerRef.value) {
      chart.applyOptions({
        width: chartContainerRef.value.clientWidth,
        height: chartContainerRef.value.clientHeight,
      })
      chartHeight.value = chartContainerRef.value.clientHeight
    }
  })

  if (chartContainerRef.value) {
    resizeObserver.observe(chartContainerRef.value)
  }
})

onUnmounted(() => {
  if (gameInterval) clearInterval(gameInterval)
  if (countdownInterval) clearInterval(countdownInterval)
  if (chart) {
    chart.remove()
    chart = null
  }
})
</script>

<style scoped>
/* === MyBalls.io Trading Style with Lightweight Charts === */

.trading-view {
  min-height: 100vh;
  background: #0C0C0C;
  color: #fff;
  font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 15px;
  padding-bottom: 100px;
  position: relative;
}

/* Game Plate Background */
.game-plate {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 180px;
  background: linear-gradient(135deg, #0d1a2d 0%, #0a1525 50%, #061020 100%);
  background-image: url('/images/app-trading-bg-1.webp');
  background-size: cover;
  background-position: center;
  z-index: 0;
  border-radius: 0 0 32px 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trading-plate {
  background: linear-gradient(135deg, #0a1a30 0%, #061428 100%);
}

.plate-title {
  font-size: 24px;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
  letter-spacing: 1px;
  opacity: 0.9;
}

/* Tournament Banner */
.tournament-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #0098EA 0%, #006AFF 100%);
  padding: 10px 20px;
  border-radius: 24px;
  cursor: pointer;
  margin-bottom: 12px;
}

.banner-emoji {
  font-size: 18px;
}

.banner-text {
  font-size: 14px;
  font-weight: 600;
}

.banner-timer {
  font-size: 14px;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

/* Top Bar */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.top-left {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 40px;
  height: 40px;
  background: #1D1E20;
  border: none;
  border-radius: 14px;
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.balance-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1D1E20;
  padding: 8px 12px;
  border-radius: 16px;
  cursor: pointer;
}

.ton-icon {
  width: 16px;
  height: 16px;
}

.balance-value {
  font-size: 14px;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.balance-add {
  width: 20px;
  height: 20px;
  background: #414244;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #fff;
}

/* Chart Wrapper - Square aspect ratio like MyBalls */
.chart-wrapper {
  width: 100%;
  aspect-ratio: 1;
  margin-bottom: 16px;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0E0F14;
  border: 2px solid #191919;
  border-radius: 32px;
  overflow: hidden;
  backdrop-filter: blur(14px);
}

/* Ping Indicator */
.ping-indicator {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* Multiplier Display */
.multiplier-display {
  position: absolute;
  right: 20px;
  z-index: 20;
  pointer-events: none;
  transition: top 0.1s ease-out;
}

.multiplier-value {
  font-size: 18px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.multiplier-display.crashed .multiplier-value {
  color: #FB2C36;
}

.multiplier-display.negative .multiplier-value {
  color: #FB2C36;
}

.multiplier-display.high .multiplier-value {
  color: #09D76D;
}

/* Price Line */
.price-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  z-index: 10;
  pointer-events: none;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0.6) 0%,
    rgba(255, 255, 255, 0.6) 60%,
    rgba(255, 255, 255, 0.3) 80%,
    transparent 100%
  );
  animation: dashMove 0.5s linear infinite;
}

@keyframes dashMove {
  from { background-position: 0 0; }
  to { background-position: 14px 0; }
}

/* Crash Overlay */
.crash-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 34px;
  background: #191919;
  border-radius: 16px 16px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
}

.crash-skulls {
  display: flex;
  gap: 8px;
  font-size: 20px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}

/* Countdown Overlay */
.countdown-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(14, 15, 20, 0.8);
  z-index: 25;
}

.countdown-value {
  font-size: 48px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  color: #0098EA;
}

/* Recent Games - MyBalls style */
.recent-games {
  margin-bottom: 16px;
}

.recent-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 10px;
  display: block;
  text-align: center;
}

.recent-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.recent-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.mini-chart {
  width: 100%;
  height: 60px;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  padding: 1px;
}

.mini-chart::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(135deg, var(--chart-color, #09D76D) 0%, transparent 50%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.9;
}

.mini-chart.red {
  --chart-color: #FB2C36;
}

.mini-chart.green {
  --chart-color: #09D76D;
}

.mini-chart.bright-green {
  --chart-color: #85FFB2;
}

.mini-chart svg {
  width: 100%;
  height: 100%;
}

.recent-mult {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  font-family: ui-monospace, monospace;
}

.recent-mult.high {
  color: #85FFB2;
}

.recent-mult.low {
  color: #FB2C36;
}

/* Traders Panel - MyBalls style */
.traders-panel {
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(15px);
  border-radius: 32px;
  padding: 16px;
  margin-bottom: 16px;
}

.panel-border {
  position: absolute;
  inset: 0;
  border-radius: 32px;
  border: 1px solid;
  border-image: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 50%) 1;
  pointer-events: none;
}

.traders-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.traders-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  font-weight: 700;
}

.title-text {
  color: #fff;
}

.traders-count {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.traders-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

/* Trader Card - MyBalls style */
.trader-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px;
  border-radius: 22px;
  background: rgba(52, 205, 239, 0.15);
  transition: background 0.2s;
}

.trader-card.exited {
  background: rgba(52, 205, 239, 0.15);
}

.trader-card.playing {
  background: rgba(255, 165, 0, 0.15);
}

.trader-left {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

/* Level Badge */
.level-badge {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.level-badge::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border-radius: 6px;
  transform: rotate(45deg);
}

.level-num {
  position: relative;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
}

/* Avatar */
.trader-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-letter {
  font-size: 14px;
  font-weight: 700;
  color: #000;
}

/* Name block */
.trader-name-block {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.trader-name {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  padding: 2px 6px;
  border-radius: 90px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.exited {
  background: rgba(52, 205, 239, 0.25);
  color: #34CDEF;
}

.status-badge.playing {
  background: rgba(255, 165, 0, 0.25);
  color: #FFA500;
}

/* Right side - profit & bet */
.trader-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.profit-display {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.profit-display.positive {
  color: #00CD3A;
}

.profit-display.negative {
  color: #FB2C36;
}

.profit-display .profit-value {
  transition: transform 0.2s;
}

.bet-display {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #fff;
  font-family: ui-monospace, monospace;
}

.ton-mini {
  flex-shrink: 0;
}

/* Panel Footer */
.panel-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.game-number {
  font-size: 11px;
}

.hash-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #fff;
  opacity: 0.5;
  font-size: 11px;
  cursor: pointer;
}

.hash-btn:hover {
  opacity: 0.8;
}

/* Legacy styles */
.btn-ton-icon {
  flex-shrink: 0;
  margin-right: 2px;
}

.swap-star-icon {
  object-fit: contain;
}

/* Bet Controls */
.bet-controls {
  margin-bottom: 12px;
}

.bet-amounts {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  justify-content: center;
}

.bet-pill {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #414244;
  border: none;
  border-radius: 16px;
  padding: 10px 14px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bet-pill.active {
  background: #0098EA;
  color: #fff;
}

.bet-pill:hover:not(.active) {
  background: #2D2E30;
}

.pill-diamond {
  width: 14px;
  height: 14px;
  color: #0098EA;
}

.bet-pill.active .pill-diamond {
  color: #fff;
}

.max-pill {
  background: #414244;
}

.edit-pill {
  padding: 10px 12px;
}

/* Action Row */
.action-row {
  display: flex;
  gap: 8px;
}

.swap-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: #181818;
  border: none;
  border-radius: 16px;
  padding: 10px 14px;
  color: #0098EA;
  font-size: 11px;
  cursor: pointer;
}

.swap-icon {
  width: 20px;
  height: 20px;
}

.swap-star {
  color: #FFD700;
  font-size: 10px;
}

.buy-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #09D76D;
  border: none;
  border-radius: 20px;
  padding: 14px 24px;
  color: #101010;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.buy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.buy-btn:not(:disabled):hover {
  opacity: 0.9;
}

.btn-diamond {
  color: #101010;
}

.btn-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.btn-label {
  font-size: 16px;
  font-weight: 600;
}

.btn-amount {
  font-size: 12px;
  opacity: 0.7;
}

.sell-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FB2C36 0%, #FF6B7A 100%);
  border: none;
  border-radius: 20px;
  padding: 14px 24px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.sell-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-percent {
  font-size: 14px;
  margin-left: 4px;
}

.btn-percent.positive {
  color: #4ade80;
}

.btn-percent.negative {
  color: #fca5a5;
}

.deposit-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: #181818;
  border: none;
  border-radius: 16px;
  padding: 10px 14px;
  color: #0098EA;
  font-size: 11px;
  cursor: pointer;
}

.deposit-plus {
  font-size: 20px;
  font-weight: 300;
}

/* Bottom Navigation */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #0C0C0C;
  display: flex;
  justify-content: space-around;
  padding: 8px 0 24px;
  border-top: 1px solid #262729;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  text-decoration: none;
}

.nav-item.active {
  color: #0098EA;
}

.nav-item svg {
  width: 20px;
  height: 20px;
}
</style>
