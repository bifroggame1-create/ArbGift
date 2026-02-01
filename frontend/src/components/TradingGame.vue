<template>
  <!--
    PIXEL-PERFECT копия Trading Game из myballs.io
    CSS: bg-[#0E0F14], border-[#191919], rounded-4xl (32px)
    Uses TradingView Lightweight Charts
  -->
  <div class="trading-game">
    <!-- Game Container -->
    <div class="game-container">
      <div class="chart-wrapper">
        <div class="chart-frame">
          <!-- TradingView Chart -->
          <div ref="chartContainer" class="chart-area"></div>

          <!-- Current Multiplier Overlay -->
          <div
            class="multiplier-overlay"
            :class="multiplierClass"
          >
            {{ displayMultiplier }}x
          </div>

          <!-- Status Badge -->
          <div class="status-badge" :class="gameStatus">
            {{ statusText }}
          </div>
        </div>
      </div>
    </div>

    <!-- Bet Controls -->
    <div class="bet-controls">
      <!-- Bet Amount -->
      <div class="bet-amount-section">
        <label class="bet-label">Ставка</label>
        <div class="bet-input-wrapper">
          <button class="bet-adjust" @click="decreaseBet">-</button>
          <input
            v-model.number="betAmount"
            type="number"
            class="bet-input"
            min="0.1"
            step="0.1"
          />
          <button class="bet-adjust" @click="increaseBet">+</button>
        </div>
        <div class="quick-bets">
          <button
            v-for="amount in quickBets"
            :key="amount"
            class="quick-bet-btn"
            @click="betAmount = amount"
          >
            {{ amount }}
          </button>
        </div>
      </div>

      <!-- Auto Cashout -->
      <div class="auto-cashout-section">
        <label class="bet-label">
          <input type="checkbox" v-model="autoCashoutEnabled" class="checkbox" />
          Авто-вывод
        </label>
        <input
          v-model.number="autoCashoutAt"
          type="number"
          class="cashout-input"
          :disabled="!autoCashoutEnabled"
          min="1.01"
          step="0.01"
        />
      </div>
    </div>

    <!-- Action Button -->
    <button
      class="action-btn"
      :class="actionButtonClass"
      :disabled="!canAct"
      @click="handleAction"
    >
      <span v-if="gameStatus === 'waiting'">
        Ставка {{ betAmount }} TON
      </span>
      <span v-else-if="gameStatus === 'playing'">
        Вывести {{ potentialWin.toFixed(2) }} TON
      </span>
      <span v-else>
        Ожидание...
      </span>
    </button>

    <!-- Recent Results -->
    <div class="recent-results">
      <div
        v-for="(result, index) in recentResults"
        :key="index"
        class="result-badge"
        :class="getResultClass(result)"
      >
        {{ result.toFixed(2) }}x
      </div>
    </div>

    <!-- Live Bets -->
    <div class="live-bets">
      <div class="bets-header">
        <span class="bets-title">Ставки</span>
        <span class="bets-count">{{ liveBets.length }}</span>
      </div>
      <div class="bets-list">
        <div
          v-for="bet in liveBets"
          :key="bet.id"
          class="bet-item"
          :class="{ cashed: bet.cashedOut }"
        >
          <div class="bet-user">
            <img :src="bet.avatar" :alt="bet.name" class="bet-avatar" />
            <span class="bet-name">{{ bet.name }}</span>
          </div>
          <div class="bet-amount">{{ bet.amount }} TON</div>
          <div v-if="bet.cashedOut" class="bet-cashout">
            {{ bet.multiplier.toFixed(2) }}x
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { createChart, type IChartApi, type ISeriesApi } from 'lightweight-charts'
import { useTelegram } from '../composables/useTelegram'

const { hapticImpact } = useTelegram()

// Chart
const chartContainer = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
let lineSeries: ISeriesApi<'Line'> | null = null

// Game state
const gameStatus = ref<'waiting' | 'starting' | 'playing' | 'crashed'>('waiting')
const currentMultiplier = ref(1.0)
const crashPoint = ref(0)

// Bet state
const betAmount = ref(0.5)
const autoCashoutEnabled = ref(false)
const autoCashoutAt = ref(2.0)
const hasBet = ref(false)
const hasCashedOut = ref(false)

// Quick bet amounts
const quickBets = [0.1, 0.5, 1, 5, 10]

// Recent results
const recentResults = ref([2.34, 1.12, 5.67, 1.89, 3.21, 1.05, 8.92, 2.11, 1.45, 3.78])

// Live bets
const liveBets = ref([
  { id: 1, name: 'Alex', avatar: 'https://i.pravatar.cc/40?u=1', amount: 5, cashedOut: true, multiplier: 2.34 },
  { id: 2, name: 'Maria', avatar: 'https://i.pravatar.cc/40?u=2', amount: 2.5, cashedOut: false, multiplier: 0 },
  { id: 3, name: 'John', avatar: 'https://i.pravatar.cc/40?u=3', amount: 10, cashedOut: true, multiplier: 1.89 },
])

// Computed
const displayMultiplier = computed(() => {
  return currentMultiplier.value.toFixed(2)
})

const multiplierClass = computed(() => {
  if (gameStatus.value === 'crashed') return 'crashed'
  if (currentMultiplier.value >= 5) return 'high'
  if (currentMultiplier.value >= 2) return 'medium'
  return 'low'
})

const statusText = computed(() => {
  switch (gameStatus.value) {
    case 'waiting': return 'Принимаются ставки'
    case 'starting': return 'Запуск...'
    case 'playing': return 'Идёт игра'
    case 'crashed': return `Краш на ${crashPoint.value.toFixed(2)}x`
    default: return ''
  }
})

const potentialWin = computed(() => {
  return betAmount.value * currentMultiplier.value
})

const canAct = computed(() => {
  if (gameStatus.value === 'waiting' && !hasBet.value) return true
  if (gameStatus.value === 'playing' && hasBet.value && !hasCashedOut.value) return true
  return false
})

const actionButtonClass = computed(() => {
  if (gameStatus.value === 'playing' && hasBet.value && !hasCashedOut.value) {
    return 'cashout'
  }
  return 'bet'
})

// Methods
const decreaseBet = () => {
  if (betAmount.value > 0.1) {
    betAmount.value = Math.round((betAmount.value - 0.1) * 10) / 10
    hapticImpact('light')
  }
}

const increaseBet = () => {
  betAmount.value = Math.round((betAmount.value + 0.1) * 10) / 10
  hapticImpact('light')
}

const handleAction = () => {
  if (gameStatus.value === 'waiting' && !hasBet.value) {
    placeBet()
  } else if (gameStatus.value === 'playing' && hasBet.value && !hasCashedOut.value) {
    cashOut()
  }
}

const placeBet = () => {
  hasBet.value = true
  hapticImpact('medium')
  // Send bet to server via WebSocket
}

const cashOut = () => {
  hasCashedOut.value = true
  hapticImpact('heavy')
  // Send cashout to server
}

const getResultClass = (result: number) => {
  if (result < 1.5) return 'low'
  if (result < 3) return 'medium'
  return 'high'
}

// Chart setup
const initChart = () => {
  if (!chartContainer.value) return

  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    layout: {
      background: { color: '#0E0F14' },
      textColor: '#6d6d71',
    },
    grid: {
      vertLines: { color: '#191919' },
      horzLines: { color: '#191919' },
    },
    rightPriceScale: {
      borderColor: '#191919',
    },
    timeScale: {
      borderColor: '#191919',
      timeVisible: false,
    },
  })

  lineSeries = chart.addSeries({
    type: 'Line',
    color: '#00ff88',
    lineWidth: 2,
    priceLineVisible: false,
    lastValueVisible: false,
  })

  // Initial data
  const data = []
  for (let i = 0; i < 100; i++) {
    data.push({
      time: i as any,
      value: 1 + Math.random() * 0.1 * i,
    })
  }
  lineSeries?.setData(data)
}

