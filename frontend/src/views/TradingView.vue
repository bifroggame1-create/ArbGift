<template>
  <div class="trading-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 20" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

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

    <!-- Connection Status -->
    <div class="connection-bar">
      <div class="connection-status" :class="{ connected: connectionStatus === 'Connected' }">
        <span class="status-dot"></span>
        <span>{{ connectionStatus }}</span>
      </div>
      <div class="game-info">
        <span>ИГРА #{{ gameNumber }}</span>
        <span class="hash-text">{{ currentHash }}</span>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="chart-container">
      <!-- Multiplier Display -->
      <div class="multiplier-overlay" :class="{ crashed: gameStatus === 'crashed' }">
        <div v-if="gameStatus === 'active'" class="multiplier-active">
          <span class="multiplier-value" :class="{ high: currentMultiplier >= 2 }">
            {{ currentMultiplier.toFixed(2) }}x
          </span>
          <span class="multiplier-label">МНОЖИТЕЛЬ</span>
        </div>
        <div v-else-if="gameStatus === 'crashed'" class="multiplier-crashed">
          <span class="crash-value">{{ crashPoint.toFixed(2) }}x</span>
          <span class="crash-label">CRASHED!</span>
          <span class="next-game">Следующая игра через {{ nextGameTimer }}с</span>
        </div>
        <div v-else class="multiplier-waiting">
          <span class="waiting-text">Ожидание игроков...</span>
          <span class="waiting-sub">Сделайте ставку</span>
        </div>
      </div>

      <!-- Chart Canvas -->
      <div ref="chartContainer" class="chart-canvas"></div>

      <!-- Chart Grid -->
      <div class="chart-grid">
        <div class="grid-line" v-for="i in 5" :key="i"></div>
      </div>

      <!-- Candlesticks Preview -->
      <div class="candles-row">
        <div
          v-for="(candle, i) in candles"
          :key="i"
          class="candle"
          :class="candle.type"
          :style="{ height: candle.height + 'px' }"
        ></div>
      </div>
    </div>

    <!-- Traders Panel -->
    <div class="traders-panel">
      <div class="traders-header">
        <span class="traders-title">Игроки</span>
        <span class="traders-count">{{ traderCount }}</span>
      </div>
      <div class="traders-list">
        <div v-for="trader in traders" :key="trader.id" class="trader-item">
          <div class="trader-avatar" :style="{ background: trader.color }">
            {{ trader.name.charAt(0) }}
          </div>
          <div class="trader-info">
            <span class="trader-name">@{{ trader.name }}</span>
            <span class="trader-bet">{{ trader.bet }} TON</span>
          </div>
          <div class="trader-status" :class="trader.status">
            <span v-if="trader.status === 'won'" class="status-won">+{{ trader.profit }}</span>
            <span v-else-if="trader.status === 'playing'">{{ trader.multiplier }}x</span>
            <span v-else class="status-waiting">⏳</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bet Controls -->
    <div class="bet-controls">
      <!-- Bet Amount Selection -->
      <div class="bet-amounts">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          :class="['bet-amount', { active: selectedBetAmount === amount }]"
          @click="selectedBetAmount = amount"
        >
          <span class="amount-value">{{ amount }}</span>
          <span class="amount-icon">💎</span>
        </button>
      </div>

      <!-- Custom Bet Input -->
      <div class="custom-bet">
        <input
          type="number"
          v-model.number="customBetAmount"
          placeholder="Своя сумма"
          class="bet-input"
        />
        <span class="input-icon">TON</span>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button
          class="btn-buy"
          :disabled="gameStatus !== 'pending' || isPlacingBet"
          @click="placeBet"
        >
          <span class="btn-icon">📈</span>
          <span class="btn-text">
            {{ isPlacingBet ? 'Покупаем...' : `Купить ${effectiveBetAmount} TON` }}
          </span>
        </button>
        <button
          class="btn-sell"
          :disabled="!activeBet || gameStatus !== 'active' || isCashingOut"
          @click="cashOut"
        >
          <span class="btn-icon">📉</span>
          <span class="btn-text">
            {{ isCashingOut ? 'Продаём...' : activeBet ? `Продать +${((activeBet.bet_amount * currentMultiplier) - activeBet.bet_amount).toFixed(2)}` : 'Продать' }}
          </span>
        </button>
      </div>

      <!-- Auto Cashout -->
      <div class="auto-cashout">
        <span class="auto-label">Авто-продажа на:</span>
        <div class="auto-options">
          <button
            v-for="mult in autoMultipliers"
            :key="mult"
            :class="['auto-btn', { active: autoMultiplier === mult }]"
            @click="autoMultiplier = mult"
          >
            {{ mult }}x
          </button>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <transition-group name="notification" tag="div" class="notifications">
      <div
        v-for="notif in notifications"
        :key="notif.id"
        :class="['notification', notif.type]"
      >
        <span class="notif-icon">{{ notif.type === 'buy' ? '📈' : '📉' }}</span>
        <span class="notif-text">{{ notif.message }}</span>
      </div>
    </transition-group>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/pvp" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4l4 4m8 8l4 4M4 20l4-4m8-8l4-4M12 12l-8 8m16 0l-8-8m0 0l8-8M4 4l8 8"/>
        </svg>
        <span>ПвП</span>
      </router-link>
      <router-link to="/solo" class="nav-item active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        <span>Соло</span>
      </router-link>
      <router-link to="/inventory" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M3 9h18M9 21V9"/>
        </svg>
        <span>Инвентарь</span>
      </router-link>
      <router-link to="/shop" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>Магазин</span>
      </router-link>
      <router-link to="/profile" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>Профиль</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

