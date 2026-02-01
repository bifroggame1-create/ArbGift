<template>
  <div class="trading-view">
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

    <!-- Connection & Game Info Bar -->
    <div class="info-bar">
      <div class="connection-status">
        <span class="status-dot"></span>
        <span>Connected</span>
      </div>
      <div class="game-meta">
        <span class="game-number">ИГРА #{{ gameNumber }}</span>
        <span class="game-hash">{{ gameHash }}</span>
      </div>
    </div>

    <!-- Candlestick Chart Container -->
    <div class="chart-container">
      <svg class="chart-svg" :viewBox="`0 0 ${chartWidth} ${chartHeight}`" preserveAspectRatio="none">
        <!-- Background Grid -->
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)"/>

        <!-- Horizontal price lines -->
        <g class="price-lines">
          <line v-for="i in 5" :key="'hline-'+i"
            x1="0" :y1="chartHeight * i / 5"
            :x2="chartWidth - 40" :y2="chartHeight * i / 5"
            stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4,4"/>
        </g>

        <!-- Entry price dashed line (1.00x baseline) -->
        <line
          x1="0" :y1="priceToY(1.0)"
          :x2="chartWidth - 40" :y2="priceToY(1.0)"
          stroke="#4b5563" stroke-width="1" stroke-dasharray="6,4"
          opacity="0.8"/>

        <!-- Candlesticks -->
        <g class="candlesticks">
          <g v-for="(candle, idx) in visibleCandles" :key="'candle-'+idx">
            <!-- Wick (shadow) -->
            <line
              :x1="getCandleX(idx) + candleWidth / 2"
              :y1="priceToY(candle.high)"
              :x2="getCandleX(idx) + candleWidth / 2"
              :y2="priceToY(candle.low)"
              :stroke="candle.close >= candle.open ? '#22c55e' : '#ef4444'"
              stroke-width="1.5"
            />
            <!-- Body -->
            <rect
              :x="getCandleX(idx) + 2"
              :y="priceToY(Math.max(candle.open, candle.close))"
              :width="candleWidth - 4"
              :height="Math.max(3, Math.abs(priceToY(candle.open) - priceToY(candle.close)))"
              :fill="candle.close >= candle.open ? '#22c55e' : '#ef4444'"
              rx="1"
            />
          </g>
        </g>

        <!-- Current candle being formed (during active game) -->
        <g v-if="gameState === 'active' && currentCandle" class="current-candle">
          <!-- Wick -->
          <line
            :x1="getCurrentCandleX() + candleWidth / 2"
            :y1="priceToY(currentCandle.high)"
            :x2="getCurrentCandleX() + candleWidth / 2"
            :y2="priceToY(currentCandle.low)"
            :stroke="currentCandleColor"
            stroke-width="2"
          />
          <!-- Body -->
          <rect
            :x="getCurrentCandleX() + 2"
            :y="priceToY(Math.max(currentCandle.open, currentCandle.close))"
            :width="candleWidth - 4"
            :height="Math.max(4, Math.abs(priceToY(currentCandle.open) - priceToY(currentCandle.close)))"
            :fill="currentCandleColor"
            rx="1"
          >
            <animate attributeName="opacity" values="1;0.7;1" dur="0.5s" repeatCount="indefinite"/>
          </rect>
        </g>

        <!-- Price line (during active game) - color based on trend -->
        <path
          v-if="pricePath && gameState === 'active'"
          :d="pricePath"
          fill="none"
          :stroke="priceLineColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- Glow effect -->
        <path
          v-if="pricePath && gameState === 'active'"
          :d="pricePath"
          fill="none"
          :stroke="priceLineColor"
          stroke-width="8"
          stroke-linecap="round"
          opacity="0.2"
          filter="blur(4px)"
        />
      </svg>

      <!-- Y-Axis Labels -->
      <div class="y-axis-labels">
        <span v-for="price in yAxisLabels" :key="price" class="y-label">{{ price.toFixed(2) }}x</span>
      </div>

      <!-- Multiplier Overlay -->
      <div class="multiplier-overlay" :class="multiplierClass">
        <template v-if="gameState === 'active'">
          <span class="multiplier-value" :class="{ negative: currentMultiplier < 1.0 }">
            {{ currentMultiplier.toFixed(3) }}x
          </span>
          <span class="multiplier-label">МНОЖИТЕЛЬ</span>
          <!-- Show P/L when player has bet -->
          <span v-if="playerBet" class="player-pl" :class="{ positive: currentPL >= 0, negative: currentPL < 0 }">
            {{ currentPL >= 0 ? '+' : '' }}{{ currentPL.toFixed(2) }} TON
          </span>
        </template>
        <template v-else-if="gameState === 'crashed'">
          <span class="multiplier-crashed">
            💀💀💀 0.000x
          </span>
          <span class="crash-label">ЛИКВИДАЦИЯ!</span>
        </template>
        <template v-else-if="gameState === 'countdown'">
          <div class="countdown-display">
            <span class="countdown-text">Новая игра начнется через</span>
            <span class="countdown-timer">{{ countdownSeconds.toFixed(2) }}s</span>
          </div>
        </template>
        <template v-else>
          <span class="waiting-text">Ожидание ставок...</span>
        </template>
      </div>

      <!-- Floating trader notifications -->
      <transition-group name="notification-fade" tag="div" class="trader-notifications">
        <div
          v-for="notif in traderNotifications"
          :key="notif.id"
          class="trader-notif"
          :class="notif.type"
          :style="{ top: notif.y + 'px', left: notif.x + 'px' }"
        >
          @{{ notif.username }} {{ notif.type === 'buy' ? 'Купил' : 'Продал' }}
          <span :class="notif.type === 'buy' ? 'amount-buy' : 'amount-sell'">
            {{ notif.type === 'buy' ? '+' : '+' }}{{ notif.amount.toFixed(2) }}
          </span>
          <span class="notif-icon">◇</span>
        </div>
      </transition-group>

      <!-- Ping indicator -->
      <div class="ping-indicator">
        <span class="ping-dot"></span>
        {{ ping }}ms
      </div>
    </div>

    <!-- Recent Games (Последние игры) -->
    <div class="recent-games">
      <div class="recent-header">
        <span class="recent-title">Последние игры</span>
      </div>
      <div class="recent-list">
        <div
          v-for="(game, idx) in recentGames"
          :key="idx"
          class="recent-game-item"
          :class="{ crashed: game.crashAt < 1.1 }"
        >
          <!-- Mini candlestick chart -->
          <div class="mini-chart">
            <svg viewBox="0 0 40 30" preserveAspectRatio="none">
              <path
                :d="game.miniPath"
                fill="none"
                :stroke="game.crashAt >= 2 ? '#22c55e' : '#ef4444'"
                stroke-width="1.5"
              />
            </svg>
          </div>
          <span class="game-multiplier" :class="{ high: game.crashAt >= 2, low: game.crashAt < 2 }">
            {{ game.crashAt < 1.1 ? '💀' : '' }}{{ game.crashAt.toFixed(2) }}x
          </span>
        </div>
      </div>
    </div>

    <!-- History Strip -->
    <div class="history-strip">
      <div
        v-for="(crash, idx) in crashHistory"
        :key="idx"
        class="history-badge"
        :class="{ high: crash >= 2, low: crash < 2 }"
      >
        {{ crash.toFixed(2) }}x
      </div>
    </div>

    <!-- Traders Panel -->
    <div class="traders-panel">
      <div class="traders-header">
        <span class="traders-title">Трейдеры</span>
        <span class="traders-count">{{ traders.length }}</span>
      </div>
      <div class="traders-list">
        <div
          v-for="trader in traders"
          :key="trader.id"
          class="trader-row"
          :class="{ exited: trader.exited, you: trader.isYou }"
        >
          <div class="trader-left">
            <div class="trader-avatar" :style="{ background: trader.color }">
              {{ trader.name.charAt(0).toUpperCase() }}
            </div>
            <div class="trader-info">
              <span class="trader-name">@{{ trader.name }}</span>
              <span class="trader-bet">{{ trader.bet }} TON</span>
            </div>
          </div>
          <div class="trader-right">
            <template v-if="trader.exited">
              <span class="trader-exited-label">Вышел</span>
              <span class="trader-profit" :class="{ positive: trader.profit > 0 }">
                {{ trader.profit > 0 ? '+' : '' }}{{ trader.profit.toFixed(2) }}
              </span>
            </template>
            <template v-else-if="gameState === 'active'">
              <span class="trader-multiplier">{{ currentMultiplier.toFixed(2) }}x</span>
            </template>
            <template v-else>
              <span class="trader-waiting">⏳</span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Bet Controls -->
    <div class="bet-section">
      <!-- Bet Amount Buttons -->
      <div class="bet-amounts">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          class="bet-btn"
          :class="{ active: selectedBet === amount }"
          @click="selectedBet = amount"
        >
          {{ amount }} <span class="bet-icon">💎</span>
        </button>
      </div>

      <!-- Action Buttons -->
      <div class="action-row">
        <button
          class="action-btn buy-btn"
          :disabled="!canBuy"
          @click="placeBet"
        >
          <span class="btn-emoji">📈</span>
          {{ playerBet ? 'Ставка сделана' : `Купить ${selectedBet} TON` }}
        </button>
        <button
          class="action-btn sell-btn"
          :class="{ 'in-loss': playerBet && currentPL < 0 }"
          :disabled="!canSell"
          @click="cashOut"
        >
          <span class="btn-emoji">📉</span>
          <span v-if="playerBet">
            Продать <span :class="currentPL >= 0 ? 'profit-text' : 'loss-text'">
              {{ currentPL >= 0 ? '+' : '' }}{{ currentPL.toFixed(2) }}
            </span>
          </span>
          <span v-else>Продать</span>
        </button>
      </div>

      <!-- Auto-sell Options -->
      <div class="autosell-row">
        <span class="autosell-label">Авто-продажа:</span>
        <div class="autosell-options">
          <button
            v-for="mult in autoSellMultipliers"
            :key="mult"
            class="autosell-btn"
            :class="{ active: autoSellAt === mult }"
            @click="autoSellAt = autoSellAt === mult ? null : mult"
          >
            {{ mult }}x
          </button>
        </div>
      </div>
    </div>

    <!-- Game Hash Footer -->
    <div class="game-footer">
      <span class="footer-label">Game #{{ gameNumber }}</span>
      <span class="footer-hash">Hash: {{ gameHash }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

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
  exited: boolean
  profit: number
  isYou: boolean
}

