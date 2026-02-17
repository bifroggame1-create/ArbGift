<template>
  <div class="rocket-game">
    <!-- Stars background -->
    <div class="stars-bg">
      <div v-for="i in 40" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="game-header-bar">
      <button class="header-back" @click="$router.push('/solo')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="header-title">
        <span class="title-main">Rocket</span>
        <span class="title-badge" style="background:#f59e0b">x100</span>
      </div>
      <div class="header-balance">
        <CurrencyIcon :currency="selectedCurrency" :size="16" />
        <span class="balance-val">{{ formatAmount(currentBalance) }}</span>
        <button class="balance-plus">+</button>
      </div>
    </header>

    <!-- History bar -->
    <div class="history-bar">
      <div
        v-for="(h, i) in history"
        :key="i"
        :class="['history-item', h >= 2 ? 'green' : 'red']"
      >
        {{ h.toFixed(2) }}x
      </div>
    </div>

    <!-- Game Area -->
    <div class="game-area">
      <div class="rocket-canvas">
        <!-- Trail path -->
        <svg class="trail-svg" viewBox="0 0 300 300" preserveAspectRatio="none">
          <defs>
            <linearGradient id="trailGrad" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0%" stop-color="transparent"/>
              <stop offset="100%" :stop-color="gameState === 'crashed' ? '#ef4444' : '#22c55e'"/>
            </linearGradient>
          </defs>
          <path
            v-if="gameState !== 'waiting'"
            :d="trailPath"
            fill="none"
            stroke="url(#trailGrad)"
            stroke-width="3"
            stroke-linecap="round"
          />
          <path
            v-if="gameState !== 'waiting'"
            :d="trailFillPath"
            :fill="gameState === 'crashed' ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)'"
          />
        </svg>

        <!-- Rocket model -->
        <div
          v-if="gameState === 'flying'"
          class="rocket-sprite"
          :style="rocketStyle"
        >
          <TgsPlayer :src="rocketModelSrc" :size="64" :loop="true" />
        </div>

        <!-- Explosion -->
        <div
          v-if="gameState === 'crashed'"
          class="explosion"
          :style="explosionStyle"
        >
          <TgsPlayer :src="rocketModelSrc" :size="72" :loop="false" :autoplay="false" />
        </div>

        <!-- Multiplier display -->
        <div class="multiplier-display">
          <div v-if="gameState === 'waiting'" class="waiting-text">
            <span class="waiting-label">Ожидание...</span>
            <span class="waiting-timer">{{ countdown.toFixed(1) }}s</span>
          </div>
          <div v-else-if="gameState === 'flying'" class="flying-multiplier">
            {{ currentMultiplier.toFixed(2) }}x
          </div>
          <div v-else class="crashed-multiplier">
            <span class="crash-label">CRASHED</span>
            <span class="crash-value">{{ crashPoint.toFixed(2) }}x</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bet Panel -->
    <div class="bet-panel">
      <!-- Bet Amount Pills -->
      <div class="bet-amounts">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          class="bet-pill"
          :class="{ active: betAmount === amount }"
          @click="betAmount = amount"
          :disabled="gameState === 'flying'"
        >
          <span>{{ amount }}</span>
          <CurrencyIcon :currency="selectedCurrency" :size="12" />
        </button>
        <button class="bet-pill max-pill" @click="betAmount = Math.floor(currentBalance * 10) / 10" :disabled="gameState === 'flying'">Макс</button>
      </div>

      <!-- Auto-cashout -->
      <div class="auto-cashout-row">
        <label>Авто-вывод</label>
        <div class="bet-input-wrap">
          <input type="number" v-model.number="autoCashout" min="1.1" step="0.1" placeholder="x2.00" />
        </div>
      </div>

      <!-- Action Row -->
      <div class="action-row-new">
        <button class="icon-btn" @click="handleSwap">
          <div class="icon-circle" :class="currencyClass">
            <svg v-if="selectedCurrency === 'stars'" width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
              <path d="M14.6817 5.56589C13.5404 5.2799 12.323 5.29637 11.1668 5.06113C10.8569 4.99258 10.6076 4.81476 10.445 4.55059C9.90682 3.6537 9.52714 2.64664 9.00479 1.7464C8.9006 1.57259 8.77945 1.40077 8.62717 1.26524C8.22916 0.896688 7.65323 0.917608 7.27034 1.29439C7.00813 1.54276 6.82745 1.9378 6.65204 2.28387C6.43563 2.73343 6.27029 3.14249 6.03969 3.58359C5.919 3.82462 5.79237 4.07655 5.67145 4.3178C5.46581 4.74065 5.34284 4.9552 4.92972 5.07582C4.76415 5.12812 4.58965 5.15438 4.41767 5.17775C4.15318 5.21247 3.89716 5.2483 3.61136 5.28925C2.98642 5.39185 2.37567 5.48844 1.74432 5.57434C1.44845 5.61908 1.13037 5.67494 0.886482 5.84897C0.530156 6.092 0.411305 6.55581 0.567254 6.94572C0.688625 7.26487 0.905489 7.49721 1.14731 7.7605C1.39921 8.02623 1.66966 8.29062 1.9653 8.51006C2.3072 8.77357 2.69857 8.87817 3.12267 8.91422C3.6519 8.96229 4.21134 8.93136 4.73667 8.88418C5.71634 8.79983 6.68295 8.60754 7.63857 8.393C7.85269 8.34915 8.08421 8.28862 8.29993 8.27571C8.70572 8.26036 8.37412 8.466 8.19459 8.54745C7.44369 8.88952 6.69761 9.24761 5.98267 9.64531C5.35017 9.99784 4.73392 10.3958 4.20928 10.8907C3.76479 11.2987 3.43251 11.7649 3.30175 12.3563C3.23168 12.638 3.17947 12.9195 3.1268 13.206C3.07023 13.5373 3.00108 13.901 3.06336 14.2141C3.1371 14.6606 3.58594 15.0271 4.04807 14.9984C4.27982 14.988 4.51683 14.8885 4.7369 14.7863C4.92239 14.7002 5.10788 14.6041 5.28834 14.5084C5.96114 14.1516 6.59112 13.8147 7.26828 13.4701C7.6017 13.2963 7.96902 13.1227 8.34939 13.2529C8.4742 13.2905 8.59694 13.3493 8.7151 13.4078C9.53401 13.824 10.3646 14.2206 11.1837 14.6363C11.4203 14.7574 11.666 14.8791 11.9328 14.9159C12.6525 15.0158 13.1637 14.4149 13.0588 13.7374C13.0318 13.4966 12.972 13.2474 12.9301 13.011C12.8669 12.6772 12.8193 12.3449 12.7531 12.0117C12.6624 11.5464 12.5591 11.0832 12.4865 10.6159C12.4432 10.3466 12.4405 10.0624 12.5919 9.82469C12.7441 9.57699 12.9853 9.38381 13.1882 9.17394C13.3769 8.98544 13.5701 8.7956 13.7643 8.60932C14.2253 8.15798 14.7493 7.75961 15.1677 7.27177C15.7374 6.607 15.5732 5.83139 14.6856 5.56811L14.6813 5.56678L14.6817 5.56589Z" class="fill-current transition-all"></path>
            </svg>
            <CurrencyIcon v-else :currency="'ton'" :size="14" />
          </div>
          <span class="icon-label">Сменить</span>
        </button>

        <button
          :class="['main-btn', 'play-btn-new', currencyClass, actionBtnClass]"
          @click="handleAction"
          :disabled="actionDisabled"
        >
          <span class="btn-text-main">{{ actionBtnTextMain }}</span>
          <span class="btn-text-sub" v-if="gameState === 'waiting' && !hasBet">
            <CurrencyIcon :currency="selectedCurrency" :size="13" />
            {{ formatAmount(betAmount) }}
          </span>
          <span class="btn-text-sub" v-else-if="gameState === 'flying' && hasBet && !hasCashedOut">
            <CurrencyIcon :currency="selectedCurrency" :size="13" />
            {{ formatAmount(betAmount * currentMultiplier) }}
          </span>
          <span class="btn-text-sub" v-else-if="gameState === 'flying'">...</span>
          <span class="btn-text-sub" v-else-if="gameState === 'crashed'">
            <CurrencyIcon :currency="selectedCurrency" :size="13" />
            {{ formatAmount(betAmount) }}
          </span>
        </button>

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

      <!-- Hash Line -->
      <div class="hash-line"></div>
    </div>

    <!-- Players -->
    <div class="players-bar">
      <div class="players-header-bar">
        <span>Игроки ({{ activeBets.length }})</span>
        <span class="total-pool">
          <CurrencyIcon :currency="selectedCurrency" :size="10" />
          {{ formatAmount(totalPool) }}
        </span>
      </div>
      <div class="players-list">
        <div v-for="bet in activeBets" :key="bet.id" class="player-row">
          <span class="p-name">{{ bet.username }}</span>
          <span class="p-bet">{{ bet.amount.toFixed(2) }}</span>
          <span v-if="bet.cashedOut" class="p-cashout green">{{ bet.cashoutAt?.toFixed(2) }}x</span>
          <span v-else-if="gameState === 'crashed'" class="p-cashout red">-</span>
          <span v-else class="p-cashout waiting">...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import CurrencyIcon from '../components/CurrencyIcon.vue'