interface Trader {
  id: number
  name: string
  bet: number
  color: string
  status: 'waiting' | 'playing' | 'won' | 'lost'
  multiplier?: number
  profit?: number
}

interface Notification {
  id: number
  type: 'buy' | 'sell'
  message: string
}

// State
const balance = ref(4.16)
const currentMultiplier = ref(1.00)
const gameStatus = ref<'pending' | 'active' | 'crashed'>('pending')
const crashPoint = ref(0)
const nextGameTimer = ref(5)
const gameNumber = ref(28392)
const traderCount = ref(12)
const currentHash = ref('3d07...f8da')
const connectionStatus = ref('Connecting...')

// Bet state
const betAmounts = [0.5, 1, 2, 5]
const selectedBetAmount = ref(1)
const customBetAmount = ref<number | null>(null)
const autoMultipliers = [1.5, 2, 3, 5, 10]
const autoMultiplier = ref<number | null>(null)
const activeBet = ref<any>(null)
const isPlacingBet = ref(false)
const isCashingOut = ref(false)

// Effective bet amount
const effectiveBetAmount = computed(() => {
  return customBetAmount.value || selectedBetAmount.value
})

// Traders
const traders = ref<Trader[]>([
  { id: 1, name: 'trader1', bet: 2.5, color: '#22c55e', status: 'playing', multiplier: 1.45 },
  { id: 2, name: 'winner99', bet: 1.0, color: '#3b82f6', status: 'won', profit: 1.8 },
  { id: 3, name: 'lucky_star', bet: 5.0, color: '#ec4899', status: 'waiting' },
])

// Candles for visual effect
const candles = ref([
  { type: 'green', height: 25 },
  { type: 'red', height: 18 },
  { type: 'green', height: 32 },
  { type: 'green', height: 28 },
  { type: 'red', height: 15 },
  { type: 'green', height: 40 },
  { type: 'red', height: 22 },
  { type: 'green', height: 35 },
])

// Notifications
const notifications = ref<Notification[]>([])
let notificationId = 0

const addNotification = (type: 'buy' | 'sell', message: string) => {
  const id = ++notificationId
  notifications.value.push({ id, type, message })
  setTimeout(() => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }, 3000)
}

// WebSocket
const ws = ref<WebSocket | null>(null)
const chartContainer = ref<HTMLElement | null>(null)

