<template>
  <div class="rocket-game">
    <!-- Stars background -->
    <div class="stars-bg">
      <div v-for="i in 40" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="game-header">
      <button class="back-btn" @click="$router.back()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="game-title">
        <span class="rocket-icon-title">🚀</span>
        <span>Rocket</span>
      </div>
      <div class="online-badge">
        <span class="online-dot"></span>
        {{ onlineCount }}
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

        <!-- Rocket emoji -->
        <div
          v-if="gameState === 'flying'"
          class="rocket-sprite"
          :style="rocketStyle"
        >
          🚀
        </div>

        <!-- Explosion -->
        <div
          v-if="gameState === 'crashed'"
          class="explosion"
          :style="explosionStyle"
        >
          💥
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
      <div class="bet-row">
        <div class="bet-input-group">
          <label>Ставка</label>
          <div class="bet-input-wrap">
            <button class="bet-adjust" @click="adjustBet(-0.1)">-</button>
            <input type="number" v-model.number="betAmount" min="0.1" step="0.1" />
            <button class="bet-adjust" @click="adjustBet(0.1)">+</button>
          </div>
          <div class="quick-bets">
            <button @click="betAmount = 0.1">0.1</button>
            <button @click="betAmount = 0.5">0.5</button>
            <button @click="betAmount = 1">1</button>
            <button @click="betAmount = 5">5</button>
          </div>
        </div>
        <div class="bet-input-group">
          <label>Авто-вывод</label>
          <div class="bet-input-wrap">
            <input type="number" v-model.number="autoCashout" min="1.1" step="0.1" placeholder="x2.00" />
          </div>
        </div>
      </div>

      <button
        :class="['action-btn', actionBtnClass]"
        @click="handleAction"
        :disabled="actionDisabled"
      >
        {{ actionBtnText }}
      </button>
    </div>

    <!-- Players -->
    <div class="players-bar">
      <div class="players-header-bar">
        <span>Игроки ({{ activeBets.length }})</span>
        <span class="total-pool">{{ totalPool.toFixed(2) }} TON</span>
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
const betAmount = ref(0.5)
const autoCashout = ref<number | null>(null)
const hasBet = ref(false)
const hasCashedOut = ref(false)
const countdown = ref(5)
const onlineCount = ref(147)
const totalPool = ref(0)
const history = ref<number[]>([2.41, 1.23, 5.67, 1.08, 3.12, 1.92, 7.84, 1.45, 2.33, 1.11])
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

const actionBtnText = computed(() => {
  if (gameState.value === 'waiting') {
    return hasBet.value ? 'Отменить ставку' : `Поставить ${betAmount.value.toFixed(2)} TON`
  }
  if (gameState.value === 'flying') {
    if (hasBet.value && !hasCashedOut.value) {
      return `Забрать ${(betAmount.value * currentMultiplier.value).toFixed(2)} TON`
    }
    return 'Ожидайте...'
  }
  return `Поставить ${betAmount.value.toFixed(2)} TON`
})

const actionDisabled = computed(() => {
  return gameState.value === 'flying' && (!hasBet.value || hasCashedOut.value)
})

function adjustBet(delta: number) {
  betAmount.value = Math.max(0.1, +(betAmount.value + delta).toFixed(2))
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

.game-header {
  display: flex; align-items: center; padding: 12px 16px;
  position: relative; z-index: 10; gap: 12px;
}
.back-btn {
  width: 36px; height: 36px; background: #1c1c1e; border: none;
  border-radius: 10px; color: #fff; display: flex; align-items: center; justify-content: center;
}
.game-title { flex: 1; font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.rocket-icon-title { font-size: 22px; }
.online-badge { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #999; }
.online-dot { width: 7px; height: 7px; background: #22c55e; border-radius: 50%; }

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
}
.trail-svg { position: absolute; inset: 0; width: 100%; height: 100%; }

.rocket-sprite {
  position: absolute; font-size: 28px; transform: translate(-50%, 50%) rotate(-45deg);
  z-index: 5; filter: drop-shadow(0 0 8px rgba(249,115,22,0.5));
}
.explosion {
  position: absolute; font-size: 48px; transform: translate(-50%, 50%);
  z-index: 5; animation: explode 0.5s ease-out;
}
@keyframes explode {
  0% { transform: translate(-50%, 50%) scale(0); opacity: 1; }
  100% { transform: translate(-50%, 50%) scale(2); opacity: 0.5; }
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