import TgsPlayer from '../components/TgsPlayer.vue'
import { useCurrency } from '../composables/useCurrency'

const { selectedCurrency, currentBalance, formatAmount, toggleCurrency } = useCurrency()

const ROCKET_MODELS_COUNT = 50
const rocketModelIndex = ref(0)
const rocketModelSrc = computed(() => `/images/rocket-models/${rocketModelIndex.value}.tgs`)

interface ActiveBet {
  id: number
  username: string
  amount: number
  cashedOut: boolean
  cashoutAt?: number
}

// State
const gameState = ref<'waiting' | 'flying' | 'crashed'>('waiting')
const currentMultiplier = ref(1.00)
const crashPoint = ref(0)

const betAmounts = computed(() => {
  return selectedCurrency.value === 'stars'
    ? [150, 500, 1000, 5000, 10000]
    : [1, 3, 10, 30, 50]
})

const currencyClass = computed(() => {
  return selectedCurrency.value === 'stars' ? 'stars-mode' : 'ton-mode'
})

const betAmount = ref(1)
const autoCashout = ref<number | null>(null)
const hasBet = ref(false)
const hasCashedOut = ref(false)
const countdown = ref(5)
const onlineCount = ref(0)
const totalPool = ref(0)
const history = ref<number[]>([])
const trailProgress = ref(0)
const lastRocketX = ref(150)
const lastRocketY = ref(280)
const activeBets = ref<ActiveBet[]>([])