// Stars background
const getStarStyle = (i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

// Game simulation for demo
let gameInterval: number | null = null

const simulateGame = () => {
  gameStatus.value = 'active'
  currentMultiplier.value = 1.00

  gameInterval = window.setInterval(() => {
    if (gameStatus.value !== 'active') return

    currentMultiplier.value += Math.random() * 0.05 + 0.01

    // Random crash
    if (Math.random() < 0.02 || currentMultiplier.value > 10) {
      crashPoint.value = currentMultiplier.value
      gameStatus.value = 'crashed'

      if (activeBet.value) {
        activeBet.value = null
        addNotification('sell', `Проигрыш -${effectiveBetAmount.value} TON`)
      }

      nextGameTimer.value = 5
      const countdown = setInterval(() => {
        nextGameTimer.value--
        if (nextGameTimer.value <= 0) {
          clearInterval(countdown)
          gameStatus.value = 'pending'
          gameNumber.value++
          setTimeout(simulateGame, 2000)
        }
      }, 1000)

      if (gameInterval) clearInterval(gameInterval)
    }

    // Auto cashout
    if (autoMultiplier.value && activeBet.value && currentMultiplier.value >= autoMultiplier.value) {
      cashOut()
    }
  }, 100)
}

const placeBet = async () => {
  if (gameStatus.value !== 'pending') return

  isPlacingBet.value = true
  await new Promise(r => setTimeout(r, 500))

  activeBet.value = {
    id: Date.now(),
    bet_amount: effectiveBetAmount.value
  }
  balance.value -= effectiveBetAmount.value

  addNotification('buy', `Куплено за ${effectiveBetAmount.value} TON`)
  isPlacingBet.value = false
}

const cashOut = async () => {
  if (!activeBet.value || gameStatus.value !== 'active') return

  isCashingOut.value = true
  await new Promise(r => setTimeout(r, 300))

  const payout = activeBet.value.bet_amount * currentMultiplier.value
  balance.value += payout

  addNotification('sell', `Продано за ${payout.toFixed(2)} TON (+${(payout - activeBet.value.bet_amount).toFixed(2)})`)
  activeBet.value = null
  isCashingOut.value = false
}

onMounted(() => {
  connectionStatus.value = 'Connected'
  setTimeout(simulateGame, 2000)
})

onUnmounted(() => {
  if (gameInterval) clearInterval(gameInterval)
  if (ws.value) ws.value.close()
})
</script>

<style scoped>
.trading-view {
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
.trading-header {
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
  background: #22c55e;
  color: #000;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
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
.balance-value { font-size: 14px; font-weight: 600; }

.balance-add {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 14px;
  margin-left: 4px;
}

/* Connection Bar */
.connection-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 12px;
  position: relative;
  z-index: 10;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.connection-status.connected { color: #4ade80; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6b7280;
}

.connection-status.connected .status-dot {
  background: #4ade80;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.game-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11px;
  color: #6b7280;
}

.hash-text {
  font-family: monospace;
}

/* Chart Container */
.chart-container {
  margin: 0 16px 16px;
  background: linear-gradient(180deg, #0a1628 0%, #0f172a 100%);
  border-radius: 20px;
  height: 200px;
  position: relative;
  z-index: 10;
  overflow: hidden;
  border: 1px solid #1e3a5f;
}

.chart-canvas {
  position: absolute;
  inset: 0;
}

.chart-grid {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px 0;
  pointer-events: none;
}

.grid-line {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
}

/* Multiplier Overlay */
.multiplier-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

.multiplier-overlay.crashed {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.multiplier-active {
  text-align: center;
}

.multiplier-value {
  display: block;
  font-size: 56px;
  font-weight: 800;
  color: #3b82f6;
  text-shadow: 0 0 40px rgba(59, 130, 246, 0.5);
  transition: color 0.3s;
}

.multiplier-value.high {
  color: #22c55e;
  text-shadow: 0 0 40px rgba(34, 197, 94, 0.5);
}

.multiplier-label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  letter-spacing: 2px;
  margin-top: 4px;
}

.multiplier-crashed {
  text-align: center;
}

.crash-value {
  display: block;
  font-size: 48px;
  font-weight: 800;
  color: #ef4444;
  text-shadow: 0 0 40px rgba(239, 68, 68, 0.5);
}

.crash-label {
  display: block;
  font-size: 16px;
  color: #ef4444;
  margin-top: 4px;
}

.next-game {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 12px;
}

.multiplier-waiting {
  text-align: center;
}

.waiting-text {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.waiting-sub {
  display: block;
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

/* Candles Row */
.candles-row {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  gap: 8px;
  pointer-events: none;
}

.candle {
  width: 12px;
  border-radius: 2px;
  opacity: 0.6;
}

.candle.green { background: #22c55e; }
.candle.red { background: #ef4444; }

/* Traders Panel */
.traders-panel {
  margin: 0 16px 16px;
  background: #1c1c1e;
  border-radius: 16px;
  padding: 14px;
  position: relative;
  z-index: 10;
}

.traders-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.traders-title {
  font-size: 14px;
  font-weight: 600;
}

.traders-count {
  background: #27272a;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 12px;
  color: #6b7280;
}

.traders-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 120px;
  overflow-y: auto;
}

.trader-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: #27272a;
  border-radius: 10px;
}

.trader-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.trader-info {
  flex: 1;
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

.trader-status {
  font-size: 12px;
  font-weight: 600;
}

.status-won { color: #4ade80; }
.status-waiting { opacity: 0.5; }

/* Bet Controls */
.bet-controls {
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.bet-amounts {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.bet-amount {
  flex: 1;
  background: #1c1c1e;
  border: 2px solid transparent;
  border-radius: 12px;
  padding: 12px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.2s;
}

.bet-amount.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.15);
}

.amount-value {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.amount-icon {
  font-size: 12px;
}

.custom-bet {
  position: relative;
  margin-bottom: 12px;
}

.bet-input {
  width: 100%;
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  border-radius: 12px;
  padding: 14px 60px 14px 16px;
  font-size: 14px;
  color: #fff;
  outline: none;
}

.bet-input:focus {
  border-color: #3b82f6;
}

.bet-input::placeholder {
  color: #6b7280;
}

.input-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #6b7280;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.btn-buy, .btn-sell {
  flex: 1;
  border: none;
  border-radius: 14px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-buy {
  background: linear-gradient(135deg, #16a34a, #22c55e);
  color: #fff;
}

.btn-buy:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-sell {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: #fff;
}

.btn-sell:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 16px;
}

/* Auto Cashout */
.auto-cashout {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #1c1c1e;
  border-radius: 12px;
}

.auto-label {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.auto-options {
  display: flex;
  gap: 6px;
  flex: 1;
  overflow-x: auto;
}

.auto-btn {
  padding: 6px 12px;
  background: #27272a;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.auto-btn.active {
  border-color: #facc15;
  background: rgba(250, 204, 21, 0.15);
  color: #facc15;
}

/* Notifications */
.notifications {
  position: fixed;
  top: 80px;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 1000;
}

.notification {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

.notification.buy {
  background: rgba(34, 197, 94, 0.9);
  color: #fff;
}

.notification.sell {
  background: rgba(59, 130, 246, 0.9);
  color: #fff;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(20px);
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
