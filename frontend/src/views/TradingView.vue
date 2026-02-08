<template>
  <div class="trading-view">
    <!-- Tournament Banner -->
    <button class="tournament-banner" @click="$router.push('/tournament')">
      <span class="banner-emoji">🏆</span>
      <span class="banner-text">Trading Mega Tournament</span>
      <span class="banner-timer">{{ tournamentTimer }}</span>
    </button>

    <!-- Top Bar -->
    <div class="top-bar">
      <div class="top-left">
        <button class="icon-btn" @click="$router.push('/history?sorting=solo_trading')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </button>
        <button class="icon-btn" @click="showHelp = true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
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
        <span v-for="n in 7" :key="n">{{ 8 - n }}</span>
      </div>

      <!-- Chart Area -->
      <div class="chart-area">
        <!-- Grid Lines -->
        <div class="grid-lines">
          <div v-for="n in 7" :key="n" class="grid-line" :style="{ top: ((n - 1) / 6) * 100 + '%' }"></div>
        </div>

        <!-- Candles -->
        <div class="candles-wrapper">
          <div
            v-for="(candle, idx) in visibleCandles"
            :key="idx"
            class="candle"
            :style="getCandleStyle(candle, idx)"
          >
            <div class="wick" :style="getWickStyle(candle)"></div>
            <div class="body" :style="getBodyStyle(candle)"></div>
          </div>
        </div>

        <!-- Price Line -->
        <div
          v-if="gameState === 'active'"
          class="price-line"
          :style="{ top: priceToY(currentMultiplier) + '%' }"
        ></div>

        <!-- Multiplier -->
        <div
          class="multiplier"
          :class="multiplierClass"
          :style="{ top: priceToY(currentMultiplier) + '%' }"
        >
          {{ displayMultiplier }}
        </div>

        <!-- Connection Status -->
        <div class="connection-status" v-if="gameState === 'waiting'">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" opacity="0.6">
            <path d="M12 3C7.46 3 3.34 4.78.29 7.67c-.18.18-.29.43-.29.71s.11.53.29.71c.4.39 1.02.39 1.42 0C4.08 6.74 7.82 5.25 12 5.25s7.92 1.49 10.29 3.84c.4.39 1.02.39 1.42 0 .18-.18.29-.43.29-.71s-.11-.53-.29-.71C20.66 4.78 16.54 3 12 3zm0 5.25c-2.34 0-4.54.79-6.36 2.13-.21.16-.34.41-.34.68s.12.51.33.67c.43.33 1.03.25 1.37-.17C8.33 10.46 10.06 10 12 10s3.67.46 4.99 1.56c.33.42.93.5 1.37.17.21-.16.33-.4.33-.67s-.13-.52-.34-.68C16.54 9.04 14.34 8.25 12 8.25zm0 5.25c-1.12 0-2.17.4-3.04 1.05-.25.19-.39.48-.37.78.02.3.19.57.45.73.42.25.96.15 1.27-.24.47-.38 1.05-.57 1.69-.57s1.22.19 1.69.57c.31.39.85.49 1.27.24.26-.16.43-.43.45-.73.02-.3-.12-.59-.37-.78-.87-.65-1.92-1.05-3.04-1.05zM12 18c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z"/>
          </svg>
          <span>Connecting...</span>
        </div>

        <!-- Countdown -->
        <div v-if="gameState === 'countdown'" class="countdown-overlay">
          <span class="countdown-text">{{ countdownSeconds.toFixed(1) }}s</span>
        </div>

        <!-- Crash -->
        <div v-if="gameState === 'crashed'" class="crash-overlay">
          <div class="crash-icons">💀💀💀</div>
        </div>
      </div>
    </div>

    <!-- Traders Panel -->
    <div class="traders-panel">
      <div class="traders-header">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" opacity="0.6">
          <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
        <span class="traders-title">Traders</span>
        <span class="traders-count">({{ traders.length }})</span>
      </div>

      <div class="traders-list" v-if="traders.length > 0">
        <div
          v-for="trader in traders"
          :key="trader.id"
          class="trader-item"
          :class="{ exited: trader.exited }"
        >
          <div class="trader-info">
            <div class="trader-level">{{ trader.level }}</div>
            <div class="trader-avatar" :style="{ background: trader.color }">
              {{ trader.name.charAt(0).toUpperCase() }}
            </div>
            <span class="trader-name">@{{ trader.name }}</span>
            <span v-if="trader.exited" class="trader-status">{{ trader.profit >= 0 ? trader.exitMult?.toFixed(2) + 'x' : '' }}</span>
          </div>
          <div class="trader-profit" :class="{ positive: trader.profit >= 0, negative: trader.profit < 0 }">
            <span>{{ trader.profit >= 0 ? '+' : '' }}{{ trader.profit.toFixed(2) }}</span>
            <svg width="10" height="10" viewBox="0 0 56 56" fill="currentColor">
              <path d="M37.56 15.63H18.44c-3.52 0-5.75 3.79-4 6.86l11.8 20.45c.77 1.34 2.7 1.34 3.47 0l11.84-20.45c1.77-3.06-.45-6.86-3.99-6.86z"/>
            </svg>
          </div>
        </div>
      </div>

      <div class="traders-footer">
        <span class="game-id">Game #{{ gameNumber }}</span>
        <button class="hash-btn">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          <span>Hash: {{ gameHash }}</span>
        </button>
      </div>
    </div>

    <!-- Bet Pills -->
    <div class="bet-pills">
      <button
        v-for="amt in [0.5, 1, 5, 10]"
        :key="amt"
        class="bet-pill"
        :class="{ active: selectedBet === amt }"
        @click="selectedBet = amt"
      >
        <svg width="12" height="12" viewBox="0 0 56 56" fill="currentColor" class="pill-ton">
          <path d="M37.56 15.63H18.44c-3.52 0-5.75 3.79-4 6.86l11.8 20.45c.77 1.34 2.7 1.34 3.47 0l11.84-20.45c1.77-3.06-.45-6.86-3.99-6.86z"/>
        </svg>
        <span>{{ amt }}</span>
      </button>
      <button class="bet-pill" @click="selectedBet = Math.floor(balance * 10) / 10">
        <span>Max</span>
      </button>
      <button class="bet-pill bet-pill-edit">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>
    </div>

    <!-- Action Buttons -->
    <div class="action-row">
      <button class="action-btn swap-btn" @click="$router.push('/swap')">
        <svg width="24" height="24" viewBox="0 0 56 56" fill="#0098EA">
          <circle cx="28" cy="28" r="28"/>
          <path d="M37.56 15.63H18.44c-3.52 0-5.75 3.79-4 6.86l11.8 20.45c.77 1.34 2.7 1.34 3.47 0l11.84-20.45c1.77-3.06-.45-6.86-3.99-6.86z" fill="white"/>
        </svg>
        <span class="action-label">Swap</span>
        <span class="swap-star">⭐</span>
      </button>

      <button
        v-if="!playerBet"
        class="main-btn buy-btn"
        :disabled="!canBuy"
        @click="placeBet"
      >
        <svg width="16" height="16" viewBox="0 0 56 56" fill="currentColor" class="btn-icon">
          <path d="M37.56 15.63H18.44c-3.52 0-5.75 3.79-4 6.86l11.8 20.45c.77 1.34 2.7 1.34 3.47 0l11.84-20.45c1.77-3.06-.45-6.86-3.99-6.86z"/>
        </svg>
        <div class="btn-content">
          <span class="btn-label">Buy</span>
          <span class="btn-amount">{{ selectedBet }} TON</span>
        </div>
      </button>

      <button
        v-else
        class="main-btn sell-btn"
        :disabled="!canSell"
        @click="cashOut"
      >
        <div class="btn-content">
          <span class="btn-label">Sell</span>
          <span class="btn-percent">{{ currentPLPercent >= 0 ? '+' : '' }}{{ currentPLPercent.toFixed(0) }}%</span>
        </div>
      </button>

      <button class="action-btn deposit-btn" @click="$router.push('/deposit')">
        <div class="deposit-icon">+</div>
        <span class="action-label">Deposit</span>
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
  color: string
  level: number
  exited: boolean
  profit: number
  exitMult?: number
}

