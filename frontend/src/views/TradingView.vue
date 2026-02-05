<template>
  <div class="trading-view">
    <!-- Tournament Banner -->
    <button class="tournament-banner" @click="$router.push('/tournament')">
      <span class="banner-emoji">🏆</span>
      <span class="banner-text">Трейдинг Мега Турнир</span>
      <span class="banner-timer">{{ tournamentTimer }}</span>
    </button>

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
      <button class="balance-pill" @click="$router.push('/deposit')">
        <svg class="ton-icon" width="18" height="18" viewBox="0 0 56 56" fill="none">
          <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z" fill="#0098EA"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
        </svg>
        <span class="balance-value">{{ balance.toFixed(2) }}</span>
        <span class="balance-plus">+</span>
      </button>
    </div>

    <!-- Chart Container -->
    <div class="chart-container">
      <!-- Y-Axis Labels -->
      <div class="y-axis">
        <span>1.75</span>
        <span>1.50</span>
        <span>1.25</span>
        <span>1.00</span>
        <span>0.75</span>
      </div>

      <!-- Chart Area -->
      <div class="chart-area" ref="chartAreaRef">
        <!-- Grid Lines -->
        <div class="grid-lines">
          <div class="grid-line" style="top: 0%"></div>
          <div class="grid-line" style="top: 25%"></div>
          <div class="grid-line" style="top: 50%"></div>
          <div class="grid-line" style="top: 75%"></div>
          <div class="grid-line" style="top: 100%"></div>
        </div>

        <!-- Ping Indicator -->
        <div class="ping-indicator">
          <span class="ping-value">{{ ping }}</span>
          <span class="ping-ms">ms</span>
        </div>

        <!-- Candles Container -->
        <div class="candles-container">
          <div
            v-for="(candle, idx) in visibleCandles"
            :key="idx"
            class="candle"
            :style="getCandleStyle(candle)"
          >
            <div class="candle-wick" :style="getWickStyle(candle)"></div>
            <div class="candle-body" :style="getBodyStyle(candle)"></div>
          </div>
        </div>

        <!-- Current Price Line -->
        <div
          v-if="gameState === 'active'"
          class="price-line"
          :style="{ top: getPriceY(currentMultiplier) + '%' }"
        >
          <span class="price-label">{{ currentMultiplier.toFixed(3) }}x</span>
        </div>

        <!-- Multiplier Display -->
        <div
          class="multiplier-display"
          :class="multiplierClass"
          :style="{ top: getPriceY(currentMultiplier) + '%' }"
        >
          {{ displayMultiplier }}
        </div>

        <!-- Status Overlay -->
        <div v-if="gameState === 'countdown'" class="status-overlay">
          <span class="countdown-text">{{ countdownSeconds.toFixed(1) }}s</span>
        </div>

        <div v-if="gameState === 'crashed'" class="status-overlay crashed">
          <div class="crash-skulls">
            <span>&#128128;</span>
            <span>&#128128;</span>
            <span>&#128128;</span>
          </div>
        </div>

        <!-- Connection Status -->
        <div class="connection-status" v-if="!isConnected">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 3C7.46 3 3.34 4.78.29 7.67c-.18.18-.29.43-.29.71 0 .28.11.53.29.71.18.19.43.3.71.3s.53-.11.71-.29C4.15 6.74 7.82 5.25 12 5.25s7.85 1.49 10.29 3.85c.18.18.43.29.71.29s.53-.11.71-.3c.18-.18.29-.43.29-.71 0-.28-.11-.53-.29-.71C20.66 4.78 16.54 3 12 3zm0 5.25c-3.03 0-5.82 1.08-8 2.88-.17.14-.29.34-.33.57-.04.22.01.45.14.64.13.19.32.32.54.37.22.05.45 0 .64-.14 1.82-1.51 4.16-2.4 7.01-2.4s5.19.89 7.01 2.4c.19.14.42.19.64.14.22-.05.41-.18.54-.37.13-.19.18-.42.14-.64-.04-.23-.16-.43-.33-.57-2.18-1.8-4.97-2.88-8-2.88zm0 5.25c-1.88 0-3.63.64-5.03 1.73-.17.13-.29.32-.34.53-.05.21-.01.44.11.63s.3.33.52.39c.21.06.44.02.63-.11 1.11-.86 2.51-1.36 4.11-1.36s3 .5 4.11 1.36c.19.13.42.17.63.11.22-.06.4-.2.52-.39s.16-.42.11-.63c-.05-.21-.17-.4-.34-.53-1.4-1.09-3.15-1.73-5.03-1.73zM12 18a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/>
          </svg>
          <span>Connecting...</span>
        </div>
      </div>
    </div>

    <!-- Traders Panel -->
    <div class="traders-panel">
      <div class="traders-header">
        <span class="traders-title">Traders</span>
        <span class="traders-count">({{ traders.length }})</span>
      </div>

      <div class="traders-list" v-if="traders.length > 0">
        <div
          v-for="trader in traders"
          :key="trader.id"
          class="trader-row"
          :class="{ exited: trader.exited }"
        >
          <div class="trader-left">
            <div class="trader-level">{{ trader.level || 1 }}</div>
            <img :src="trader.avatar || '/icons/avatar-default.png'" class="trader-avatar" />
            <span class="trader-name">@{{ trader.name }}</span>
            <span v-if="trader.exited" class="trader-badge exited">Вышел</span>
          </div>
          <div class="trader-right">
            <span class="trader-profit" :class="{ positive: trader.profit >= 0, negative: trader.profit < 0 }">
              {{ trader.profit >= 0 ? '+' : '' }}{{ trader.profit.toFixed(2) }}
            </span>
            <svg width="10" height="10" viewBox="0 0 56 56" fill="currentColor">
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z"/>
            </svg>
          </div>
        </div>
      </div>

      <div class="traders-footer">
        <span class="game-number">Game #{{ gameNumber }}</span>
        <button class="hash-btn">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          <span>Hash: {{ gameHash }}</span>
        </button>
      </div>
    </div>

    <!-- Bet Pills -->
    <div class="bet-pills">
      <button
        v-for="amount in betAmounts"
        :key="amount"
        class="bet-pill"
        :class="{ active: selectedBet === amount }"
        @click="selectBet(amount)"
      >
        <svg width="12" height="12" viewBox="0 0 56 56" fill="currentColor" class="pill-icon">
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z"/>
        </svg>
        <span>{{ amount }}</span>
      </button>
      <button class="bet-pill" @click="selectBet(Math.floor(balance * 10) / 10)">
        <span>Макс</span>
      </button>
      <button class="bet-pill edit-pill">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button class="swap-btn" @click="$router.push('/swap')">
        <svg width="24" height="24" viewBox="0 0 56 56" fill="#0098EA">
          <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
        </svg>
        <span>Сменить</span>
        <span class="swap-star">⭐</span>
      </button>

      <button
        v-if="!playerBet"
        class="buy-btn"
        :disabled="!canBuy"
        @click="placeBet"
      >
        <div class="buy-text">
          <span class="buy-label">Купить</span>
          <span class="buy-amount">{{ selectedBet.toFixed(1) }} TON</span>
        </div>
      </button>

      <button
        v-else
        class="sell-btn"
        :disabled="!canSell"
        @click="cashOut"
      >
        <div class="sell-text">
          <span class="sell-label">Продать</span>
          <span class="sell-percent" :class="{ positive: currentPLPercent >= 0, negative: currentPLPercent < 0 }">
            {{ currentPLPercent >= 0 ? '+' : '' }}{{ currentPLPercent.toFixed(0) }}%
          </span>
        </div>
      </button>

      <button class="deposit-btn" @click="$router.push('/deposit')">
        <span class="deposit-plus">+</span>
        <span>Отправить</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

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
  avatar?: string
  level?: number
  exited: boolean
  profit: number
}