const trailPath = computed(() => {
  const points: string[] = []
  const steps = Math.floor(trailProgress.value * 50)
  for (let i = 0; i <= steps; i++) {
    const t = i / 50
    const x = t * 280 + 10
    const y = 280 - (Math.pow(t, 0.7) * 260)
    points.push(i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`)
  }
  return points.join(' ')
})

const trailFillPath = computed(() => {
  const steps = Math.floor(trailProgress.value * 50)
  if (steps < 1) return ''
  let path = ''
  for (let i = 0; i <= steps; i++) {
    const t = i / 50
    const x = t * 280 + 10
    const y = 280 - (Math.pow(t, 0.7) * 260)
    path += i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`
  }
  const lastT = steps / 50
  const lastX = lastT * 280 + 10
  path += ` L ${lastX} 290 L 10 290 Z`
  return path
})

const rocketStyle = computed(() => {
  const t = trailProgress.value
  const x = t * 280 + 10
  const y = 280 - (Math.pow(t, 0.7) * 260)
  lastRocketX.value = x
  lastRocketY.value = y
  return {
    left: `${(x / 300) * 100}%`,
    bottom: `${((300 - y) / 300) * 100}%`,
  }
})

const explosionStyle = computed(() => ({
  left: `${(lastRocketX.value / 300) * 100}%`,
  bottom: `${((300 - lastRocketY.value) / 300) * 100}%`,
}))

const actionBtnClass = computed(() => {
  if (gameState.value === 'waiting') return hasBet.value ? 'cancel' : 'bet'
  if (gameState.value === 'flying') return hasBet.value && !hasCashedOut.value ? 'cashout' : 'disabled'
  return 'bet'
})

const actionBtnTextMain = computed(() => {
  if (gameState.value === 'waiting') {
    return hasBet.value ? 'Отменить' : 'Играть'
  }
  if (gameState.value === 'flying') {
    if (hasBet.value && !hasCashedOut.value) {
      return 'Забрать'
    }
    return 'Ожидайте'
  }
  return 'Играть'
})

const actionDisabled = computed(() => {
  return gameState.value === 'flying' && (!hasBet.value || hasCashedOut.value)
})

function handleSwap() {
  toggleCurrency()
}

function handleDeposit() {
  // Navigate to deposit/top-up page
}

function handleAction() {
  if (gameState.value === 'waiting') {
    hasBet.value = !hasBet.value
  } else if (gameState.value === 'flying' && hasBet.value && !hasCashedOut.value) {
    hasCashedOut.value = true
    const playerBet = activeBets.value.find(b => b.id === 99)
    if (playerBet) {
      playerBet.cashedOut = true
      playerBet.cashoutAt = currentMultiplier.value
    }
  } else if (gameState.value === 'crashed') {
    hasBet.value = true
  }
}

function getStarStyle(_i: number) {
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    width: `${Math.random() * 2 + 1}px`,
    height: `${Math.random() * 2 + 1}px`,
    animationDelay: `${Math.random() * 3}s`,
    animationDuration: `${Math.random() * 2 + 2}s`
  }
}