// Chart config
const PRICE_MIN = 1
const PRICE_MAX = 7
const MAX_CANDLES = 25

// State
const gameState = ref<'waiting' | 'active' | 'crashed' | 'countdown'>('waiting')
const currentMultiplier = ref(1.0)
const countdownSeconds = ref(5.0)
const gameNumber = ref(36637)
const gameHash = ref('33a4...faa6')
const tournamentTimer = ref('10:13:30:00')
const showHelp = ref(false)

// Player
const balance = ref(0.66)
const selectedBet = ref(0.5)
const playerBet = ref<number | null>(null)

// Chart
const candles = ref<Candle[]>([])
const currentCandle = ref<Candle | null>(null)
let candleIdx = 0

// Traders
const traders = ref<Trader[]>([])

// Computed
const visibleCandles = computed(() => {
  const all = [...candles.value]
  if (currentCandle.value) all.push(currentCandle.value)
  return all.slice(-MAX_CANDLES)
})

const displayMultiplier = computed(() => {
  if (gameState.value === 'crashed') return '0.000x'
  return currentMultiplier.value.toFixed(3) + 'x'
})

const multiplierClass = computed(() => {
  if (gameState.value === 'crashed') return 'crashed'
  if (currentMultiplier.value >= 2) return 'high'
  if (currentMultiplier.value < 1) return 'low'
  return ''
})