interface TraderNotification {
  id: number
  username: string
  type: 'buy' | 'sell'
  amount: number
  x: number
  y: number
}

interface RecentGame {
  crashAt: number
  miniPath: string
}

// Chart config
const chartWidth = 360
const chartHeight = 200
const candleWidth = 18
const maxVisibleCandles = Math.floor((chartWidth - 50) / candleWidth)

// Game state
const gameState = ref<'waiting' | 'active' | 'crashed' | 'countdown'>('waiting')
const currentMultiplier = ref(1.0)
const crashedAt = ref(0)
const countdownSeconds = ref(5)
const gameNumber = ref(28392)
const gameHash = ref('3d07...f8da')
const ping = ref(74)

// Candle data
const candles = ref<Candle[]>([])
const currentCandle = ref<Candle | null>(null)
const priceHistory = ref<number[]>([])

// Player state
const balance = ref(3.16)
const selectedBet = ref(1)
const playerBet = ref<number | null>(null)
const autoSellAt = ref<number | null>(null)
const betAmounts = [0.5, 1, 2, 5]
const autoSellMultipliers = [1.5, 2, 3, 5, 10]

// Traders
const traders = ref<Trader[]>([
  { id: 1, name: 'you', bet: 1, color: '#facc15', exited: false, profit: 0, isYou: true },
  { id: 2, name: 'trader1', bet: 2.5, color: '#22c55e', exited: false, profit: 0, isYou: false },
])

