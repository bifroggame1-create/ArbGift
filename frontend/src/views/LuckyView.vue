<template>
  <div class="lucky-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 25" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="lucky-header">
      <button class="header-back" @click="$router.push('/solo')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="header-title">
        <span class="title-main">Lucky</span>
        <span class="title-badge hot">HOT</span>
      </div>
      <div class="header-balance">
        <svg class="balance-icon-svg" width="16" height="16" viewBox="0 0 56 56" fill="none">
          <circle cx="28" cy="28" r="28" fill="#0098EA"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
        </svg>
        <span class="balance-value">{{ balance.toFixed(2) }}</span>
        <button class="balance-add">+</button>
      </div>
    </header>

    <!-- Game Info -->
    <div class="game-info-bar">
      <div class="info-chip">
        <span class="chip-label">ИГРА</span>
        <span class="chip-value">#{{ gameNumber }}</span>
      </div>
      <div class="info-chip">
        <span class="chip-dot"></span>
        <span class="chip-value">{{ onlineCount }} онлайн</span>
      </div>
      <div class="info-chip hash">
        <span class="chip-value">{{ currentHash }}</span>
        <button class="copy-btn">📋</button>
      </div>
    </div>

    <!-- Lucky Wheel -->
    <div class="wheel-container">
      <!-- Pointer -->
      <div class="wheel-pointer">
        <svg width="30" height="36" viewBox="0 0 30 36" fill="#fff">
          <path d="M15 36L0 8h30L15 36z"/>
        </svg>
      </div>

      <!-- Wheel -->
      <div
        class="lucky-wheel"
        :class="{ spinning: isSpinning }"
        :style="{ transform: `rotate(${wheelRotation}deg)` }"
      >
        <div
          v-for="(segment, i) in segments"
          :key="i"
          class="wheel-segment"
          :style="getSegmentStyle(i)"
        >
          <span class="segment-label">{{ segment.label }}</span>
        </div>
        <div class="wheel-center">
          <span v-if="!isSpinning">{{ gameStatus }}</span>
          <span v-else class="spinning-text">🎰</span>
        </div>
      </div>

      <!-- Glow Effect -->
      <div class="wheel-glow" :class="{ active: isSpinning }"></div>
    </div>

    <!-- Result Display -->
    <div v-if="showResult" class="result-display" :class="resultClass">
      <div class="result-content">
        <span class="result-multiplier">{{ lastResult.multiplier }}x</span>
        <span class="result-amount" :class="{ win: lastResult.win > 0 }">
          {{ lastResult.win > 0 ? '+' : '' }}{{ lastResult.win.toFixed(2) }} TON
        </span>
      </div>
    </div>

    <!-- History Strip -->
    <div class="history-strip">
      <div
        v-for="(item, i) in history.slice(0, 15)"
        :key="i"
        :class="['history-dot', getColorClass(item.color)]"
        :title="`${item.multiplier}x`"
      ></div>
    </div>

    <!-- Color Betting -->
    <div class="betting-section">
      <div class="section-title">Выберите цвет</div>

      <div class="color-buttons">
        <button
          v-for="color in colors"
          :key="color.name"
          :class="['color-btn', color.class, { selected: selectedColor === color.name }]"
          @click="selectedColor = color.name"
          :disabled="isSpinning"
        >
          <span class="color-mult">{{ color.multiplier }}x</span>
          <span class="color-name">{{ color.label }}</span>
        </button>
      </div>

      <!-- Bet Amount -->
      <div class="bet-row">
        <div class="bet-amounts">
          <button
            v-for="amount in betAmounts"
            :key="amount"
            :class="['bet-btn', { active: selectedBet === amount }]"
            @click="selectedBet = amount"
            :disabled="isSpinning"
          >
            {{ amount }}
          </button>
        </div>
        <div class="custom-bet">
          <input
            type="number"
            v-model.number="customBet"
            placeholder="Сумма"
            class="bet-input"
            :disabled="isSpinning"
          />
          <span class="input-suffix">TON</span>
        </div>
      </div>

      <!-- Play Button -->
      <button
        class="btn-play"
        :disabled="!selectedColor || isSpinning || balance < effectiveBet"
        @click="spin"
      >
        <span v-if="isSpinning" class="spinner"></span>
        <span v-else>🎰 Крутить за {{ effectiveBet }} TON</span>
      </button>
    </div>

    <!-- Stats Panel -->
    <div class="stats-panel">
      <div class="stat-box">
        <span class="stat-label">Всего ставок</span>
        <span class="stat-value">{{ totalBets }}</span>
      </div>
      <div class="stat-box">
        <span class="stat-label">Выиграно</span>
        <span class="stat-value win">{{ totalWon.toFixed(2) }} TON</span>
      </div>
      <div class="stat-box">
        <span class="stat-label">Удача</span>
        <span class="stat-value">{{ luckPercentage }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Segment {
  color: string
  label: string
  multiplier: number
}

interface HistoryItem {
  color: string
  multiplier: number
  win: number
}

// Wheel segments - Rolls.codes style
const segments = ref<Segment[]>([
  { color: 'green', label: '50x', multiplier: 50 },
  { color: 'blue', label: '3x', multiplier: 3 },
  { color: 'yellow', label: '2x', multiplier: 2 },
  { color: 'pink', label: '5x', multiplier: 5 },
  { color: 'blue', label: '3x', multiplier: 3 },
  { color: 'yellow', label: '2x', multiplier: 2 },
  { color: 'purple', label: '10x', multiplier: 10 },
  { color: 'blue', label: '3x', multiplier: 3 },
  { color: 'yellow', label: '2x', multiplier: 2 },
  { color: 'pink', label: '5x', multiplier: 5 },
  { color: 'blue', label: '3x', multiplier: 3 },
  { color: 'yellow', label: '2x', multiplier: 2 },
])

// Color options
const colors = [
  { name: 'yellow', label: 'Жёлтый', multiplier: 2, class: 'yellow' },
  { name: 'blue', label: 'Синий', multiplier: 3, class: 'blue' },
  { name: 'pink', label: 'Розовый', multiplier: 5, class: 'pink' },
  { name: 'purple', label: 'Фиолет', multiplier: 10, class: 'purple' },
  { name: 'green', label: 'Зелёный', multiplier: 50, class: 'green' },
]

// State
const balance = ref(4.16)
const gameNumber = ref(89432)
const onlineCount = ref(156)
const currentHash = ref('a7d2...8f1c')
const isSpinning = ref(false)
const wheelRotation = ref(0)
const gameStatus = ref('КРУТИ')
const showResult = ref(false)

const selectedColor = ref<string | null>(null)
const selectedBet = ref(1)
const customBet = ref<number | null>(null)
const betAmounts = [0.5, 1, 2, 5, 10]

const history = ref<HistoryItem[]>([
  { color: 'yellow', multiplier: 2, win: 1 },
  { color: 'blue', multiplier: 3, win: 2 },
  { color: 'yellow', multiplier: 2, win: -1 },
  { color: 'pink', multiplier: 5, win: 4 },
  { color: 'yellow', multiplier: 2, win: 1 },
])

const lastResult = ref({ multiplier: 0, win: 0, color: '' })
const totalBets = ref(24)
const totalWon = ref(12.5)

const effectiveBet = computed(() => customBet.value || selectedBet.value)

const luckPercentage = computed(() => {
  if (totalBets.value === 0) return 0
  const wins = history.value.filter(h => h.win > 0).length
  return Math.round((wins / Math.min(history.value.length, 10)) * 100)
})

const resultClass = computed(() => {
  return lastResult.value.win > 0 ? 'win' : 'lose'
})

// Stars background
const getStarStyle = (_i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

// Wheel segment style
const getSegmentStyle = (index: number) => {
  const segmentAngle = 360 / segments.value.length
  const rotation = segmentAngle * index
  const segment = segments.value[index]

  const colorMap: Record<string, string> = {
    green: '#22c55e',
    blue: '#3b82f6',
    yellow: '#eab308',
    pink: '#ec4899',
    purple: '#8b5cf6',
  }

  return {
    transform: `rotate(${rotation}deg)`,
    background: colorMap[segment.color] || '#6b7280',
  }
}

const getColorClass = (color: string) => color

// Spin logic
const spin = async () => {
  if (!selectedColor.value || isSpinning.value || balance.value < effectiveBet.value) return

  isSpinning.value = true
  showResult.value = false
  balance.value -= effectiveBet.value
  gameNumber.value++
  totalBets.value++

  gameStatus.value = '🎰'

  // Weighted random - house edge
  const rand = Math.random()
  let winningColor = 'yellow'
  let winningMultiplier = 2

  if (rand < 0.4) {
    winningColor = 'yellow'
    winningMultiplier = 2
  } else if (rand < 0.7) {
    winningColor = 'blue'
    winningMultiplier = 3
  } else if (rand < 0.85) {
    winningColor = 'pink'
    winningMultiplier = 5
  } else if (rand < 0.95) {
    winningColor = 'purple'
    winningMultiplier = 10
  } else {
    winningColor = 'green'
    winningMultiplier = 50
  }

  // Find segment index for this color
  const segmentIndex = segments.value.findIndex(s => s.color === winningColor)
  const segmentAngle = 360 / segments.value.length

  // Calculate rotation to land on this segment
  const baseRotation = 360 * 5 // 5 full spins
  const segmentCenter = segmentIndex * segmentAngle + segmentAngle / 2
  const finalRotation = baseRotation + (360 - segmentCenter) + Math.random() * (segmentAngle * 0.6) - segmentAngle * 0.3

  wheelRotation.value = finalRotation

  // Wait for animation
  await new Promise(r => setTimeout(r, 4000))

  // Calculate win
  const isWin = selectedColor.value === winningColor
  const winAmount = isWin ? effectiveBet.value * winningMultiplier - effectiveBet.value : -effectiveBet.value

  if (isWin) {
    balance.value += effectiveBet.value * winningMultiplier
    totalWon.value += winAmount
  }

  lastResult.value = {
    multiplier: winningMultiplier,
    win: winAmount,
    color: winningColor
  }

  history.value.unshift({
    color: winningColor,
    multiplier: winningMultiplier,
    win: winAmount
  })

  showResult.value = true
  isSpinning.value = false
  gameStatus.value = 'КРУТИ'

  // Generate new hash
  currentHash.value = Math.random().toString(36).substring(2, 6) + '...' + Math.random().toString(36).substring(2, 6)

  // Hide result after delay
  setTimeout(() => {
    showResult.value = false
  }, 3000)
}

let onlineInterval: number | null = null

onMounted(() => {
  onlineInterval = window.setInterval(() => {
    onlineCount.value = Math.floor(Math.random() * 50) + 130
  }, 5000)
})

onUnmounted(() => {
  if (onlineInterval) clearInterval(onlineInterval)
})
</script>

<style scoped>
.lucky-view {
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
.lucky-header {
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
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}

.title-badge.hot {
  background: #ef4444;
  color: #fff;
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
.balance-icon-svg { flex-shrink: 0; }
.balance-value { font-size: 14px; font-weight: 600; }

.balance-add {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 14px;
}

/* Game Info Bar */
.game-info-bar {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 0 16px 12px;
  position: relative;
  z-index: 10;
  flex-wrap: wrap;
}

.info-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1c1c1e;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.chip-label {
  color: #6b7280;
}

.chip-value {
  font-weight: 600;
}

.chip-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.info-chip.hash {
  font-family: monospace;
  font-size: 11px;
}

.copy-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: 12px;
  cursor: pointer;
}

/* Wheel Container */
.wheel-container {
  position: relative;
  width: 260px;
  height: 260px;
  margin: 20px auto;
  z-index: 10;
}

.wheel-pointer {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
}

.lucky-wheel {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  transition: transform 4s cubic-bezier(0.17, 0.67, 0.12, 0.99);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
}

.lucky-wheel.spinning {
  transition: transform 4s cubic-bezier(0.17, 0.67, 0.12, 0.99);
}

.wheel-segment {
  position: absolute;
  width: 50%;
  height: 50%;
  top: 0;
  left: 50%;
  transform-origin: 0% 100%;
  clip-path: polygon(0 100%, 100% 0, 100% 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.segment-label {
  position: absolute;
  top: 35%;
  left: 60%;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  transform: rotate(15deg);
}

.wheel-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  z-index: 5;
  border: 3px solid #333;
}

.spinning-text {
  font-size: 24px;
  animation: spinEmoji 0.5s linear infinite;
}

@keyframes spinEmoji {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.wheel-glow {
  position: absolute;
  inset: -10px;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
  box-shadow: 0 0 40px rgba(59, 130, 246, 0.5);
}

.wheel-glow.active {
  opacity: 1;
  animation: glowPulse 0.5s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.5); }
  50% { box-shadow: 0 0 60px rgba(59, 130, 246, 0.8); }
}

/* Result Display */
.result-display {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 24px 40px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(10px);
  z-index: 100;
  animation: popIn 0.3s ease;
}

@keyframes popIn {
  from { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
  to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

.result-display.win {
  border: 2px solid #22c55e;
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.3);
}

.result-display.lose {
  border: 2px solid #ef4444;
  box-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
}

.result-content {
  text-align: center;
}

.result-multiplier {
  display: block;
  font-size: 36px;
  font-weight: 800;
  color: #fff;
}

.result-amount {
  display: block;
  font-size: 18px;
  margin-top: 8px;
  color: #ef4444;
}

.result-amount.win {
  color: #4ade80;
}

/* History Strip */
.history-strip {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 12px 16px;
  position: relative;
  z-index: 10;
}

.history-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  opacity: 0.8;
}

.history-dot.yellow { background: #eab308; }
.history-dot.blue { background: #3b82f6; }
.history-dot.pink { background: #ec4899; }
.history-dot.purple { background: #8b5cf6; }
.history-dot.green { background: #22c55e; }

/* Betting Section */
.betting-section {
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  text-align: center;
}

.color-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.color-btn {
  flex: 1;
  min-width: 60px;
  padding: 12px 8px;
  border-radius: 12px;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}

.color-btn.yellow { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.color-btn.blue { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.color-btn.pink { background: rgba(236, 72, 153, 0.2); color: #ec4899; }
.color-btn.purple { background: rgba(139, 92, 246, 0.2); color: #8b5cf6; }
.color-btn.green { background: rgba(34, 197, 94, 0.2); color: #22c55e; }

.color-btn.selected {
  border-color: currentColor;
  transform: scale(1.05);
}

.color-btn:disabled {
  opacity: 0.5;
}

.color-mult {
  font-size: 14px;
  font-weight: 700;
}

.color-name {
  font-size: 10px;
  opacity: 0.8;
}

/* Bet Row */
.bet-row {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.bet-amounts {
  display: flex;
  gap: 6px;
}

.bet-btn {
  padding: 10px 14px;
  background: #1c1c1e;
  border: 2px solid transparent;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.bet-btn.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.15);
}

.bet-btn:disabled {
  opacity: 0.5;
}

.custom-bet {
  flex: 1;
  position: relative;
}

.bet-input {
  width: 100%;
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  border-radius: 10px;
  padding: 10px 50px 10px 12px;
  font-size: 13px;
  color: #fff;
  outline: none;
}

.bet-input:focus {
  border-color: #3b82f6;
}

.input-suffix {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: #6b7280;
}

/* Play Button */
.btn-play {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #facc15, #f59e0b);
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.btn-play:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0,0,0,0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Stats Panel */
.stats-panel {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.stat-box {
  flex: 1;
  background: #1c1c1e;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 10px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 14px;
  font-weight: 700;
}

.stat-value.win {
  color: #4ade80;
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