const currentPLPercent = computed(() => (currentMultiplier.value - 1) * 100)
const canBuy = computed(() => ['waiting', 'countdown', 'active'].includes(gameState.value) && !playerBet.value && balance.value >= selectedBet.value)
const canSell = computed(() => gameState.value === 'active' && playerBet.value !== null)

// Methods
const priceToY = (price: number): number => {
  const clamped = Math.max(PRICE_MIN, Math.min(PRICE_MAX, price))
  return ((PRICE_MAX - clamped) / (PRICE_MAX - PRICE_MIN)) * 100
}

const getCandleStyle = (_candle: Candle, idx: number) => {
  const total = visibleCandles.value.length
  const w = 100 / Math.max(total, 15)
  return {
    left: `${idx * w}%`,
    width: `${w * 0.7}%`
  }
}

const getWickStyle = (candle: Candle) => ({
  top: `${priceToY(candle.high)}%`,
  height: `${priceToY(candle.low) - priceToY(candle.high)}%`,
  background: candle.close >= candle.open ? '#09D76D' : '#FB2C36'
})

const getBodyStyle = (candle: Candle) => {
  const openY = priceToY(candle.open)
  const closeY = priceToY(candle.close)
  return {
    top: `${Math.min(openY, closeY)}%`,
    height: `${Math.max(Math.abs(closeY - openY), 1)}%`,
    background: candle.close >= candle.open ? '#09D76D' : '#FB2C36'
  }
}

const placeBet = () => {
  if (!canBuy.value) return
  playerBet.value = selectedBet.value
  balance.value -= selectedBet.value
  traders.value.push({
    id: Date.now(),
    name: 'you',
    bet: selectedBet.value,
    color: '#0098EA',
    level: 1,
    exited: false,
    profit: 0
  })
}

const cashOut = () => {
  if (!canSell.value || !playerBet.value) return
  const payout = playerBet.value * currentMultiplier.value
  balance.value += payout
  const me = traders.value.find(t => t.name === 'you')
  if (me) {
    me.exited = true
    me.profit = payout - playerBet.value
    me.exitMult = currentMultiplier.value
  }
  playerBet.value = null
}

// Game loop
let gameLoop: number | null = null
let countdownLoop: number | null = null
let tick = 0