// Chart settings
const PRICE_MIN = 0.75
const PRICE_MAX = 1.75
const MAX_VISIBLE_CANDLES = 20

// State
const chartAreaRef = ref<HTMLElement | null>(null)
const isConnected = ref(true)
const ping = ref(76)
const gameState = ref<'waiting' | 'active' | 'crashed' | 'countdown'>('waiting')
const currentMultiplier = ref(1.0)
const countdownSeconds = ref(5)
const gameNumber = ref(36619)
const gameHash = ref('6ab3...0790')
const tournamentTimer = ref('10:13:41:30')
const showHelp = ref(false)

// Player
const balance = ref(0.66)
const selectedBet = ref(0.5)
const playerBet = ref<number | null>(null)
const betAmounts = [0.5, 1, 5, 10]

// Candles
const candles = ref<Candle[]>([])
const currentCandle = ref<Candle | null>(null)
let candleIndex = 0

// Traders
const traders = ref<Trader[]>([])

// Computed
const visibleCandles = computed(() => {
  const all = [...candles.value]
  if (currentCandle.value) {
    all.push(currentCandle.value)
  }
  return all.slice(-MAX_VISIBLE_CANDLES)
})

const displayMultiplier = computed(() => {
  if (gameState.value === 'crashed') return '0.000x'
  return currentMultiplier.value.toFixed(3) + 'x'
})

