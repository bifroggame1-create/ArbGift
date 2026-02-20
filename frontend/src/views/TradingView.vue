<template>
  <div class="trading-view">
    <!-- Header -->
    <header class="game-header-bar">
      <button class="header-back" @click="$router.push('/solo')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="header-title">
        <span class="title-main">Trading</span>
        <span class="title-badge" style="background:#ef4444">CRASH</span>
      </div>
      <div class="header-balance">
        <CurrencyIcon :currency="selectedCurrency" :size="16" />
        <span class="balance-val">{{ formatAmount(currentBalance) }}</span>
        <button class="balance-plus">+</button>
      </div>
    </header>

    <!-- Game Section: Chart + Controls -->
    <div class="game-section">
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
          <span>{{ amount }}</span>
          <CurrencyIcon :currency="selectedCurrency" :size="12" />
        </button>
        <button class="bet-pill max-pill" @click="selectedBet = Math.floor(currentBalance * 10) / 10">Макс</button>
      </div>

      <!-- Action Row -->
      <div class="action-row">
        <!-- Swap Button -->
        <button class="icon-btn" @click="handleSwap">
          <div class="icon-circle" :class="currencyClass">
            <svg v-if="selectedCurrency === 'stars'" width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
              <path d="M14.6817 5.56589C13.5404 5.2799 12.323 5.29637 11.1668 5.06113C10.8569 4.99258 10.6076 4.81476 10.445 4.55059C9.90682 3.6537 9.52714 2.64664 9.00479 1.7464C8.9006 1.57259 8.77945 1.40077 8.62717 1.26524C8.22916 0.896688 7.65323 0.917608 7.27034 1.29439C7.00813 1.54276 6.82745 1.9378 6.65204 2.28387C6.43563 2.73343 6.27029 3.14249 6.03969 3.58359C5.919 3.82462 5.79237 4.07655 5.67145 4.3178C5.46581 4.74065 5.34284 4.9552 4.92972 5.07582C4.76415 5.12812 4.58965 5.15438 4.41767 5.17775C4.15318 5.21247 3.89716 5.2483 3.61136 5.28925C2.98642 5.39185 2.37567 5.48844 1.74432 5.57434C1.44845 5.61908 1.13037 5.67494 0.886482 5.84897C0.530156 6.092 0.411305 6.55581 0.567254 6.94572C0.688625 7.26487 0.905489 7.49721 1.14731 7.7605C1.39921 8.02623 1.66966 8.29062 1.9653 8.51006C2.3072 8.77357 2.69857 8.87817 3.12267 8.91422C3.6519 8.96229 4.21134 8.93136 4.73667 8.88418C5.71634 8.79983 6.68295 8.60754 7.63857 8.393C7.85269 8.34915 8.08421 8.28862 8.29993 8.27571C8.70572 8.26036 8.37412 8.466 8.19459 8.54745C7.44369 8.88952 6.69761 9.24761 5.98267 9.64531C5.35017 9.99784 4.73392 10.3958 4.20928 10.8907C3.76479 11.2987 3.43251 11.7649 3.30175 12.3563C3.23168 12.638 3.17947 12.9195 3.1268 13.206C3.07023 13.5373 3.00108 13.901 3.06336 14.2141C3.1371 14.6606 3.58594 15.0271 4.04807 14.9984C4.27982 14.988 4.51683 14.8885 4.7369 14.7863C4.92239 14.7002 5.10788 14.6041 5.28834 14.5084C5.96114 14.1516 6.59112 13.8147 7.26828 13.4701C7.6017 13.2963 7.96902 13.1227 8.34939 13.2529C8.4742 13.2905 8.59694 13.3493 8.7151 13.4078C9.53401 13.824 10.3646 14.2206 11.1837 14.6363C11.4203 14.7574 11.666 14.8791 11.9328 14.9159C12.6525 15.0158 13.1637 14.4149 13.0588 13.7374C13.0318 13.4966 12.972 13.2474 12.9301 13.011C12.8669 12.6772 12.8193 12.3449 12.7531 12.0117C12.6624 11.5464 12.5591 11.0832 12.4865 10.6159C12.4432 10.3466 12.4405 10.0624 12.5919 9.82469C12.7441 9.57699 12.9853 9.38381 13.1882 9.17394C13.3769 8.98544 13.5701 8.7956 13.7643 8.60932C14.2253 8.15798 14.7493 7.75961 15.1677 7.27177C15.7374 6.607 15.5732 5.83139 14.6856 5.56811L14.6813 5.56678L14.6817 5.56589Z" class="fill-current transition-all"></path>
            </svg>
            <CurrencyIcon v-else :currency="'ton'" :size="14" />
          </div>
          <span class="icon-label">Сменить</span>
        </button>

        <!-- Gift Button -->
        <button class="icon-btn" @click="openGiftModal" :disabled="playerBet !== null">
          <div class="icon-circle" :class="selectedGift ? 'gift-mode' : currencyClass">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="8" width="18" height="4" rx="1"/>
              <rect x="3" y="12" width="18" height="9" rx="1"/>
              <path d="M12 8V4m0 0c0-1.1-.9-2-2-2s-2 .9-2 2h4zm0 0c0-1.1.9-2 2-2s2 .9 2 2h-4z"/>
            </svg>
          </div>
          <span class="icon-label">Гифт</span>
        </button>

        <!-- Main Action Button -->
        <button
          v-if="!playerBet"
          class="main-btn buy-btn"
          :class="selectedGift ? 'gift-mode' : currencyClass"
          :disabled="!canBuy"
          @click="placeBet"
        >
          <span class="btn-text-main">Купить</span>
          <span class="btn-text-sub" v-if="selectedGift">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="8" width="18" height="4" rx="1"/>
              <rect x="3" y="12" width="18" height="9" rx="1"/>
            </svg>
            {{ selectedGift.gift.name }}
          </span>
          <span class="btn-text-sub" v-else>
            <CurrencyIcon :currency="selectedCurrency" :size="13" />
            {{ formatAmount(selectedBet) }}
          </span>
        </button>
        <button
          v-else
          class="main-btn sell-btn"
          :class="currencyClass"
          :disabled="gameState !== 'running'"
          @click="cashOut"
        >
          <span class="btn-label">Продать</span>
          <span class="btn-percent" :class="currentPLPercent >= 0 ? 'positive' : 'negative'">
            {{ currentPLPercent >= 0 ? '+' : '' }}{{ currentPLPercent.toFixed(0) }}%
          </span>
        </button>

        <!-- Deposit Button -->
        <button class="icon-btn" @click="handleDeposit">
          <div class="icon-circle" :class="currencyClass">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </div>
          <span class="icon-label">Пополнить</span>
        </button>
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
            <div class="trader-avatar" :style="{ background: trader.photoUrl ? 'transparent' : trader.color }">
              <img v-if="trader.photoUrl" :src="trader.photoUrl" alt="" class="trader-avatar-img" />
              <span v-else>{{ trader.name.charAt(0).toUpperCase() }}</span>
            </div>
            <span class="trader-name">@{{ trader.name }}</span>
          </div>
          <div class="trader-bet">
            <CurrencyIcon :currency="selectedCurrency" :size="10" />
            {{ formatAmount(trader.bet) }}
          </div>
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

    <!-- Gift Bet Modal -->
    <GiftBetModal
      :open="showGiftModal"
      :items="inventoryItems"
      :loading="inventoryLoading"
      :server-seed-hash="gameHash"
      @close="showGiftModal = false"
      @confirm="handleGiftBet"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { createChart, CandlestickSeries, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts'
import CurrencyIcon from '../components/CurrencyIcon.vue'
import GiftBetModal from '../components/GiftBetModal.vue'
import { useCurrency } from '../composables/useCurrency'
import { useTelegram } from '../composables/useTelegram'
import {
  inventoryGetMy,
  inventoryLock,
  inventoryUnlock,
  type InventoryItem
} from '../api/client'

const { selectedCurrency, currentBalance, deductBalance, addBalance, formatAmount, toggleCurrency } = useCurrency()
const { user, hapticImpact } = useTelegram()

// Gift betting
const showGiftModal = ref(false)
const inventoryItems = ref<InventoryItem[]>([])
const inventoryLoading = ref(false)
const selectedGift = ref<InventoryItem | null>(null)

const currencyClass = computed(() => {
  return selectedCurrency.value === 'stars' ? 'stars-mode' : 'ton-mode'
})

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
  photoUrl?: string
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
const gameNumber = ref(0)
const gameHash = ref('---')
const ping = ref(0)

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
// Balance from useCurrency (no local ref)
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
  return gameState.value === 'running' && !playerBet.value && currentBalance.value >= selectedBet.value
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
    addBalance(payout)
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

    // Unlock gift on lose
    if (selectedGift.value) {
      inventoryUnlock(selectedGift.value.id).catch(() => {})
      selectedGift.value = null
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
async function placeBet() {
  if (!canBuy.value) return

  // Lock gift if betting with gift
  if (selectedGift.value) {
    try {
      await inventoryLock(selectedGift.value.id, 'trading_bet')
    } catch (error) {
      console.error('Failed to lock gift:', error)
      return
    }
  }

  playerBet.value = selectedBet.value
  if (!selectedGift.value) {
    deductBalance(selectedBet.value)
  }

  traders.value.push({
    id: Date.now(),
    name: 'you',
    bet: selectedBet.value,
    color: selectedGift.value ? '#a855f7' : '#34CDEF',
    exited: false,
    profit: 0,
    photoUrl: user.value?.photo_url || '',
  })
}

async function cashOut() {
  if (gameState.value !== 'running' || !playerBet.value) return

  const payout = playerBet.value * currentMultiplier.value
  const profit = payout - playerBet.value

  if (!selectedGift.value) {
    addBalance(payout)
  }

  const me = traders.value.find(t => t.name === 'you')
  if (me) {
    me.exited = true
    me.profit = +profit.toFixed(2)
  }

  // Unlock gift on cashout (win)
  if (selectedGift.value) {
    await inventoryUnlock(selectedGift.value.id).catch(() => {})
    selectedGift.value = null
  }

  playerBet.value = null
}

function handleSwap() {
  toggleCurrency()
  hapticImpact?.('light')
}

function handleDeposit() {
  // Navigate to deposit/top-up page
  hapticImpact?.('light')
}

// ======= Gift Betting =======
async function loadInventory() {
  try {
    inventoryLoading.value = true
    inventoryItems.value = await inventoryGetMy(true)
  } catch (error) {
    console.error('Failed to load inventory:', error)
  } finally {
    inventoryLoading.value = false
  }
}

async function handleGiftBet(item: InventoryItem) {
  selectedGift.value = item
  selectedBet.value = Number(item.current_floor_price_ton)
  showGiftModal.value = false
  hapticImpact?.('medium')
}

function openGiftModal() {
  loadInventory()
  showGiftModal.value = true
  hapticImpact?.('light')
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
  background: #0C0C0C;
  color: #fff;
  font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 15px;
  padding-bottom: 100px;
}

/* Header */
.game-header-bar { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; position: relative; z-index: 10; }
.header-back { width: 40px; height: 40px; background: #1c1c1e; border: none; border-radius: 12px; color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.header-title { display: flex; align-items: center; gap: 8px; }
.title-main { font-size: 18px; font-weight: 700; }
.title-badge { color: #000; padding: 2px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; }
.header-balance { display: flex; align-items: center; gap: 6px; background: #1c1c1e; padding: 8px 12px; border-radius: 12px; }
.balance-val { font-size: 14px; font-weight: 600; }
.balance-plus { width: 22px; height: 22px; border-radius: 50%; border: 1px solid #4b5563; background: transparent; color: #fff; font-size: 14px; display: flex; align-items: center; justify-content: center; cursor: pointer; }

/* Game Section */
.game-section {
  margin-bottom: 16px;
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
  /* Remove max-height and overflow - let parent viewport handle scrolling */
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
  overflow: hidden;
  flex-shrink: 0;
}

.trader-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.trader-avatar span {
  display: block;
}
.trader-name { font-size: 13px; }
.trader-bet { font-size: 13px; color: rgba(255, 255, 255, 0.4); }
.trader-status { display: flex; align-items: center; gap: 8px; }
.status-active { font-size: 13px; font-weight: 600; color: #34CDEF; }
.trader-profit { font-size: 13px; font-weight: 600; color: #E23535; }
.trader-profit.positive { color: #00FF62; }

/* ====== Currency Bar ====== */
.currency-bar {
  margin-bottom: 12px;
}

/* ====== Bet Controls ====== */
.bet-controls {
  margin-bottom: 12px;
  padding: 0 16px;
}

.bet-amounts {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  justify-content: space-between;
}

.bet-pill {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 20px;
  padding: 11px 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.16s ease;
  -webkit-tap-highlight-color: transparent;
  box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.05);
}

.bet-pill.active {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.bet-pill:active {
  background: rgba(255, 255, 255, 0.08);
}

.max-pill {
  background: rgba(255, 255, 255, 0.06);
}

/* Action Row */
.action-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  justify-content: space-between;
}

.icon-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  flex-shrink: 0;
}

.icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
  transition: background 0.2s;
}

.icon-btn:active .icon-circle {
  background: rgba(255, 255, 255, 0.1);
}

.icon-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
  white-space: nowrap;
}

/* Gift Mode */
.icon-circle.gift-mode {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: #fff;
}

.buy-btn.gift-mode {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  box-shadow: 0 0 24px rgba(168, 85, 247, 0.4), 0 4px 12px rgba(0, 0, 0, 0.3);
}

.buy-btn.gift-mode:not(:disabled):active {
  transform: scale(0.97);
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.5), 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Main Action Button */
.main-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 64px;
  border: none;
  border-radius: 32px;
  font-family: "SF Pro Text", -apple-system, sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
  -webkit-tap-highlight-color: transparent;
  position: relative;
}

.buy-btn {
  background: linear-gradient(90deg, #00FF62 0%, #00E056 100%);
  color: #000;
  box-shadow: 0 0 24px rgba(0, 255, 98, 0.4), 0 4px 12px rgba(0, 0, 0, 0.3);
}

.buy-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.buy-btn:not(:disabled):active {
  transform: scale(0.97);
  box-shadow: 0 0 20px rgba(0, 255, 98, 0.5), 0 2px 8px rgba(0, 0, 0, 0.3);
}

.btn-text-main {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
}

.btn-text-sub {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.8;
  margin-top: 2px;
}

.sell-btn {
  background: linear-gradient(135deg, #E23535 0%, #FF6B6B 100%);
  color: #fff;
  flex-direction: row;
  gap: 8px;
}

.sell-btn:not(:disabled):active {
  transform: scale(0.97);
}

.sell-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-label {
  font-size: 17px;
  font-weight: 600;
}

.btn-percent {
  font-size: 15px;
  font-weight: 700;
}

.btn-percent.positive { color: #a7f3d0; }
.btn-percent.negative { color: #fca5a5; }
</style>