function generateCrashPoint(): number {
  const e = Math.random()
  const houseEdge = 0.03
  return Math.min(Math.max(1.0, (1 - houseEdge) / (1 - e)), 100)
}

function generateFakeBets(): ActiveBet[] {
  const names = ['CryptoKing', 'TonMaster', 'DegenBoy', 'Player42', 'LuckyGirl', 'BigBet', 'SmallFish', 'WhaleAlert']
  const count = Math.floor(Math.random() * 5) + 3
  const bets: ActiveBet[] = []
  let pool = 0
  for (let i = 0; i < count; i++) {
    const amount = +(Math.random() * 5 + 0.1).toFixed(2)
    pool += amount
    bets.push({ id: i, username: names[i % names.length], amount, cashedOut: false })
  }
  totalPool.value = pool
  return bets
}

let gameInterval: number | null = null
let countdownInterval: number | null = null

function startGameCycle() {
  gameState.value = 'waiting'
  currentMultiplier.value = 1.00
  trailProgress.value = 0
  hasCashedOut.value = false
  countdown.value = 5
  rocketModelIndex.value = (rocketModelIndex.value + 1) % ROCKET_MODELS_COUNT
  activeBets.value = generateFakeBets()

  if (hasBet.value) {
    activeBets.value.push({ id: 99, username: 'Ты', amount: betAmount.value, cashedOut: false })
    totalPool.value += betAmount.value
  }

  countdownInterval = window.setInterval(() => {
    countdown.value -= 0.1
    if (countdown.value <= 0) {
      clearInterval(countdownInterval!)
      startFlight()
    }
  }, 100)
}

function startFlight() {
  gameState.value = 'flying'
  crashPoint.value = generateCrashPoint()
  const startTime = Date.now()

  gameInterval = window.setInterval(() => {
    const elapsed = (Date.now() - startTime) / 1000
    currentMultiplier.value = Math.pow(Math.E, 0.06 * elapsed)
    trailProgress.value = Math.min(1, elapsed / 20)

    // Bot auto-cashouts
    for (const bet of activeBets.value) {
      if (!bet.cashedOut && bet.id !== 99) {
        const autoCash = 1.1 + Math.random() * (crashPoint.value - 1.1) * 0.8
        if (currentMultiplier.value >= autoCash) {
          bet.cashedOut = true
          bet.cashoutAt = currentMultiplier.value
        }
      }
    }

    // Player auto-cashout
    if (hasBet.value && !hasCashedOut.value && autoCashout.value && currentMultiplier.value >= autoCashout.value) {
      hasCashedOut.value = true
      const playerBet = activeBets.value.find(b => b.id === 99)
      if (playerBet) {
        playerBet.cashedOut = true
        playerBet.cashoutAt = currentMultiplier.value
      }
    }

    if (currentMultiplier.value >= crashPoint.value) {
      clearInterval(gameInterval!)
      gameState.value = 'crashed'
      currentMultiplier.value = crashPoint.value
      history.value.unshift(crashPoint.value)
      if (history.value.length > 10) history.value.pop()
      setTimeout(() => { hasBet.value = false; startGameCycle() }, 3000)
    }
  }, 50)
}

let onlineInterval: number | null = null

onMounted(() => {
  startGameCycle()
  onlineInterval = window.setInterval(() => {
    onlineCount.value = Math.floor(Math.random() * 50) + 120
  }, 5000)
})