// Simulate game (demo)
let gameInterval: ReturnType<typeof setInterval>

const startGameSimulation = () => {
  gameStatus.value = 'playing'
  currentMultiplier.value = 1.0
  crashPoint.value = 1 + Math.random() * 10

  gameInterval = setInterval(() => {
    if (currentMultiplier.value >= crashPoint.value) {
      gameStatus.value = 'crashed'
      clearInterval(gameInterval)

      // Reset after 3 seconds
      setTimeout(() => {
        gameStatus.value = 'waiting'
        hasBet.value = false
        hasCashedOut.value = false
        currentMultiplier.value = 1.0

        // Start new round after 5 seconds
        setTimeout(startGameSimulation, 5000)
      }, 3000)
      return
    }

    currentMultiplier.value += 0.01 + Math.random() * 0.02

    // Auto cashout
    if (autoCashoutEnabled.value && hasBet.value && !hasCashedOut.value) {
      if (currentMultiplier.value >= autoCashoutAt.value) {
        cashOut()
      }
    }

    // Update chart
    if (lineSeries) {
      lineSeries.update({
        time: Date.now() as any,
        value: currentMultiplier.value,
      })
    }
  }, 100)
}

onMounted(() => {
  initChart()
  // Start game simulation after 2 seconds
  setTimeout(startGameSimulation, 2000)
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
  }
  if (gameInterval) {
    clearInterval(gameInterval)
  }
})
</script>