const startGame = () => {
  gameState.value = 'active'
  currentMultiplier.value = 1.0
  tick = 0
  candleIdx = 0
  candles.value = []
  currentCandle.value = { time: 0, open: 1, high: 1, low: 1, close: 1 }

  // Fake traders
  setTimeout(() => {
    if (gameState.value === 'active') {
      const names = ['whale_99', 'Kweer_gg', 'ntybe', 'lucky_star']
      traders.value.push({
        id: Date.now(),
        name: names[Math.floor(Math.random() * names.length)],
        bet: +(0.3 + Math.random() * 2).toFixed(1),
        color: `hsl(${Math.random() * 360}, 60%, 50%)`,
        level: Math.floor(Math.random() * 50) + 1,
        exited: false,
        profit: 0
      })
    }
  }, 300)

  gameLoop = window.setInterval(() => {
    if (gameState.value !== 'active') return
    tick++

    // Price movement
    const dir = Math.random() > 0.48 ? 1 : -1
    const mag = Math.random() * 0.08
    currentMultiplier.value = Math.max(0, currentMultiplier.value + dir * mag - 0.002)

    if (currentCandle.value) {
      currentCandle.value.close = currentMultiplier.value
      currentCandle.value.high = Math.max(currentCandle.value.high, currentMultiplier.value)
      currentCandle.value.low = Math.min(currentCandle.value.low, currentMultiplier.value)
    }

    // New candle every 12 ticks
    if (tick % 12 === 0) {
      if (currentCandle.value) candles.value.push({ ...currentCandle.value })
      candleIdx++
      currentCandle.value = {
        time: candleIdx,
        open: currentMultiplier.value,
        high: currentMultiplier.value,
        low: currentMultiplier.value,
        close: currentMultiplier.value
      }
    }

    // Fake exits
    if (Math.random() < 0.008) {
      const active = traders.value.filter(t => !t.exited && t.name !== 'you')
      if (active.length) {
        const t = active[Math.floor(Math.random() * active.length)]
        t.exited = true
        t.profit = t.bet * currentMultiplier.value - t.bet
        t.exitMult = currentMultiplier.value
      }
    }

    if (currentMultiplier.value <= 0.001) crash()
  }, 60)
}

const crash = () => {
  if (gameLoop) clearInterval(gameLoop)
  gameState.value = 'crashed'
  currentMultiplier.value = 0
  if (playerBet.value) {
    const me = traders.value.find(t => t.name === 'you')
    if (me) { me.exited = true; me.profit = -me.bet }
    playerBet.value = null
  }
  setTimeout(startCountdown, 2500)
}

const startCountdown = () => {
  gameState.value = 'countdown'
  countdownSeconds.value = 5
  gameNumber.value++
  gameHash.value = Math.random().toString(36).slice(2, 6) + '...' + Math.random().toString(36).slice(2, 6)
  traders.value = []
  candles.value = []

  countdownLoop = window.setInterval(() => {
    countdownSeconds.value -= 0.05
    if (countdownSeconds.value <= 0) {
      if (countdownLoop) clearInterval(countdownLoop)
      startGame()
    }
  }, 50)
}

// Timer
let timerLoop: number | null = null
const updateTimer = () => {
  const [d, h, m, s] = tournamentTimer.value.split(':').map(Number)
  let sec = s - 1, min = m, hr = h, day = d
  if (sec < 0) { sec = 59; min-- }
  if (min < 0) { min = 59; hr-- }
  if (hr < 0) { hr = 23; day-- }
  if (day < 0) day = 0
  tournamentTimer.value = [day, hr, min, sec].map(n => String(n).padStart(2, '0')).join(':')
}

onMounted(() => {
  setTimeout(startGame, 800)
  timerLoop = window.setInterval(updateTimer, 1000)
})

onUnmounted(() => {
  if (gameLoop) clearInterval(gameLoop)
  if (countdownLoop) clearInterval(countdownLoop)
  if (timerLoop) clearInterval(timerLoop)
})
</script>