onUnmounted(() => {
  if (gameInterval) clearInterval(gameInterval)
  if (countdownInterval) clearInterval(countdownInterval)
  if (onlineInterval) clearInterval(onlineInterval)
})
</script>

<style scoped>
.rocket-game {
  min-height: 100vh;
  background: #000;
  color: #fff;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 90px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
}

.stars-bg { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
.star {
  position: absolute; background: #fff; border-radius: 50%; opacity: 0.3;
  animation: twinkle 3s infinite ease-in-out;
}
@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.3); }
}

.game-header-bar { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; position: relative; z-index: 10; }
.header-back { width: 40px; height: 40px; background: #1c1c1e; border: none; border-radius: 12px; color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.header-title { display: flex; align-items: center; gap: 8px; }
.title-main { font-size: 18px; font-weight: 700; }
.title-badge { color: #000; padding: 2px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; }
.header-balance { display: flex; align-items: center; gap: 6px; background: #1c1c1e; padding: 8px 12px; border-radius: 12px; }
.balance-val { font-size: 14px; font-weight: 600; }
.balance-plus { width: 22px; height: 22px; border-radius: 50%; border: 1px solid #4b5563; background: transparent; color: #fff; font-size: 14px; display: flex; align-items: center; justify-content: center; cursor: pointer; }

.history-bar {
  display: flex; gap: 6px; padding: 8px 16px; overflow-x: auto;
  position: relative; z-index: 10; -webkit-overflow-scrolling: touch;
}
.history-item { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; white-space: nowrap; flex-shrink: 0; }
.history-item.green { background: rgba(34,197,94,0.15); color: #22c55e; }
.history-item.red { background: rgba(239,68,68,0.15); color: #ef4444; }

.game-area { position: relative; z-index: 10; padding: 0 16px; margin-bottom: 16px; }
.rocket-canvas {
  position: relative; width: 100%; aspect-ratio: 1; max-height: 280px;
  background: #0a0a0a; border-radius: 16px; border: 1px solid #1c1c1e; overflow: hidden;
  touch-action: pan-y;
}
.trail-svg { position: absolute; inset: 0; width: 100%; height: 100%; }

.rocket-sprite {
  position: absolute; transform: translate(-50%, 50%) rotate(-45deg);
  z-index: 5; filter: drop-shadow(0 0 12px rgba(249,115,22,0.6));
  width: 64px; height: 64px;
}
.explosion {
  position: absolute; transform: translate(-50%, 50%);
  z-index: 5; animation: explode 0.5s ease-out;
  width: 72px; height: 72px; opacity: 0.5;
}
@keyframes explode {
  0% { transform: translate(-50%, 50%) scale(0); opacity: 1; }
  100% { transform: translate(-50%, 50%) scale(2); opacity: 0.3; }
}

.multiplier-display {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  text-align: center; z-index: 10;
}
.waiting-text { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.waiting-label { font-size: 14px; color: #666; }
.waiting-timer { font-size: 32px; font-weight: 700; color: #eab308; }
.flying-multiplier { font-size: 48px; font-weight: 800; color: #22c55e; text-shadow: 0 0 20px rgba(34,197,94,0.5); }
.crashed-multiplier { display: flex; flex-direction: column; align-items: center; }
.crash-label { font-size: 14px; color: #ef4444; font-weight: 700; letter-spacing: 2px; }
.crash-value { font-size: 48px; font-weight: 800; color: #ef4444; text-shadow: 0 0 20px rgba(239,68,68,0.5); }

.bet-panel { padding: 0 16px; margin-bottom: 16px; position: relative; z-index: 10; }

/* Bet Controls */
.bet-amounts {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  margin-bottom: 12px;
}

.bet-amounts::-webkit-scrollbar {
  display: none;
}

.bet-pill {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bet-pill:active {
  transform: scale(0.95);
}

.bet-pill:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bet-pill.active {
  background: rgba(139, 92, 246, 0.2);
  border-color: #8b5cf6;
  color: #8b5cf6;
}

.max-pill {
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.3);
  color: #8b5cf6;
}

/* Auto-cashout row */
.auto-cashout-row {
  margin-bottom: 12px;
}

.auto-cashout-row label {
  display: block;
  font-size: 11px;
  color: #666;
  margin-bottom: 6px;
}

/* Action Row */
.action-row-new {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.icon-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s ease;
}

.icon-btn:active {
  transform: scale(0.95);
}

.icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.icon-circle.stars-mode {
  background: rgba(255, 193, 7, 0.15);
  color: #FFC107;
}

.icon-circle.ton-mode {
  background: rgba(52, 205, 239, 0.15);
  color: #34CDEF;
}

.icon-label {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
}

.main-btn {
  flex: 1;
  padding: 14px 20px;
  border-radius: 16px;
  border: none;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.main-btn:active {
  transform: scale(0.98);
}

.main-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.play-btn-new.stars-mode {
  background: linear-gradient(135deg, #FFB800 0%, #FF8C00 100%);
  color: #000;
  box-shadow: 0 0 24px rgba(255, 184, 0, 0.4);
}

.play-btn-new.ton-mode {
  background: linear-gradient(135deg, #34CDEF 0%, #0EA5E9 100%);
  color: #000;
  box-shadow: 0 0 24px rgba(52, 205, 239, 0.4);
}

.play-btn-new.cancel {
  background: #ef4444;
  color: #fff;
}

.play-btn-new.cashout {
  background: #eab308;
  color: #000;
  animation: pulseBtn 0.5s ease-in-out infinite alternate;
}

.play-btn-new.disabled {
  background: #2c2c2e;
  color: #666;
  cursor: not-allowed;
}

.btn-text-main {
  font-size: 17px;
  font-weight: 700;
  line-height: 1;
}

.btn-text-sub {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.8;
  line-height: 1;
}

/* Hash Line */
.hash-line {
  width: 100%;
  height: 1px;
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.1) 0px,
    rgba(255, 255, 255, 0.1) 4px,
    transparent 4px,
    transparent 8px
  );
  margin-top: 4px;
}

/* Old styles - keep for compatibility */
.bet-row { display: flex; gap: 10px; margin-bottom: 10px; }
.bet-input-group { flex: 1; }
.bet-input-group label { display: block; font-size: 11px; color: #666; margin-bottom: 6px; }
.bet-input-wrap {
  display: flex; background: #1c1c1e; border-radius: 10px; overflow: hidden; border: 1px solid #2c2c2e;
}
.bet-input-wrap input {
  flex: 1; background: transparent; border: none; color: #fff; padding: 10px;
  font-size: 15px; font-weight: 600; text-align: center; outline: none; width: 0;
}
.bet-adjust {
  width: 36px; background: #2c2c2e; border: none; color: #fff; font-size: 18px; font-weight: 600; cursor: pointer;
}
.quick-bets { display: flex; gap: 4px; margin-top: 6px; }
.quick-bets button {
  flex: 1; background: #1c1c1e; border: 1px solid #2c2c2e; border-radius: 6px;
  color: #999; padding: 4px; font-size: 11px; cursor: pointer;
}

.action-btn {
  width: 100%; padding: 16px; border: none; border-radius: 14px;
  font-size: 16px; font-weight: 700; cursor: pointer; transition: all 0.2s;
}
.action-btn.bet { background: #22c55e; color: #fff; }
.action-btn.cancel { background: #ef4444; color: #fff; }
.action-btn.cashout { background: #eab308; color: #000; animation: pulseBtn 0.5s ease-in-out infinite alternate; }
@keyframes pulseBtn {
  from { transform: scale(1); }
  to { transform: scale(1.02); box-shadow: 0 0 20px rgba(234,179,8,0.3); }
}
.action-btn.disabled, .action-btn:disabled { background: #2c2c2e; color: #666; cursor: not-allowed; }

.players-bar { padding: 0 16px; position: relative; z-index: 10; }
.players-header-bar { display: flex; justify-content: space-between; font-size: 13px; color: #999; margin-bottom: 8px; }
.total-pool { color: #22c55e; font-weight: 600; }
.players-list { background: #1c1c1e; border-radius: 12px; overflow: hidden; }
.player-row {
  display: flex; align-items: center; padding: 10px 12px;
  border-bottom: 1px solid #2c2c2e; font-size: 13px;
}
.player-row:last-child { border-bottom: none; }
.p-name { flex: 1; font-weight: 500; }
.p-bet { width: 60px; text-align: right; color: #999; margin-right: 12px; }
.p-cashout { width: 60px; text-align: right; font-weight: 600; }
.p-cashout.green { color: #22c55e; }
.p-cashout.red { color: #ef4444; }
.p-cashout.waiting { color: #666; }
</style>
