<template>
  <div class="trading-view">
    <!-- Tournament Banner -->
    <div class="tournament-banner" @click="$router.push('/tournament')">
      <span class="banner-emoji">&#127942;</span>
      <span class="banner-text">Trading Mega Tournament</span>
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

        <!-- Multiplier Display (only during RUNNING) -->
        <div
          v-if="gameState === 'running'"
          class="multiplier-display"
          :class="multiplierColorClass"
          :style="multiplierPosition"
        >
          <span class="multiplier-value">{{ displayMultiplier }}</span>
        </div>

        <!-- Dashed Price Line (during RUNNING) -->
        <div
          v-if="gameState === 'running'"
          class="price-line"
          :style="{ top: priceLineY + 'px' }"
        ></div>

        <!-- WAITING overlay: blurred chart + timer -->
        <div v-if="gameState === 'waiting'" class="waiting-overlay">
          <div class="waiting-timer">{{ waitingTimerText }}</div>
          <div class="waiting-sub">Game #{{ gameNumber }}</div>
        </div>

        <!-- ENDED overlay: WIN or LOSE -->
        <div v-if="gameState === 'ended'" class="ended-overlay" :class="endedClass">
          <template v-if="lastResult === 'win'">
            <div class="ended-mult win">{{ lastWinMultiplier.toFixed(2) }}x</div>
            <div class="ended-label win-label">WIN</div>
          </template>
          <template v-else>
            <div class="ended-skulls">
              <span>&#128128;</span><span>&#128128;</span><span>&#128128;</span>
            </div>
            <div class="ended-mult lose">0.00x</div>
          </template>
        </div>
      </div>
    </div>

    <!-- Recent Games Strip -->
    <div class="recent-games">
      <div class="recent-list">
        <div
          v-for="(game, idx) in recentGames"
          :key="idx"
          class="recent-item"
          :class="{ 'recent-item--win': game.isWin }"
        >
          <div class="mini-chart">
            <svg viewBox="0 0 40 24" preserveAspectRatio="none">
              <path :d="game.path" fill="none" :stroke="game.isWin ? '#00FF62' : '#E23535'" stroke-width="1.5"/>
            </svg>
          </div>
          <span class="recent-mult" :class="{ win: game.isWin }">
            {{ game.isWin ? game.mult.toFixed(2) + 'x' : '0.00x' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Traders Panel -->
    <div class="traders-panel">
      <div class="traders-header">
        <div class="traders-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <span>Traders</span>
          <span class="traders-count">({{ traders.length }})</span>
        </div>
        <div class="game-info">
          <span class="game-number-label">Game #{{ gameNumber }}</span>
          <button class="hash-btn" @click="copyHash">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            {{ gameHash }}
          </button>
        </div>
      </div>
      <div class="traders-list" v-if="traders.length > 0">
        <div v-for="trader in traders" :key="trader.id" class="trader-row" :class="{ exited: trader.exited }">
          <div class="trader-info">
            <div class="trader-avatar" :style="{ background: trader.color }">
              {{ trader.name.charAt(0).toUpperCase() }}
            </div>
            <span class="trader-name">@{{ trader.name }}</span>
          </div>
          <div class="trader-bet">{{ trader.bet.toFixed(2) }} TON</div>
          <div class="trader-status">
            <template v-if="trader.exited">
              <span class="trader-profit" :class="{ positive: trader.profit > 0 }">
                {{ trader.profit >= 0 ? '+' : '' }}{{ trader.profit.toFixed(2) }}
              </span>
            </template>
            <template v-else-if="gameState === 'running'">
              <span class="status-active">{{ currentMultiplier.toFixed(2) }}x</span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Bet Controls -->
    <div class="bet-controls">
      <!-- Bet Amount Pills -->
      <div class="bet-amounts">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          class="bet-pill"
          :class="{ active: selectedBet === amount }"
          @click="selectedBet = amount"
        >
          <svg class="pill-diamond" width="12" height="12" viewBox="0 0 56 56" fill="currentColor">
            <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z" opacity="0.3"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z"/>
          </svg>
          {{ amount }}
        </button>
        <button class="bet-pill max-pill" @click="selectedBet = Math.floor(balance * 10) / 10">Max</button>
      </div>

      <!-- Main Action Button -->
      <button
        v-if="!playerBet"
        class="main-btn buy-btn"
        :disabled="!canBuy"
        @click="placeBet"
      >
        <svg class="btn-diamond" width="18" height="18" viewBox="0 0 56 56" fill="currentColor">
          <path d="M28 56C43.464 56 56 43.464 56 28C56 12.536 43.464 0 28 0C12.536 0 0 12.536 0 28C0 43.464 12.536 56 28 56Z" opacity="0.3"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z"/>
        </svg>
        <span class="btn-label">Buy {{ selectedBet.toFixed(1) }} TON</span>
      </button>
      <button
        v-else
        class="main-btn sell-btn"
        :disabled="gameState !== 'running'"
        @click="cashOut"
      >
        <span class="btn-label">Sell</span>
        <span class="btn-percent" :class="currentPLPercent >= 0 ? 'positive' : 'negative'">
          {{ currentPLPercent >= 0 ? '+' : '' }}{{ currentPLPercent.toFixed(0) }}%
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { createChart, CandlestickSeries, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts'

// ======= Types =======
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
}

interface RecentGame {
  isWin: boolean
  mult: number
  path: string
}

type GameState = 'waiting' | 'running' | 'ended'

// ======= Chart refs =======
const chartContainerRef = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
let candleSeries: ISeriesApi<'Candlestick'> | null = null

// ======= FSM State =======
const gameState = ref<GameState>('waiting')
const currentMultiplier = ref(1.0)
const waitingCountdown = ref(5.0)
const gameNumber = ref(30772)
const gameHash = ref('2b2c...c667')
const ping = ref(73)
const tournamentTimer = ref('14:13:24:13')
const showHelp = ref(false)

// Result of current round (pre-determined)
const lastResult = ref<'win' | 'lose'>('lose')
const lastWinMultiplier = ref(1.0)
let targetCrashTick = 0  // tick at which game ends
let isWinRound = false
let winMultTarget = 1.0

// Candle tracking
let candleIndex = 0
let tickInCandle = 0
let currentCandleData: Candle | null = null

// ======= Player state =======
const balance = ref(3.66)
const selectedBet = ref(0.5)
const playerBet = ref<number | null>(null)
const betAmounts = [0.5, 1, 5, 10]

// ======= Traders =======
const traders = ref<Trader[]>([])
const FAKE_NAMES = ['vomki', 'Kweer_gg', 'lucky_star', 'whale_99', 'moon_boy', 'diamond_h', 'crypto_kid', 'degen_404']

// ======= Recent games =======
const recentGames = ref<RecentGame[]>([
  { isWin: false, mult: 0, path: genMiniPath(false) },
  { isWin: true, mult: 2.33, path: genMiniPath(true) },
  { isWin: false, mult: 0, path: genMiniPath(false) },
  { isWin: true, mult: 5.87, path: genMiniPath(true) },
  { isWin: false, mult: 0, path: genMiniPath(false) },
  { isWin: false, mult: 0, path: genMiniPath(false) },
])

// ======= Intervals =======
let gameLoopInterval: number | null = null
let waitingInterval: number | null = null
let pingInterval: number | null = null

// ======= Game config =======
const TICK_MS = 100            // ms per tick during RUNNING
const TICKS_PER_CANDLE = 12   // fewer, bigger candles
const VOLATILITY = 0.04       // bigger price moves
const DRIFT = 0.002           // slight upward bias (makes it exciting)
const WAIT_SECONDS = 4.5      // countdown duration
const ENDED_SHOW_MS = 1500    // how long to show result

// ======= Computed =======
const displayMultiplier = computed(() => currentMultiplier.value.toFixed(3) + 'x')

const multiplierColorClass = computed(() => {
  if (currentMultiplier.value >= 2) return 'mult-high'
  if (currentMultiplier.value >= 1) return 'mult-normal'
  return 'mult-negative'
})

const endedClass = computed(() => lastResult.value === 'win' ? 'ended--win' : 'ended--lose')

const waitingTimerText = computed(() => {
  const s = Math.max(0, waitingCountdown.value)
  return s.toFixed(2) + 's'
})

const currentPLPercent = computed(() => (currentMultiplier.value - 1) * 100)

const canBuy = computed(() => {
  return gameState.value === 'running' && !playerBet.value && balance.value >= selectedBet.value
})

// Price line Y position & multiplier position (track chart coordinate)
const priceLineY = ref(0)
const multiplierPosition = computed(() => {
  return {
    top: Math.max(20, priceLineY.value - 14) + 'px',
  }
})

// ======= Helpers =======
function genMiniPath(isWin: boolean): string {
  const pts: string[] = []
  let y = 12
  for (let x = 0; x <= 40; x += 4) {
    if (isWin) {
      y += (Math.random() - 0.3) * 4  // tends upward
    } else {
      y += (Math.random() - 0.6) * 5  // tends downward
      if (x >= 28) y += 2             // crash at end
    }
    y = Math.max(2, Math.min(22, y))
    pts.push(`${x},${y}`)
  }
  return `M ${pts.join(' L ')}`
}

function randomHash(): string {
  const hex = () => Math.random().toString(16).substring(2, 6)
  return hex() + '...' + hex()
}

function copyHash() {
  navigator.clipboard?.writeText(gameHash.value)
}

// ======= Chart =======
function initChart() {
  if (!chartContainerRef.value) return

  const container = chartContainerRef.value

  chart = createChart(container, {
    width: container.clientWidth,
    height: container.clientHeight,
    layout: {
      background: { type: ColorType.Solid, color: 'transparent' },
      textColor: 'rgba(255, 255, 255, 0.3)',
      fontFamily: "'SF Pro Text', -apple-system, sans-serif",
      fontSize: 10,
    },
    grid: {
      vertLines: { visible: false },
      horzLines: { color: 'rgba(255, 255, 255, 0.04)', style: 1 },
    },
    crosshair: { mode: 0 },
    rightPriceScale: { visible: false },
    leftPriceScale: {
      visible: true,
      borderVisible: false,
      scaleMargins: { top: 0.1, bottom: 0.1 },
    },
    timeScale: {
      visible: false,
      borderVisible: false,
      barSpacing: 14,
      minBarSpacing: 8,
      rightOffset: 3,
      shiftVisibleRangeOnNewBar: true,
    },
    handleScroll: false,
    handleScale: false,
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#00FF62',
    downColor: '#E23535',
    borderUpColor: '#00FF62',
    borderDownColor: '#E23535',
    wickUpColor: '#00FF62',
    wickDownColor: '#E23535',
    priceScaleId: 'left',
  })

  candleSeries.priceScale().applyOptions({
    autoScale: true,
    scaleMargins: { top: 0.1, bottom: 0.1 },
  })
}

function clearChart() {
  if (candleSeries) {
    candleSeries.setData([])
  }
}

function pushCandle(candle: Candle) {
  if (!candleSeries) return
  candleSeries.update({
    time: candle.time as any,
    open: candle.open,
    high: candle.high,
    low: candle.low,
    close: candle.close,
  })
  updatePriceLineY(candle.close)
}

function updatePriceLineY(price: number) {
  if (!chart || !candleSeries || !chartContainerRef.value) return
  try {
    const y = (candleSeries as any).priceToCoordinate(price)
    if (y !== null && typeof y === 'number' && isFinite(y)) {
      priceLineY.value = y
    }
  } catch {
    // priceToCoordinate may fail before chart is fully rendered
  }
}

// ======= Pre-determine outcome =======
function determineOutcome() {
  // ~65% loss rate
  isWinRound = Math.random() > 0.65
  if (isWinRound) {
    // Win multiplier: 1.3x - 6.0x
    winMultTarget = 1.3 + Math.random() * 4.7
    // Calculate how many ticks to reach that multiplier
    // With DRIFT of 0.002 per tick, ~650 ticks to reach 2.3x average
    // But volatility makes it faster. Target ~30-80 candles
    const totalCandles = 15 + Math.floor(Math.random() * 40)
    targetCrashTick = totalCandles * TICKS_PER_CANDLE
  } else {
    // Lose: game runs 8-30 candles then crashes to 0.00x
    const totalCandles = 8 + Math.floor(Math.random() * 22)
    targetCrashTick = totalCandles * TICKS_PER_CANDLE
    winMultTarget = 0
  }
}

// ======= Fake Traders =======
function spawnFakeTraders() {
  traders.value = []
  const count = 2 + Math.floor(Math.random() * 4)
  for (let i = 0; i < count; i++) {
    traders.value.push({
      id: Date.now() + i,
      name: FAKE_NAMES[Math.floor(Math.random() * FAKE_NAMES.length)],
      bet: +(0.1 + Math.random() * 2).toFixed(2),
      color: `hsl(${Math.random() * 360}, 60%, 50%)`,
      exited: false,
      profit: 0,
    })
  }
}

function tickFakeTraders() {
  // Occasionally a trader exits with profit
  if (Math.random() < 0.02 && gameState.value === 'running') {
    const active = traders.value.filter(t => !t.exited && t.name !== 'you')
    if (active.length > 0) {
      const t = active[Math.floor(Math.random() * active.length)]
      t.exited = true
      t.profit = +(t.bet * (currentMultiplier.value - 1)).toFixed(2)
    }
  }
  // Occasionally a new trader joins
  if (Math.random() < 0.015 && gameState.value === 'running') {
    traders.value.push({
      id: Date.now() + Math.random(),
      name: FAKE_NAMES[Math.floor(Math.random() * FAKE_NAMES.length)],
      bet: +(0.1 + Math.random() * 1.5).toFixed(2),
      color: `hsl(${Math.random() * 360}, 60%, 50%)`,
      exited: false,
      profit: 0,
    })
  }
}

// ======= FSM Transitions =======

/** WAITING → RUNNING */
function startWaiting() {
  gameState.value = 'waiting'
  waitingCountdown.value = WAIT_SECONDS
  gameNumber.value++
  gameHash.value = randomHash()

  // Pre-determine next game outcome
  determineOutcome()
  spawnFakeTraders()

  // Don't clear chart — keep previous game's chart visible (frozen/blurred)

  waitingInterval = window.setInterval(() => {
    waitingCountdown.value -= 0.05
    if (waitingCountdown.value <= 0) {
      if (waitingInterval) {
        clearInterval(waitingInterval)
        waitingInterval = null
      }
      startRunning()
    }
  }, 50)
}

/** Start the actual game */
function startRunning() {
  gameState.value = 'running'
  currentMultiplier.value = 1.0
  candleIndex = 1  // start from 1, grows right
  tickInCandle = 0
  let totalTicks = 0

  // Clear chart for new game
  clearChart()

  // Initialize first candle
  currentCandleData = {
    time: candleIndex,
    open: 1.0,
    high: 1.0,
    low: 1.0,
    close: 1.0,
  }
  pushCandle(currentCandleData)

  let momentum = 0

  gameLoopInterval = window.setInterval(() => {
    if (gameState.value !== 'running') return

    totalTicks++
    tickInCandle++

    // Check if game should end
    if (totalTicks >= targetCrashTick) {
      if (isWinRound) {
        endGameWin()
      } else {
        endGameLose()
      }
      return
    }

    // Price movement — biased based on outcome
    let direction: number
    let magnitude: number

    if (isWinRound) {
      // Win round: generally upward trend with volatility
      const progress = totalTicks / targetCrashTick
      const upBias = 0.55 + progress * 0.15  // increasingly bullish
      direction = Math.random() < upBias ? 1 : -1
      magnitude = Math.random() * VOLATILITY
      momentum = momentum * 0.9 + direction * 0.01
    } else {
      // Lose round: wobbles around then crashes
      const progress = totalTicks / targetCrashTick
      if (progress < 0.7) {
        // Early phase: random walk with slight up (teasing)
        direction = Math.random() < 0.52 ? 1 : -1
        magnitude = Math.random() * VOLATILITY * 0.8
        momentum = momentum * 0.9 + direction * 0.008
      } else {
        // Late phase: accelerating downward
        const crashProgress = (progress - 0.7) / 0.3
        direction = Math.random() < (0.3 - crashProgress * 0.25) ? 1 : -1
        magnitude = Math.random() * VOLATILITY * (1 + crashProgress * 2)
        momentum = momentum * 0.85 - 0.02 * crashProgress
      }
    }

    const priceChange = direction * magnitude + momentum * 0.5 + DRIFT
    currentMultiplier.value = Math.max(0.01, currentMultiplier.value + priceChange)

    // Update current candle
    if (currentCandleData) {
      currentCandleData.close = currentMultiplier.value
      currentCandleData.high = Math.max(currentCandleData.high, currentMultiplier.value)
      currentCandleData.low = Math.min(currentCandleData.low, currentMultiplier.value)
      pushCandle(currentCandleData)
    }

    // New candle every TICKS_PER_CANDLE
    if (tickInCandle >= TICKS_PER_CANDLE) {
      candleIndex++
      tickInCandle = 0
      currentCandleData = {
        time: candleIndex,
        open: currentMultiplier.value,
        high: currentMultiplier.value,
        low: currentMultiplier.value,
        close: currentMultiplier.value,
      }
      pushCandle(currentCandleData)
    }

    // Fake trader activity
    tickFakeTraders()
  }, TICK_MS)
}

/** End game with WIN */
function endGameWin() {
  if (gameLoopInterval) {
    clearInterval(gameLoopInterval)
    gameLoopInterval = null
  }

  // Snap multiplier to target
  currentMultiplier.value = winMultTarget
  lastResult.value = 'win'
  lastWinMultiplier.value = winMultTarget

  // Final candle update
  if (currentCandleData) {
    currentCandleData.close = winMultTarget
    currentCandleData.high = Math.max(currentCandleData.high, winMultTarget)
    pushCandle(currentCandleData)
  }

  // Player payout
  if (playerBet.value) {
    const payout = playerBet.value * winMultTarget
    balance.value += payout
    const me = traders.value.find(t => t.name === 'you')
    if (me) {
      me.exited = true
      me.profit = +(payout - me.bet).toFixed(2)
    }
    playerBet.value = null
  }

  // Update recent games
  recentGames.value.unshift({ isWin: true, mult: winMultTarget, path: genMiniPath(true) })
  recentGames.value = recentGames.value.slice(0, 6)

  gameState.value = 'ended'
  setTimeout(startWaiting, ENDED_SHOW_MS)
}

/** End game with LOSE (crash to 0.00x) */
function endGameLose() {
  if (gameLoopInterval) {
    clearInterval(gameLoopInterval)
    gameLoopInterval = null
  }

  lastResult.value = 'lose'
  currentMultiplier.value = 0

  // Crash candle to 0
  if (currentCandleData && candleSeries) {
    currentCandleData.close = 0
    currentCandleData.low = 0
    pushCandle(currentCandleData)
  }

  // Liquidate player
  if (playerBet.value) {
    const me = traders.value.find(t => t.name === 'you')
    if (me) {
      me.exited = true
      me.profit = -me.bet
    }
    playerBet.value = null
  }

  // Update recent games
  recentGames.value.unshift({ isWin: false, mult: 0, path: genMiniPath(false) })
  recentGames.value = recentGames.value.slice(0, 6)

  gameState.value = 'ended'
  setTimeout(startWaiting, ENDED_SHOW_MS)
}

// ======= Player Actions =======
function placeBet() {
  if (!canBuy.value) return
  playerBet.value = selectedBet.value
  balance.value -= selectedBet.value

  traders.value.push({
    id: Date.now(),
    name: 'you',
    bet: selectedBet.value,
    color: '#34CDEF',
    exited: false,
    profit: 0,
  })
}

function cashOut() {
  if (gameState.value !== 'running' || !playerBet.value) return

  const payout = playerBet.value * currentMultiplier.value
  const profit = payout - playerBet.value
  balance.value += payout

  const me = traders.value.find(t => t.name === 'you')
  if (me) {
    me.exited = true
    me.profit = +profit.toFixed(2)
  }

  playerBet.value = null
}

// ======= Lifecycle =======
onMounted(() => {
  nextTick(() => {
    initChart()
  })

  // Ping simulation
  pingInterval = window.setInterval(() => {
    ping.value = Math.floor(50 + Math.random() * 80)
  }, 3000)

  // Start first game after short delay
  setTimeout(startWaiting, 800)

  // Resize handler
  const resizeObserver = new ResizeObserver(() => {
    if (chart && chartContainerRef.value) {
      chart.applyOptions({
        width: chartContainerRef.value.clientWidth,
        height: chartContainerRef.value.clientHeight,
      })
    }
  })

  if (chartContainerRef.value) {
    resizeObserver.observe(chartContainerRef.value)
  }
})

onUnmounted(() => {
  if (gameLoopInterval) clearInterval(gameLoopInterval)
  if (waitingInterval) clearInterval(waitingInterval)
  if (pingInterval) clearInterval(pingInterval)
  if (chart) {
    chart.remove()
    chart = null
  }
})
</script>

<style scoped>
/* === Trading View — myballs.io style === */

.trading-view {
  min-height: 100vh;
  background: #0C0C0C;
  color: #fff;
  font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 15px;
  padding-bottom: 100px;
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
.banner-emoji { font-size: 18px; }
.banner-text { font-size: 14px; font-weight: 600; }
.banner-timer { font-size: 14px; font-weight: 600; font-family: ui-monospace, monospace; }

/* Top Bar */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.top-left { display: flex; gap: 8px; }
.icon-btn {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.05);
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
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 16px;
  cursor: pointer;
}
.ton-icon { width: 16px; height: 16px; }
.balance-value { font-size: 14px; font-weight: 600; font-family: ui-monospace, monospace; }
.balance-add {
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #fff;
}

/* ====== Chart ====== */
.chart-wrapper {
  width: 100%;
  aspect-ratio: 1;
  margin-bottom: 12px;
}
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0E0F14;
  border: 2px solid #191919;
  border-radius: 32px;
  overflow: hidden;
}

/* Ping */
.ping-indicator {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* Dashed Price Line */
.price-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  z-index: 15;
  pointer-events: none;
  background-image: repeating-linear-gradient(
    to right,
    rgba(255, 255, 255, 0.5) 0px,
    rgba(255, 255, 255, 0.5) 6px,
    transparent 6px,
    transparent 12px
  );
  transition: top 0.08s linear;
}

/* Multiplier (RUNNING) — follows price line */
.multiplier-display {
  position: absolute;
  right: 16px;
  z-index: 20;
  pointer-events: none;
  transition: top 0.08s linear;
}
.multiplier-value {
  font-size: 28px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.6);
}
.mult-normal .multiplier-value { color: #fff; }
.mult-high .multiplier-value { color: #00FF62; }
.mult-negative .multiplier-value { color: #E23535; }

/* WAITING Overlay */
.waiting-overlay {
  position: absolute;
  inset: 0;
  z-index: 25;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(14, 15, 20, 0.75);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
.waiting-timer {
  font-size: 56px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  color: #34CDEF;
  line-height: 1;
  margin-bottom: 8px;
}
.waiting-sub {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

/* ENDED Overlay */
.ended-overlay {
  position: absolute;
  inset: 0;
  z-index: 25;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ended--win {
  background: rgba(0, 255, 98, 0.08);
}
.ended--lose {
  background: rgba(226, 53, 53, 0.08);
}
.ended-mult {
  font-size: 56px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  line-height: 1;
}
.ended-mult.win { color: #00FF62; }
.ended-mult.lose { color: #E23535; }
.ended-label {
  font-size: 18px;
  font-weight: 600;
  margin-top: 4px;
}
.win-label { color: #00FF62; }
.ended-skulls {
  display: flex;
  gap: 12px;
  font-size: 32px;
  margin-bottom: 8px;
  animation: skullShake 0.5s ease-in-out;
}

@keyframes skullShake {
  0%, 100% { transform: translateY(0) rotate(0); }
  20% { transform: translateY(-6px) rotate(-5deg); }
  40% { transform: translateY(0) rotate(5deg); }
  60% { transform: translateY(-3px) rotate(-3deg); }
  80% { transform: translateY(0) rotate(2deg); }
}

/* ====== Recent Games ====== */
.recent-games {
  margin-bottom: 12px;
}
.recent-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}
.recent-list::-webkit-scrollbar { display: none; }
.recent-item {
  flex-shrink: 0;
  width: 56px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
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
.recent-mult {
  font-size: 11px;
  font-weight: 600;
  color: #E23535;
  font-family: ui-monospace, monospace;
}
.recent-mult.win {
  color: #00FF62;
}

/* ====== Traders Panel ====== */
.traders-panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 12px;
}
.traders-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.traders-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
}
.traders-title svg { color: rgba(255, 255, 255, 0.5); }
.traders-count { color: rgba(255, 255, 255, 0.4); font-weight: 400; }
.game-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.game-number-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}
.hash-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
  cursor: pointer;
}
.traders-list {
  max-height: 140px;
  overflow-y: auto;
}
.trader-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.trader-row.exited {
  background: rgba(0, 255, 98, 0.04);
}
.trader-info { display: flex; align-items: center; gap: 10px; }
.trader-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #000;
}
.trader-name { font-size: 13px; }
.trader-bet { font-size: 13px; color: rgba(255, 255, 255, 0.4); }
.trader-status { display: flex; align-items: center; gap: 8px; }
.status-active { font-size: 13px; font-weight: 600; color: #34CDEF; }
.trader-profit { font-size: 13px; font-weight: 600; color: #E23535; }
.trader-profit.positive { color: #00FF62; }

/* ====== Bet Controls ====== */
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
  background: rgba(255, 255, 255, 0.08);
  border: none;
  border-radius: 16px;
  padding: 10px 14px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.16s ease;
  -webkit-tap-highlight-color: transparent;
}
.bet-pill.active {
  background: #34CDEF;
  color: #000;
}
.bet-pill:hover:not(.active) {
  background: rgba(255, 255, 255, 0.12);
}
.pill-diamond { width: 14px; height: 14px; color: #34CDEF; }
.bet-pill.active .pill-diamond { color: #000; }
.max-pill { background: rgba(255, 255, 255, 0.08); }

/* Main Action Button — DOMINANT */
.main-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  min-height: 56px;
  border: none;
  border-radius: 20px;
  font-family: "SF Pro Text", -apple-system, sans-serif;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
  -webkit-tap-highlight-color: transparent;
}
.buy-btn {
  background: #34CDEF;
  color: #000;
}
.buy-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.buy-btn:not(:disabled):active {
  transform: scale(0.97);
  background: #2ab8d6;
}
.btn-diamond { color: #000; }
.btn-label {
  font-size: 17px;
  font-weight: 600;
}
.sell-btn {
  background: linear-gradient(135deg, #E23535 0%, #FF6B6B 100%);
  color: #fff;
}
.sell-btn:not(:disabled):active {
  transform: scale(0.97);
}
.sell-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn-percent {
  font-size: 15px;
  margin-left: 4px;
  font-weight: 700;
}
.btn-percent.positive { color: #a7f3d0; }
.btn-percent.negative { color: #fca5a5; }
</style>