// Notifications
const traderNotifications = ref<TraderNotification[]>([])
let notifId = 0

// Recent games & crash history
const crashHistory = ref([2.34, 1.12, 5.67, 1.89, 3.21, 1.05, 8.92, 2.11])
const recentGames = ref<RecentGame[]>([])

// Generate initial data
const generateCandles = () => {
  const result: Candle[] = []
  let price = 1.0
  for (let i = 0; i < 12; i++) {
    const open = price
    const change = (Math.random() - 0.4) * 0.25
    const close = Math.max(0.6, price + change)
    const wickUp = Math.random() * 0.08
    const wickDown = Math.random() * 0.08
    const high = Math.max(open, close) + wickUp
    const low = Math.min(open, close) - wickDown
    result.push({ open, high, low, close, time: Date.now() - (12 - i) * 5000 })
    price = close
  }
  return result
}

const generateMiniPath = (): string => {
  const points: string[] = []
  let y = 15 + Math.random() * 10
  for (let x = 0; x <= 40; x += 4) {
    y += (Math.random() - 0.45) * 6
    y = Math.max(5, Math.min(25, y))
    points.push(`${x},${y}`)
  }
  return `M ${points.join(' L ')}`
}

const generateRecentGames = () => {
  return crashHistory.value.slice(0, 6).map(crashAt => ({
    crashAt,
    miniPath: generateMiniPath()
  }))
}