<style scoped>
/*
  MYBALLS.IO Design System
  bg-[#0E0F14], border-[#191919], rounded-4xl (32px)
*/

.trading-game {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
  background: #0E0F14;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Game Container */
.game-container {
  margin-bottom: 16px;
}

.chart-wrapper {
  width: 100%;
  aspect-ratio: 1;
}

.chart-frame {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 32px;
  border: 2px solid #191919;
  background: #0E0F14;
  backdrop-filter: blur(14px);
  overflow: hidden;
}

.chart-area {
  width: 100%;
  height: 100%;
}

/* Multiplier Overlay */
.multiplier-overlay {
  position: absolute;
  bottom: 30%;
  right: 20%;
  font-family: 'SF Mono', monospace;
  font-size: 48px;
  font-weight: bold;
  color: #fff;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  pointer-events: none;
  transition: color 0.2s;
}

.multiplier-overlay.low {
  color: #fff;
}

.multiplier-overlay.medium {
  color: #00ff88;
}

.multiplier-overlay.high {
  color: #ffd700;
}

.multiplier-overlay.crashed {
  color: #ff4444;
}

/* Status Badge */
.status-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.status-badge.playing {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.status-badge.crashed {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

/* Bet Controls */
.bet-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.bet-amount-section {
  flex: 1;
}

.bet-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6d6d71;
  margin-bottom: 8px;
}

.checkbox {
  width: 16px;
  height: 16px;
  accent-color: #00ff88;
}

.bet-input-wrapper {
  display: flex;
  background: #191919;
  border-radius: 12px;
  overflow: hidden;
}

.bet-adjust {
  width: 44px;
  height: 44px;
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.bet-adjust:hover {
  background: #282727;
}

.bet-input {
  flex: 1;
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  outline: none;
}

.bet-input::-webkit-inner-spin-button {
  display: none;
}

.quick-bets {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.quick-bet-btn {
  flex: 1;
  padding: 8px;
  background: #191919;
  border: none;
  border-radius: 8px;
  color: #6d6d71;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-bet-btn:hover {
  background: #282727;
  color: #fff;
}

/* Auto Cashout */
.auto-cashout-section {
  width: 120px;
}

.cashout-input {
  width: 100%;
  height: 44px;
  background: #191919;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  text-align: center;
  outline: none;
}

.cashout-input:disabled {
  opacity: 0.5;
}

/* Action Button */
.action-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 16px;
}

.action-btn.bet {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #000;
}

.action-btn.cashout {
  background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%);
  color: #000;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn:not(:disabled):active {
  transform: scale(0.98);
}

/* Recent Results */
.recent-results {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 8px 0;
  margin-bottom: 16px;
}

.result-badge {
  flex-shrink: 0;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.result-badge.low {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.result-badge.medium {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.result-badge.high {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
}

/* Live Bets */
.live-bets {
  background: #191919;
  border-radius: 16px;
  overflow: hidden;
}

.bets-header {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #282727;
}

.bets-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.bets-count {
  font-size: 14px;
  color: #6d6d71;
}

.bets-list {
  max-height: 200px;
  overflow-y: auto;
}

.bet-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid #282727;
}

.bet-item.cashed {
  background: rgba(0, 255, 136, 0.05);
}

.bet-user {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.bet-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.bet-name {
  font-size: 13px;
  color: #fff;
}

.bet-amount {
  font-size: 13px;
  color: #6d6d71;
}

.bet-cashout {
  font-size: 13px;
  font-weight: 600;
  color: #00ff88;
}
</style>