<style scoped>
.trading-view {
  min-height: 100vh;
  background: #000;
  padding: 12px;
  padding-bottom: 100px;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
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
.banner-emoji { font-size: 18px; }
.banner-text { font-size: 14px; font-weight: 600; color: #fff; }
.banner-timer { font-size: 14px; font-weight: 600; color: #fff; font-family: ui-monospace, monospace; }

/* Top Bar */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.top-left { display: flex; gap: 8px; }
.icon-btn {
  width: 44px;
  height: 44px;
  background: #1C1C1E;
  border: none;
  border-radius: 14px;
  color: rgba(255,255,255,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.balance-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1C1C1E;
  border: none;
  border-radius: 20px;
  padding: 10px 12px 10px 14px;
  cursor: pointer;
}
.balance-value { font-size: 15px; font-weight: 600; color: #fff; font-family: ui-monospace, monospace; }
.balance-plus {
  width: 22px;
  height: 22px;
  background: #333;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 300;
  color: #fff;
}

/* Chart */
.chart-container {
  display: flex;
  background: #0E0F14;
  border: 1px solid #191919;
  border-radius: 24px;
  overflow: hidden;
  margin-bottom: 12px;
  aspect-ratio: 1;
}
.y-axis {
  width: 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  text-align: right;
  padding-right: 6px;
}
.chart-area {
  flex: 1;
  position: relative;
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
  background: rgba(255,255,255,0.06);
}
.candles-wrapper {
  position: absolute;
  inset: 8px;
}
.candle {
  position: absolute;
  top: 0;
  bottom: 0;
}
.wick {
  position: absolute;
  width: 2px;
  left: 50%;
  transform: translateX(-50%);
}
.body {
  position: absolute;
  width: 100%;
  border-radius: 1px;
  min-height: 2px;
}
.price-line {
  position: absolute;
  left: 0;
  right: 0;
  border-top: 2px dashed rgba(255,255,255,0.4);
  pointer-events: none;
}
.multiplier {
  position: absolute;
  right: 12px;
  transform: translateY(-50%);
  font-size: 20px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0,0,0,0.8);
  transition: top 0.08s linear;
}
.multiplier.high { color: #09D76D; }
.multiplier.low { color: #FB2C36; }
.multiplier.crashed { color: #FB2C36; }

.connection-status {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}
.countdown-overlay, .crash-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.6);
}
.countdown-text {
  font-size: 48px;
  font-weight: 700;
  color: #0098EA;
  font-family: ui-monospace, monospace;
}
.crash-icons { font-size: 32px; }

/* Traders Panel */
.traders-panel {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 14px;
  margin-bottom: 12px;
}
.traders-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.traders-title { font-size: 15px; font-weight: 600; }
.traders-count { font-size: 15px; color: rgba(255,255,255,0.5); }
.traders-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 120px;
  overflow-y: auto;
  margin-bottom: 10px;
}
.trader-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(52,205,239,0.1);
  border-radius: 14px;
}
.trader-item.exited { background: rgba(52,205,239,0.15); }
.trader-info { display: flex; align-items: center; gap: 8px; }
.trader-level {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 4px;
  transform: rotate(45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
}
.trader-level span { transform: rotate(-45deg); }
.trader-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #000;
}
.trader-name { font-size: 13px; font-weight: 500; }
.trader-status {
  padding: 2px 6px;
  background: rgba(52,205,239,0.2);
  border-radius: 6px;
  font-size: 10px;
  color: #34CDEF;
}
.trader-profit {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}
.trader-profit.positive { color: #09D76D; }
.trader-profit.negative { color: #FB2C36; }
.traders-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.game-id { font-size: 12px; color: rgba(255,255,255,0.5); }
.hash-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  font-size: 12px;
  cursor: pointer;
}

/* Bet Pills */
.bet-pills {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.bet-pill {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 14px;
  background: #1C1C1E;
  border: 1px solid #333;
  border-radius: 14px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.bet-pill.active {
  background: #0098EA;
  border-color: #0098EA;
}
.bet-pill .pill-ton { color: #0098EA; }
.bet-pill.active .pill-ton { color: #fff; }
.bet-pill-edit { padding: 10px 12px; }

/* Action Row */
.action-row {
  display: flex;
  gap: 8px;
  align-items: stretch;
}
.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 60px;
  padding: 10px 8px;
  background: #1C1C1E;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  position: relative;
}
.action-label { font-size: 11px; color: #fff; }
.swap-star {
  position: absolute;
  bottom: 6px;
  right: 6px;
  font-size: 10px;
}
.deposit-icon {
  font-size: 24px;
  font-weight: 300;
  color: #0098EA;
  line-height: 1;
}

.main-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 20px;
  border: none;
  border-radius: 18px;
  cursor: pointer;
  transition: opacity 0.15s;
}
.main-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.buy-btn {
  background: #09D76D;
  color: #000;
}
.buy-btn .btn-icon { color: rgba(0,0,0,0.3); }
.sell-btn {
  background: linear-gradient(135deg, #FB2C36, #FF6B7A);
  color: #fff;
}
.btn-content { display: flex; flex-direction: column; align-items: flex-start; }
.btn-label { font-size: 16px; font-weight: 700; }
.btn-amount { font-size: 12px; opacity: 0.7; }
.btn-percent { font-size: 14px; font-weight: 600; }
</style>