// Initialize
candles.value = generateCandles()
recentGames.value = generateRecentGames()

// Computed
const visibleCandles = computed(() => candles.value.slice(-maxVisibleCandles))

const minPrice = computed(() => {
  const prices = visibleCandles.value.flatMap(c => [c.low, c.high])
  if (currentCandle.value) {
    prices.push(currentCandle.value.low, currentCandle.value.high)
  }
  prices.push(...priceHistory.value)
  return Math.max(0.5, Math.min(...prices, 1) - 0.15)
})

const maxPrice = computed(() => {
  const prices = visibleCandles.value.flatMap(c => [c.low, c.high])
  if (currentCandle.value) {
    prices.push(currentCandle.value.low, currentCandle.value.high)
  }
  prices.push(...priceHistory.value)
  return Math.max(...prices, 1) + 0.3
})

const yAxisLabels = computed(() => {
  const labels = []
  const step = (maxPrice.value - minPrice.value) / 4
  for (let i = 0; i <= 4; i++) {
    labels.push(maxPrice.value - step * i)
  }
  return labels
})

const priceToY = (price: number): number => {
  const range = maxPrice.value - minPrice.value
  return chartHeight - ((price - minPrice.value) / range) * chartHeight
}

const getCandleX = (idx: number): number => {
  return idx * candleWidth + 10
}

const getCurrentCandleX = (): number => {
  return visibleCandles.value.length * candleWidth + 10
}

const pricePath = computed(() => {
  if (priceHistory.value.length < 2) return ''
  const startX = getCurrentCandleX() + candleWidth / 2
  const points = priceHistory.value.map((price, i) => {
    const x = startX + i * 2
    const y = priceToY(price)
    return `${x},${y}`
  })
  return `M ${points.join(' L ')}`
})

const multiplierClass = computed(() => {
  if (gameState.value === 'crashed') return 'crashed'
  if (currentMultiplier.value < 1.0) return 'negative'  // Below entry price
  if (currentMultiplier.value >= 2) return 'high'
  if (currentMultiplier.value >= 1.5) return 'medium'
  return 'normal'
})

// Current P/L for player (can be negative!)
const currentPL = computed(() => {
  if (!playerBet.value) return 0
  return (playerBet.value * currentMultiplier.value) - playerBet.value
})

// Current candle color based on direction
const currentCandleColor = computed(() => {
  if (!currentCandle.value) return '#22c55e'
  return currentCandle.value.close >= currentCandle.value.open ? '#22c55e' : '#ef4444'
})

// Price line color based on current trend
const priceLineColor = computed(() => {
  if (priceHistory.value.length < 2) return '#22c55e'
  const last = priceHistory.value[priceHistory.value.length - 1]
  const prev = priceHistory.value[priceHistory.value.length - 2]
  return last >= prev ? '#22c55e' : '#ef4444'
})

const canBuy = computed(() => {
  return (gameState.value === 'waiting' || gameState.value === 'countdown') && !playerBet.value
})

const canSell = computed(() => {
  return gameState.value === 'active' && playerBet.value !== null
})