const multiplierClass = computed(() => {
  if (gameState.value === 'crashed') return 'crashed'
  if (currentMultiplier.value < 1.0) return 'negative'
  if (currentMultiplier.value >= 1.5) return 'positive'
  return ''
})

const currentPLPercent = computed(() => (currentMultiplier.value - 1) * 100)

const canBuy = computed(() => {
  return (gameState.value === 'waiting' || gameState.value === 'countdown' || gameState.value === 'active') &&
         !playerBet.value && balance.value >= selectedBet.value
})

const canSell = computed(() => gameState.value === 'active' && playerBet.value !== null)

// Methods
const getPriceY = (price: number): number => {
  const range = PRICE_MAX - PRICE_MIN
  const normalized = (price - PRICE_MIN) / range
  return (1 - normalized) * 100
}

const getCandleStyle = (candle: Candle) => {
  const totalCandles = visibleCandles.value.length
  const idx = visibleCandles.value.indexOf(candle)
  const width = 100 / Math.max(totalCandles, 10)
  const left = idx * width

  return {
    left: `${left}%`,
    width: `${width * 0.7}%`,
  }
}

const getWickStyle = (candle: Candle) => {
  const highY = getPriceY(candle.high)
  const lowY = getPriceY(candle.low)

  return {
    top: `${highY}%`,
    height: `${lowY - highY}%`,
    background: candle.close >= candle.open ? '#09D76D' : '#FB2C36',
  }
}

const getBodyStyle = (candle: Candle) => {
  const openY = getPriceY(candle.open)
  const closeY = getPriceY(candle.close)
  const top = Math.min(openY, closeY)
  const height = Math.abs(closeY - openY)

  return {
    top: `${top}%`,
    height: `${Math.max(height, 0.5)}%`,
    background: candle.close >= candle.open ? '#09D76D' : '#FB2C36',
  }
}

const selectBet = (amount: number) => {
  selectedBet.value = amount
}