// Methods
const addNotification = (username: string, type: 'buy' | 'sell', amount: number) => {
  const notif: TraderNotification = {
    id: notifId++,
    username,
    type,
    amount,
    x: 50 + Math.random() * 150,
    y: 40 + Math.random() * 80
  }
  traderNotifications.value.push(notif)
  setTimeout(() => {
    const idx = traderNotifications.value.findIndex(n => n.id === notif.id)
    if (idx !== -1) traderNotifications.value.splice(idx, 1)
  }, 2500)
}

const placeBet = () => {
  if (!canBuy.value) return
  playerBet.value = selectedBet.value
  balance.value -= selectedBet.value

  // Update trader entry
  const me = traders.value.find(t => t.isYou)
  if (me) {
    me.bet = selectedBet.value
    me.exited = false
    me.profit = 0
  }

  addNotification('you', 'buy', selectedBet.value)
}

const cashOut = () => {
  if (!canSell.value || !playerBet.value) return

  const payout = playerBet.value * currentMultiplier.value
  const profit = payout - playerBet.value
  balance.value += payout

  // Update trader
  const me = traders.value.find(t => t.isYou)
  if (me) {
    me.exited = true
    me.profit = profit
  }

  addNotification('you', 'sell', profit)
  playerBet.value = null
}

// Game simulation - VOLATILE MODEL (not Aviator!)
let gameInterval: number | null = null
let countdownInterval: number | null = null
let tickCount = 0
let gameStartTime = 0
let momentum = 0  // For creating price trends

// Volatility parameters
const VOLATILITY = 0.025        // Base volatility per tick
const DRIFT = -0.0008           // Slight negative drift (house edge)
const MOMENTUM_DECAY = 0.92     // How fast momentum decays
const MOMENTUM_NOISE = 0.015    // Random momentum changes
const TICKS_PER_CANDLE = 20     // Ticks before new candle

// Get probability of price going down (increases over time = house edge)
const getDownProbability = (elapsedSeconds: number) => {
  // Start at 50%, gradually increase chance of down movement
  return 0.50 + elapsedSeconds * 0.0015  // +0.15% per second
}

const startGame = () => {
  gameState.value = 'active'
  currentMultiplier.value = 1.0
  priceHistory.value = [1.0]
  tickCount = 0
  gameStartTime = Date.now()
  momentum = 0

  // Initialize current candle from 1.0
  currentCandle.value = {
    open: 1.0,
    high: 1.0,
    low: 1.0,
    close: 1.0,
    time: Date.now()
  }

  // Simulate fake traders buying in
  setTimeout(() => {
    if (gameState.value === 'active') {
      addNotification('vomki', 'buy', 0.16 + Math.random() * 0.5)
    }
  }, 500 + Math.random() * 1000)

  setTimeout(() => {
    if (gameState.value === 'active') {
      addNotification('Kweer_gg', 'buy', 0.03 + Math.random() * 0.3)
    }
  }, 1200 + Math.random() * 800)

  gameInterval = window.setInterval(() => {
    if (gameState.value !== 'active') return

    tickCount++
    const elapsedSeconds = (Date.now() - gameStartTime) / 1000

    // === VOLATILE PRICE MODEL ===
    // 1. Calculate down probability (increases over time)
    const downProb = getDownProbability(elapsedSeconds)

    // 2. Determine direction with momentum influence
    const momentumBias = momentum * 0.3
    const effectiveDownProb = Math.max(0.3, Math.min(0.7, downProb - momentumBias))
    const direction = Math.random() > effectiveDownProb ? 1 : -1

    // 3. Calculate price change magnitude
    const magnitude = Math.random() * VOLATILITY

    // 4. Apply change with drift
    const priceChange = (direction * magnitude) + DRIFT

    // 5. Update momentum (creates trends - series of green/red candles)
    momentum = momentum * MOMENTUM_DECAY + (direction * MOMENTUM_NOISE * Math.random())

    // 6. Update current price (can't go below 0)
    currentMultiplier.value = Math.max(0, currentMultiplier.value + priceChange)

    // Add to price history
    priceHistory.value.push(currentMultiplier.value)
    if (priceHistory.value.length > 120) priceHistory.value.shift()

    // Update current candle
    if (currentCandle.value) {
      currentCandle.value.close = currentMultiplier.value
      currentCandle.value.high = Math.max(currentCandle.value.high, currentMultiplier.value)
      currentCandle.value.low = Math.min(currentCandle.value.low, currentMultiplier.value)
    }

    // Create new candle every N ticks
    if (tickCount >= TICKS_PER_CANDLE) {
      // Finalize current candle
      if (currentCandle.value) {
        candles.value.push({ ...currentCandle.value })
        // Keep only last 20 candles
        if (candles.value.length > 20) candles.value.shift()
      }

      // Start new candle
      currentCandle.value = {
        open: currentMultiplier.value,
        high: currentMultiplier.value,
        low: currentMultiplier.value,
        close: currentMultiplier.value,
        time: Date.now()
      }
      tickCount = 0
    }

    // Auto-sell check (only if in profit)
    if (autoSellAt.value && playerBet.value && currentMultiplier.value >= autoSellAt.value) {
      cashOut()
    }

    // Fake trader activity
    if (Math.random() < 0.015) {
      const names = ['lucky_star', 'crypto_king', 'moon_boy', 'diamond_hands', 'whale_hunter']
      const action = Math.random() > 0.4 ? 'buy' : 'sell'
      const amount = action === 'buy' ? (0.1 + Math.random() * 0.5) : (Math.random() * 1.5)
      addNotification(names[Math.floor(Math.random() * names.length)], action, amount)
    }

    // === CRASH ONLY AT 0.000x ===
    if (currentMultiplier.value <= 0.001) {
      crashGame(0)
    }
  }, 80)  // ~12.5 ticks per second
}

const crashGame = (_crashAt: number) => {
  if (gameInterval) {
    clearInterval(gameInterval)
    gameInterval = null
  }

  // Calculate max multiplier reached during this round for history
  const maxReached = Math.max(...priceHistory.value, 1)
  crashedAt.value = 0  // Always 0.000x for Trading

  gameState.value = 'crashed'

  // Finalize current candle (crashed to 0)
  if (currentCandle.value) {
    currentCandle.value.close = 0
    currentCandle.value.low = 0
    candles.value.push({ ...currentCandle.value })
    currentCandle.value = null
  }

  // Update crash history with max multiplier reached (for display)
  crashHistory.value.unshift(maxReached)
  crashHistory.value = crashHistory.value.slice(0, 10)
  recentGames.value = generateRecentGames()

  // Reset player bet if still active (they lost everything)
  if (playerBet.value) {
    const me = traders.value.find(t => t.isYou)
    if (me) {
      me.exited = true
      me.profit = -me.bet  // Lost full bet
    }
    playerBet.value = null
  }

  // Start countdown to next game
  setTimeout(startCountdown, 3000)
}

const startCountdown = () => {
  gameState.value = 'countdown'
  countdownSeconds.value = 5

  gameNumber.value++
  gameHash.value = Math.random().toString(36).substring(2, 10) + '...' + Math.random().toString(36).substring(2, 6)

  // Reset traders
  traders.value.forEach(t => {
    t.exited = false
    t.profit = 0
  })

  countdownInterval = window.setInterval(() => {
    countdownSeconds.value -= 0.05
    if (countdownSeconds.value <= 0) {
      if (countdownInterval) {
        clearInterval(countdownInterval)
        countdownInterval = null
      }
      priceHistory.value = []
      startGame()
    }
  }, 50)
}

// Watch for auto-sell
watch(currentMultiplier, (newVal) => {
  if (autoSellAt.value && playerBet.value && newVal >= autoSellAt.value && gameState.value === 'active') {
    cashOut()
  }
})

onMounted(() => {
  // Random ping simulation
  setInterval(() => {
    ping.value = Math.floor(50 + Math.random() * 80)
  }, 3000)

  // Start first game after delay
  setTimeout(startGame, 2000)
})

onUnmounted(() => {
  if (gameInterval) clearInterval(gameInterval)
  if (countdownInterval) clearInterval(countdownInterval)
})
</script>

<style scoped>
.trading-view {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0e17 0%, #0d1320 100%);
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
  padding-bottom: 100px;
}

/* Header */
.trading-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(0,0,0,0.3);
}