const placeBet = () => {
  if (!canBuy.value) return
  playerBet.value = selectedBet.value
  balance.value -= selectedBet.value

  traders.value.push({
    id: Date.now(),
    name: 'you',
    bet: selectedBet.value,
    level: 1,
    exited: false,
    profit: 0,
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

const VOLATILITY = 0.02
const DRIFT = -0.0005
const TICKS_PER_CANDLE = 15

const startGame = () => {
  gameState.value = 'active'
  currentMultiplier.value = 1.0
  tickCount = 0
  candleIndex = 0
  candles.value = []

  currentCandle.value = {
    time: candleIndex,
    open: 1.0,
    high: 1.0,
    low: 1.0,
    close: 1.0,
  }

  // Add fake traders
  setTimeout(() => {
    if (gameState.value === 'active') {
      const names = ['whale_99', 'lucky_star', 'Kweer_gg', 'ntybe']
      traders.value.push({
        id: Date.now(),
        name: names[Math.floor(Math.random() * names.length)],
        bet: 0.5 + Math.random() * 2,
        level: Math.floor(Math.random() * 50) + 1,
        exited: false,
        profit: 0,
      })
    }
  }, 500)

  gameInterval = window.setInterval(() => {
    if (gameState.value !== 'active') return

    tickCount++

    // Price movement
    const direction = Math.random() > 0.52 ? 1 : -1
    const magnitude = Math.random() * VOLATILITY
    currentMultiplier.value = Math.max(0, currentMultiplier.value + direction * magnitude + DRIFT)

    // Update candle
    if (currentCandle.value) {
      currentCandle.value.close = currentMultiplier.value
      currentCandle.value.high = Math.max(currentCandle.value.high, currentMultiplier.value)
      currentCandle.value.low = Math.min(currentCandle.value.low, currentMultiplier.value)
    }

    // New candle
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

    // Fake trader exits
    if (Math.random() < 0.01) {
      const active = traders.value.filter(t => !t.exited && t.name !== 'you')
      if (active.length > 0) {
        const trader = active[Math.floor(Math.random() * active.length)]
        trader.exited = true
        trader.profit = trader.bet * currentMultiplier.value - trader.bet
      }
    }

    // Crash
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

  gameState.value = 'crashed'
  currentMultiplier.value = 0

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

// Tournament timer
let timerInterval: number | null = null
const updateTournamentTimer = () => {
  const parts = tournamentTimer.value.split(':').map(Number)
  let [days, hours, minutes, seconds] = parts

  seconds--
  if (seconds < 0) { seconds = 59; minutes-- }
  if (minutes < 0) { minutes = 59; hours-- }
  if (hours < 0) { hours = 23; days-- }
  if (days < 0) days = 0

  tournamentTimer.value = [days, hours, minutes, seconds]
    .map(n => n.toString().padStart(2, '0'))
    .join(':')
}

onMounted(() => {
  setTimeout(startGame, 1000)
  timerInterval = window.setInterval(updateTournamentTimer, 1000)

  // Ping simulation
  setInterval(() => {
    ping.value = Math.floor(50 + Math.random() * 80)
  }, 3000)
})

onUnmounted(() => {
  if (gameInterval) clearInterval(gameInterval)
  if (countdownInterval) clearInterval(countdownInterval)
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.trading-view {
  min-height: 100vh;
  background: #000;
  color: #fff;
  padding: 12px;
  padding-bottom: 100px;
}

/* Tournament Banner */
.tournament-banner {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #0098EA 0%, #0066CC 100%);
  border: none;
  border-radius: 20px;
  padding: 12px 20px;
  margin-bottom: 12px;
  cursor: pointer;
}

.banner-emoji {
  font-size: 20px;
}

.banner-text {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.banner-timer {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
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
  width: 44px;
  height: 44px;
  background: #1a1a1a;
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
  gap: 8px;
  background: #1a1a1a;
  border: none;
  border-radius: 20px;
  padding: 10px 14px;
  cursor: pointer;
}

.balance-value {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  font-family: ui-monospace, monospace;
}

.balance-plus {
  width: 22px;
  height: 22px;
  background: #333;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #fff;
}

/* Chart Container */
.chart-container {
  display: flex;
  background: #111;
  border: 1px solid #222;
  border-radius: 24px;
  overflow: hidden;
  margin-bottom: 12px;
  aspect-ratio: 1;
}

.y-axis {
  width: 36px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 12px 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  text-align: right;
  padding-right: 8px;
}

.chart-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.grid-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.grid-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
}

.candles-container {
  position: absolute;
  inset: 0;
  padding: 12px 8px;
}

.candle {
  position: absolute;
  bottom: 0;
  top: 0;
  display: flex;
  justify-content: center;
}

.candle-wick {
  position: absolute;
  width: 2px;
  left: 50%;
  transform: translateX(-50%);
}

.candle-body {
  position: absolute;
  width: 100%;
  border-radius: 2px;
  min-height: 2px;
}

.price-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 0;
  border-top: 2px dashed rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
}

.price-label {
  display: none;
}

.multiplier-display {
  position: absolute;
  right: 12px;
  transform: translateY(-50%);
  font-size: 20px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
  transition: top 0.1s ease-out;
}

.multiplier-display.positive {
  color: #09D76D;
}

.multiplier-display.negative {
  color: #FB2C36;
}

.multiplier-display.crashed {
  color: #FB2C36;
}

.status-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
}

.countdown-text {
  font-size: 48px;
  font-weight: 700;
  color: #0098EA;
  font-family: ui-monospace, monospace;
}

.status-overlay.crashed {
  background: rgba(0, 0, 0, 0.5);
}

.crash-skulls {
  display: flex;
  gap: 10px;
  font-size: 32px;
}

.connection-status {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.ping-indicator {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: baseline;
  gap: 2px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  z-index: 10;
}

.ping-value {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
}

.ping-ms {
  font-size: 10px;
}

/* Traders Panel */
.traders-panel {
  background: #111;
  border: 1px solid #222;
  border-radius: 20px;
  padding: 14px;
  margin-bottom: 12px;
}

.traders-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 10px;
}

.traders-title {
  font-size: 16px;
  font-weight: 700;
}

.traders-count {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
}

.traders-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
  max-height: 150px;
  overflow-y: auto;
}

.trader-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: rgba(52, 205, 239, 0.1);
  border-radius: 14px;
}

.trader-row.exited {
  background: rgba(52, 205, 239, 0.15);
}

.trader-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trader-level {
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border-radius: 5px;
  transform: rotate(45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
}

.trader-level span {
  transform: rotate(-45deg);
}

.trader-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.trader-name {
  font-size: 13px;
  font-weight: 500;
}

.trader-badge {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 500;
}

.trader-badge.exited {
  background: rgba(52, 205, 239, 0.2);
  color: #34CDEF;
}

.trader-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.trader-profit {
  font-size: 13px;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.trader-profit.positive {
  color: #09D76D;
}

.trader-profit.negative {
  color: #FB2C36;
}

.traders-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid #222;
}

.game-number {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.hash-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  cursor: pointer;
}

/* Bet Pills */
.bet-pills {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.bet-pill {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 14px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 14px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bet-pill.active {
  background: #0098EA;
  border-color: #0098EA;
}

.bet-pill .pill-icon {
  color: #0098EA;
}

.bet-pill.active .pill-icon {
  color: #fff;
}

.bet-pill.edit-pill {
  padding: 10px 12px;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

.swap-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 12px 16px;
  background: #1a1a1a;
  border: none;
  border-radius: 16px;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
}

.swap-star {
  position: absolute;
  bottom: 8px;
  right: 8px;
}

.buy-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 24px;
  background: #09D76D;
  border: none;
  border-radius: 18px;
  color: #000;
  cursor: pointer;
  transition: opacity 0.2s;
}

.buy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.buy-icon {
  color: #000;
}

.buy-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.buy-label {
  font-size: 16px;
  font-weight: 700;
}

.buy-amount {
  font-size: 12px;
  opacity: 0.7;
}

.sell-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #FB2C36 0%, #FF6B7A 100%);
  border: none;
  border-radius: 18px;
  color: #fff;
  cursor: pointer;
}

.sell-btn:disabled {
  opacity: 0.5;
}

.sell-text {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sell-label {
  font-size: 16px;
  font-weight: 700;
}

.sell-percent {
  font-size: 14px;
  font-weight: 600;
}

.sell-percent.positive {
  color: #4ade80;
}

.sell-percent.negative {
  color: #fca5a5;
}

.deposit-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 12px 16px;
  background: #1a1a1a;
  border: none;
  border-radius: 16px;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
}

.deposit-plus {
  font-size: 24px;
  font-weight: 300;
  color: #0098EA;
}
</style>