.header-back {
  width: 36px;
  height: 36px;
  background: #1c1f2e;
  border: none;
  border-radius: 10px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-main {
  font-size: 17px;
  font-weight: 600;
}

.title-badge {
  background: linear-gradient(135deg, #22c55e, #15803d);
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.header-balance {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1c1f2e;
  padding: 8px 12px;
  border-radius: 10px;
}

.balance-icon { font-size: 14px; }
.balance-value { font-size: 14px; font-weight: 600; }

.balance-add {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
}

/* Info Bar */
.info-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
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
  50% { opacity: 0.4; }
}

.game-meta {
  display: flex;
  gap: 12px;
  font-size: 10px;
  color: #6b7280;
  font-family: 'SF Mono', monospace;
}

/* Chart Container */
.chart-container {
  margin: 8px 12px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  border-radius: 16px;
  height: 220px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.05);
}

.chart-svg {
  width: calc(100% - 45px);
  height: 100%;
}

.y-axis-labels {
  position: absolute;
  right: 6px;
  top: 10px;
  bottom: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
}

.y-label {
  font-size: 9px;
  color: #4b5563;
  font-family: 'SF Mono', monospace;
}

/* Multiplier Overlay */
.multiplier-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  z-index: 10;
}

.multiplier-value {
  display: block;
  font-size: 48px;
  font-weight: 800;
  color: #22c55e;
  text-shadow: 0 0 40px rgba(34, 197, 94, 0.6);
  font-family: 'SF Mono', -apple-system, monospace;
  letter-spacing: -2px;
  transition: color 0.2s;
}

/* Negative multiplier (below 1.0x) */
.multiplier-value.negative,
.multiplier-overlay.negative .multiplier-value {
  color: #ef4444;
  text-shadow: 0 0 40px rgba(239, 68, 68, 0.6);
}

.multiplier-overlay.medium .multiplier-value {
  color: #60a5fa;
  text-shadow: 0 0 40px rgba(96, 165, 250, 0.6);
}

.multiplier-overlay.high .multiplier-value {
  color: #facc15;
  text-shadow: 0 0 40px rgba(250, 204, 21, 0.6);
}

/* Player P/L display */
.player-pl {
  display: block;
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
  padding: 4px 12px;
  border-radius: 8px;
  background: rgba(0,0,0,0.4);
}

.player-pl.positive {
  color: #4ade80;
}

.player-pl.negative {
  color: #f87171;
}

@keyframes glow-pulse {
  from { text-shadow: 0 0 40px rgba(250, 204, 21, 0.6); }
  to { text-shadow: 0 0 60px rgba(250, 204, 21, 0.9); }
}

.multiplier-overlay.high .multiplier-value {
  animation: glow-pulse 0.5s infinite alternate;
}

.multiplier-label {
  display: block;
  font-size: 10px;
  color: #6b7280;
  letter-spacing: 2px;
  margin-top: 4px;
}

.multiplier-crashed {
  font-size: 42px;
  font-weight: 800;
  color: #ef4444;
  text-shadow: 0 0 40px rgba(239, 68, 68, 0.5);
}

.crash-label {
  display: block;
  font-size: 12px;
  color: #ef4444;
  font-weight: 700;
  margin-top: 4px;
}

.countdown-display {
  text-align: center;
}

.countdown-text {
  display: block;
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 8px;
}

.countdown-timer {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: #60a5fa;
  font-family: 'SF Mono', monospace;
}

.waiting-text {
  font-size: 14px;
  color: #9ca3af;
}

/* Trader Notifications */
.trader-notifications {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.trader-notif {
  position: absolute;
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11px;
  color: #fff;
  white-space: nowrap;
  animation: float-up 2.5s ease-out forwards;
}

@keyframes float-up {
  0% { opacity: 0; transform: translateY(10px); }
  20% { opacity: 1; transform: translateY(0); }
  80% { opacity: 1; }
  100% { opacity: 0; transform: translateY(-20px); }
}

.notification-fade-enter-active,
.notification-fade-leave-active {
  transition: all 0.3s ease;
}

.notification-fade-enter-from,
.notification-fade-leave-to {
  opacity: 0;
}

.amount-buy { color: #4ade80; }
.amount-sell { color: #facc15; }
.notif-icon { color: #60a5fa; margin-left: 4px; }

/* Ping Indicator */
.ping-indicator {
  position: absolute;
  bottom: 8px;
  right: 8px;
  font-size: 10px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 4px;
}

.ping-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #4ade80;
}

/* Recent Games Section */
.recent-games {
  padding: 8px 12px;
}

.recent-header {
  margin-bottom: 8px;
}

.recent-title {
  font-size: 12px;
  color: #6b7280;
}

.recent-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.recent-game-item {
  flex-shrink: 0;
  width: 56px;
  background: #1c1f2e;
  border-radius: 8px;
  padding: 6px;
  text-align: center;
}

.mini-chart {
  height: 24px;
  margin-bottom: 4px;
}

.mini-chart svg {
  width: 100%;
  height: 100%;
}

.game-multiplier {
  font-size: 10px;
  font-weight: 600;
}

.game-multiplier.high { color: #4ade80; }
.game-multiplier.low { color: #ef4444; }

/* History Strip */
.history-strip {
  display: flex;
  gap: 6px;
  padding: 0 12px;
  margin-bottom: 12px;
  overflow-x: auto;
}

.history-badge {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
}

.history-badge.high {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.history-badge.low {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

/* Traders Panel */
.traders-panel {
  margin: 0 12px 12px;
  background: #1c1f2e;
  border-radius: 12px;
  overflow: hidden;
}

.traders-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.traders-title {
  font-size: 13px;
  font-weight: 600;
}

.traders-count {
  background: #27272a;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  color: #6b7280;
}

.traders-list {
  max-height: 120px;
  overflow-y: auto;
}

.trader-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}

.trader-row.you {
  background: rgba(250, 204, 21, 0.05);
}

.trader-row.exited {
  opacity: 0.7;
}

.trader-left {
  display: flex;
  align-items: center;
  gap: 10px;
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
  color: #000;
}

.trader-info {
  display: flex;
  flex-direction: column;
}

.trader-name {
  font-size: 12px;
  font-weight: 500;
}

.trader-bet {
  font-size: 10px;
  color: #6b7280;
}

.trader-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trader-exited-label {
  font-size: 10px;
  color: #6b7280;
}

.trader-profit {
  font-size: 12px;
  font-weight: 600;
  color: #ef4444;
}

.trader-profit.positive {
  color: #4ade80;
}

.trader-multiplier {
  font-size: 12px;
  font-weight: 600;
  color: #60a5fa;
}

.trader-waiting {
  font-size: 14px;
  opacity: 0.5;
}

/* Bet Section */
.bet-section {
  padding: 0 12px;
}

.bet-amounts {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.bet-btn {
  flex: 1;
  background: #1c1f2e;
  border: 2px solid transparent;
  border-radius: 10px;
  padding: 10px 8px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.bet-btn.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.15);
}

.bet-icon {
  font-size: 12px;
}

/* Action Row */
.action-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.action-btn {
  flex: 1;
  border: none;
  border-radius: 12px;
  padding: 14px 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.buy-btn {
  background: linear-gradient(135deg, #16a34a, #22c55e);
  color: #fff;
}

.sell-btn {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: #fff;
}

.sell-btn.in-loss {
  background: linear-gradient(135deg, #7f1d1d, #991b1b);
}

.profit-text {
  color: #4ade80;
  font-weight: 700;
}

.loss-text {
  color: #fca5a5;
  font-weight: 700;
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-emoji {
  font-size: 16px;
}

/* Auto-sell Row */
.autosell-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #1c1f2e;
  border-radius: 10px;
}

.autosell-label {
  font-size: 11px;
  color: #6b7280;
  white-space: nowrap;
}

.autosell-options {
  display: flex;
  gap: 6px;
  flex: 1;
  overflow-x: auto;
}

.autosell-btn {
  padding: 6px 10px;
  background: #27272a;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #9ca3af;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.autosell-btn.active {
  border-color: #facc15;
  background: rgba(250, 204, 21, 0.15);
  color: #facc15;
}

/* Game Footer */
.game-footer {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  font-size: 10px;
  color: #4b5563;
  font-family: 'SF Mono', monospace;
}
</style>
