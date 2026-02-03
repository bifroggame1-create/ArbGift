<template>
  <div class="solo-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 30" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="solo-header">
      <button class="header-close" @click="$router.back()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
        <span>Закрыть</span>
      </button>
      <div class="online-badge">
        <span class="online-dot"></span>
        <span>{{ onlineCount }} онлайн</span>
      </div>
      <div class="header-actions">
        <button class="header-icon-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
        </button>
        <button class="header-icon-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- Title -->
    <div class="solo-title">
      <h1>Соло игры</h1>
      <p>Играй и выигрывай гифты!</p>
    </div>

    <!-- Balance Card -->
    <div class="balance-card">
      <div class="balance-row">
        <div class="balance-item">
          <svg class="balance-icon-svg" width="24" height="24" viewBox="0 0 56 56" fill="none">
            <circle cx="28" cy="28" r="28" fill="#0098EA"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
          </svg>
          <div class="balance-info">
            <span class="balance-label">TON Баланс</span>
            <span class="balance-value">{{ tonBalance }} TON</span>
          </div>
        </div>
        <div class="balance-divider"></div>
        <div class="balance-item">
          <img src="/icons/stars.png" alt="Stars" class="balance-icon-img" width="24" height="24" />
          <div class="balance-info">
            <span class="balance-label">Stars Баланс</span>
            <span class="balance-value">{{ starsBalance }} Stars</span>
          </div>
        </div>
      </div>
      <button class="btn-deposit" @click="$router.push('/topup')">
        <svg class="btn-icon-svg" width="14" height="14" viewBox="0 0 56 56" fill="none">
          <circle cx="28" cy="28" r="28" fill="#0098EA"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
        </svg>
        Пополнить баланс
      </button>
    </div>

    <!-- Games Section - Rolls.codes Style -->
    <div class="games-section">
      <h2 class="section-title">
        <span class="title-icon">🎰</span>
        Рулетки
      </h2>
      <div class="games-grid">
        <router-link to="/lucky" class="game-card lucky">
          <div class="game-badge hot">HOT</div>
          <div class="game-visual">
            <div class="lucky-wheel">
              <div class="wheel-segment" v-for="(_seg, i) in luckySegments" :key="i" :style="getSegmentStyle(i)"></div>
              <div class="wheel-center">?</div>
            </div>
          </div>
          <div class="game-info">
            <span class="game-name">Lucky</span>
            <span class="game-desc">Крути колесо</span>
          </div>
          <div class="game-multiplier">до x50</div>
        </router-link>

        <router-link to="/roulette" class="game-card mono">
          <div class="game-visual">
            <div class="mono-display">
              <div class="mono-row">
                <span class="mono-cell red"></span>
                <span class="mono-cell black"></span>
                <span class="mono-cell red"></span>
              </div>
            </div>
          </div>
          <div class="game-info">
            <span class="game-name">Моно</span>
            <span class="game-desc">Красное/Чёрное</span>
          </div>
          <div class="game-multiplier">x2</div>
        </router-link>

        <router-link to="/roll" class="game-card roll">
          <div class="game-visual">
            <div class="roll-display">
              <span class="roll-num">7</span>
              <span class="roll-num active">7</span>
              <span class="roll-num">7</span>
            </div>
          </div>
          <div class="game-info">
            <span class="game-name">Ролл</span>
            <span class="game-desc">0-100 числа</span>
          </div>
          <div class="game-multiplier">до x100</div>
        </router-link>
      </div>
    </div>

    <!-- Games Section - MyBalls.io Style -->
    <div class="games-section">
      <h2 class="section-title">
        <span class="title-icon">📈</span>
        Трейдинг
      </h2>
      <div class="games-list">
        <router-link to="/trading" class="game-card-wide trading">
          <div class="game-badge new">NEW</div>
          <div class="game-visual-wide">
            <div class="chart-preview">
              <svg viewBox="0 0 100 40" class="chart-line">
                <polyline
                  fill="none"
                  stroke="#22c55e"
                  stroke-width="2"
                  points="0,35 15,30 25,32 40,20 55,25 65,15 80,18 100,5"
                />
              </svg>
              <div class="chart-candles">
                <div class="candle green"></div>
                <div class="candle red"></div>
                <div class="candle green"></div>
                <div class="candle green"></div>
                <div class="candle red"></div>
              </div>
            </div>
          </div>
          <div class="game-info-wide">
            <span class="game-name">Trading / Crash</span>
            <span class="game-desc">Купи и продай вовремя</span>
          </div>
          <div class="game-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Games Section - Arcade -->
    <div class="games-section">
      <h2 class="section-title">
        <span class="title-icon">🎮</span>
        Аркады
      </h2>
      <div class="games-grid arcade">
        <router-link to="/plinko" class="game-card plinko">
          <div class="game-badge popular">TOP</div>
          <div class="game-visual">
            <div class="plinko-preview">
              <div class="pin-row" v-for="row in 4" :key="row">
                <span class="pin" v-for="pin in row + 2" :key="pin"></span>
              </div>
              <div class="ball-preview"></div>
            </div>
          </div>
          <div class="game-info">
            <span class="game-name">Plinko</span>
            <span class="game-desc">Кинь шарик</span>
          </div>
          <div class="game-multiplier">до x1000</div>
        </router-link>

        <router-link to="/ball-escape" class="game-card myballs">
          <div class="game-visual">
            <div class="balls-preview">
              <div class="funnel-shape"></div>
              <div class="preview-ball" v-for="i in 5" :key="i" :style="getBallStyle(i)"></div>
            </div>
          </div>
          <div class="game-info">
            <span class="game-name">MyBalls</span>
            <span class="game-desc">Цветные шары</span>
          </div>
          <div class="game-multiplier">до x10</div>
        </router-link>

        <router-link to="/rocket" class="game-card rocket">
          <div class="game-visual">
            <div class="rocket-preview">
              <span class="rocket-emoji">🚀</span>
              <div class="rocket-trail"></div>
            </div>
          </div>
          <div class="game-info">
            <span class="game-name">Rocket</span>
            <span class="game-desc">Взлёт ракеты</span>
          </div>
          <div class="game-multiplier">до x100</div>
        </router-link>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="stats-section">
      <div class="stat-block">
        <span class="stat-value">{{ formatNumber(totalWins) }}</span>
        <span class="stat-label">Всего выигрышей</span>
      </div>
      <div class="stat-block">
        <span class="stat-value">{{ formatNumber(totalPlayers) }}</span>
        <span class="stat-label">Игроков онлайн</span>
      </div>
      <div class="stat-block">
        <span class="stat-value">{{ totalPaid }} TON</span>
        <span class="stat-label">Выплачено</span>
      </div>
    </div>

    <!-- Upgrades Section -->
    <div class="games-section">
      <h2 class="section-title">
        <span class="title-icon">⬆️</span>
        Апгрейды
      </h2>
      <div class="upgrade-info-card">
        <div class="upgrade-icon">🎰</div>
        <div class="upgrade-text">
          <h3>Апгрейд гифтов</h3>
          <p>Объедините 2 гифта и получите шанс на более ценный!</p>
        </div>
        <router-link to="/upgrade" class="btn-upgrade">
          Попробовать
        </router-link>
      </div>
      <div class="upgrades-list">
        <div class="upgrade-item">
          <div class="upgrade-from">
            <span class="from-icon">🎁</span>
            <span>2x Common</span>
          </div>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          <div class="upgrade-to">
            <svg class="to-icon-svg" width="18" height="18" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
            <span>1x Rare</span>
          </div>
          <span class="upgrade-chance">45%</span>
        </div>
        <div class="upgrade-item">
          <div class="upgrade-from">
            <svg class="from-icon-svg" width="18" height="18" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
            <span>2x Rare</span>
          </div>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          <div class="upgrade-to">
            <span class="to-icon">👑</span>
            <span>1x Epic</span>
          </div>
          <span class="upgrade-chance">30%</span>
        </div>
      </div>
    </div>

    <!-- Provably Fair -->
    <div class="fair-block">
      <div class="fair-icon">🔐</div>
      <div class="fair-text">
        <span class="fair-title">Provably Fair</span>
        <span class="fair-desc">Все игры проверяемо честны</span>
      </div>
      <button class="fair-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// State
const onlineCount = ref(142)
const tonBalance = ref(0)
const starsBalance = ref(0)
const totalWins = ref(1847293)
const totalPlayers = ref(3291)
const totalPaid = ref('847.2K')

// Lucky wheel segments
const luckySegments = ['#22c55e', '#3b82f6', '#eab308', '#ec4899', '#8b5cf6', '#f97316']

// Pre-generate star styles once (not on every render)
const starStyles = Array.from({ length: 30 }, () => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
}))

// Stars background - use pre-generated styles
const getStarStyle = (i: number) => starStyles[i - 1]

// Lucky wheel segment style
const getSegmentStyle = (index: number) => {
  const rotation = (360 / luckySegments.length) * index
  return {
    background: luckySegments[index],
    transform: `rotate(${rotation}deg)`
  }
}

// Ball style for MyBalls preview
const getBallStyle = (i: number) => {
  const colors = ['#22c55e', '#3b82f6', '#ec4899', '#eab308', '#8b5cf6']
  return {
    background: colors[i - 1],
    left: `${15 + (i - 1) * 18}%`,
    animationDelay: `${i * 0.2}s`
  }
}

// Format large numbers
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

let pollInterval: number | null = null

onMounted(() => {
  pollInterval = window.setInterval(() => {
    onlineCount.value = Math.floor(Math.random() * 50) + 120
  }, 5000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.solo-view {
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
.solo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  position: relative;
  z-index: 10;
}

.header-close {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1c1c1e;
  border: none;
  color: #fff;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 14px;
}

.online-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-icon-btn {
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

/* Title */
.solo-title {
  padding: 0 16px 16px;
  position: relative;
  z-index: 10;
}

.solo-title h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 4px;
}

.solo-title p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* Balance Card */
.balance-card {
  margin: 0 16px 24px;
  background: linear-gradient(135deg, #1c1c1e 0%, #27272a 100%);
  border-radius: 20px;
  padding: 16px;
  position: relative;
  z-index: 10;
  border: 1px solid #3a3a3c;
}

.balance-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.balance-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.balance-icon {
  font-size: 24px;
}

.balance-icon-svg {
  flex-shrink: 0;
}

.balance-icon-img {
  flex-shrink: 0;
  object-fit: contain;
}

.btn-icon-svg {
  flex-shrink: 0;
  margin-right: 4px;
}

.balance-info {
  display: flex;
  flex-direction: column;
}

.balance-label {
  font-size: 11px;
  color: #6b7280;
}

.balance-value {
  font-size: 16px;
  font-weight: 700;
}

.balance-divider {
  width: 1px;
  height: 40px;
  background: #3a3a3c;
  margin: 0 12px;
}

.btn-deposit {
  width: 100%;
  background: #facc15;
  color: #000;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Games Section */
.games-section {
  padding: 0 16px;
  margin-bottom: 24px;
  position: relative;
  z-index: 10;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 20px;
}

/* Games Grid */
.games-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.games-grid.arcade {
  grid-template-columns: repeat(2, 1fr);
}

/* Game Card */
.game-card {
  background: #1c1c1e;
  border-radius: 16px;
  padding: 12px;
  text-decoration: none;
  color: #fff;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.game-card:active {
  transform: scale(0.98);
}

.game-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

.game-badge.hot {
  background: #ef4444;
  color: #fff;
}

.game-badge.new {
  background: #22c55e;
  color: #fff;
}

.game-badge.popular {
  background: #f97316;
  color: #fff;
}

.game-visual {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.game-info {
  display: flex;
  flex-direction: column;
}

.game-name {
  font-size: 13px;
  font-weight: 600;
}

.game-desc {
  font-size: 10px;
  color: #6b7280;
}

.game-multiplier {
  font-size: 11px;
  color: #4ade80;
  font-weight: 600;
  margin-top: 6px;
}

/* Lucky Wheel */
.lucky-wheel {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  animation: slowSpin 10s linear infinite;
}

@keyframes slowSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.wheel-segment {
  position: absolute;
  width: 50%;
  height: 50%;
  top: 0;
  left: 25%;
  transform-origin: 50% 100%;
  clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
}

.wheel-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  z-index: 2;
}

/* Mono Display */
.mono-display {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mono-row {
  display: flex;
  gap: 4px;
}

.mono-cell {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.mono-cell.red { background: #ef4444; }
.mono-cell.black { background: #27272a; border: 1px solid #3a3a3c; }

/* Roll Display */
.roll-display {
  display: flex;
  gap: 4px;
}

.roll-num {
  width: 20px;
  height: 28px;
  background: #27272a;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #6b7280;
}

.roll-num.active {
  background: #3b82f6;
  color: #fff;
}

/* Wide Game Card */
.games-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.game-card-wide {
  background: #1c1c1e;
  border-radius: 16px;
  padding: 16px;
  text-decoration: none;
  color: #fff;
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
}

.game-visual-wide {
  width: 80px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.game-info-wide {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.game-arrow {
  color: #6b7280;
}

/* Chart Preview */
.chart-preview {
  width: 80px;
  height: 50px;
  position: relative;
}

.chart-line {
  position: absolute;
  inset: 0;
}

.chart-candles {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 30px;
}

.candle {
  width: 6px;
  border-radius: 2px;
}

.candle.green {
  background: #22c55e;
  height: 20px;
}

.candle.red {
  background: #ef4444;
  height: 15px;
}

/* Plinko Preview */
.plinko-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  position: relative;
}

.pin-row {
  display: flex;
  gap: 8px;
}

.pin {
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
}

.ball-preview {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 10px;
  height: 10px;
  background: #ec4899;
  border-radius: 50%;
  animation: plinkoFall 2s ease-in-out infinite;
}

@keyframes plinkoFall {
  0% { top: 0; left: 50%; }
  25% { top: 25%; left: 45%; }
  50% { top: 50%; left: 55%; }
  75% { top: 75%; left: 40%; }
  100% { top: 100%; left: 50%; opacity: 0; }
}

/* MyBalls Preview */
.balls-preview {
  width: 60px;
  height: 60px;
  position: relative;
}

.funnel-shape {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 30px solid transparent;
  border-right: 30px solid transparent;
  border-top: 40px solid #27272a;
}

.preview-ball {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: ballFloat 1.5s ease-in-out infinite;
}

@keyframes ballFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* Giftomania Preview */
.giftomania-preview {
  width: 60px;
  height: 60px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wheel-ring {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 4px solid #27272a;
  position: relative;
}

.wheel-progress {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #facc15;
  animation: progressSpin 2s linear infinite;
}

@keyframes progressSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.wheel-gift {
  position: absolute;
  font-size: 20px;
}

/* Rocket Preview */
.rocket-preview {
  width: 60px;
  height: 60px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rocket-emoji {
  font-size: 28px;
  animation: rocketBounce 1s ease-in-out infinite;
}

@keyframes rocketBounce {
  0%, 100% { transform: translateY(0) rotate(-45deg); }
  50% { transform: translateY(-8px) rotate(-45deg); }
}

.rocket-trail {
  position: absolute;
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 20px;
  background: linear-gradient(to bottom, #f97316, transparent);
  border-radius: 4px;
  opacity: 0.6;
}

/* Stats Section */
.stats-section {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  margin-bottom: 24px;
  position: relative;
  z-index: 10;
}

.stat-block {
  flex: 1;
  background: #1c1c1e;
  border-radius: 14px;
  padding: 14px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #4ade80;
}

.stat-label {
  font-size: 10px;
  color: #6b7280;
}

/* Provably Fair */
.fair-block {
  margin: 0 16px 24px;
  background: #1c1c1e;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 10;
}

.fair-icon {
  font-size: 28px;
}

.fair-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.fair-title {
  font-size: 14px;
  font-weight: 600;
}

.fair-desc {
  font-size: 12px;
  color: #6b7280;
}

.fair-btn {
  width: 36px;
  height: 36px;
  background: #27272a;
  border: none;
  border-radius: 10px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Upgrades */
.upgrade-info-card {
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.upgrade-icon {
  font-size: 40px;
}

.upgrade-text {
  flex: 1;
}

.upgrade-text h3 {
  font-size: 16px;
  margin: 0 0 4px;
}

.upgrade-text p {
  font-size: 12px;
  opacity: 0.8;
  margin: 0;
}

.btn-upgrade {
  background: #fff;
  color: #1e3a8a;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.upgrades-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upgrade-item {
  background: #1c1c1e;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.upgrade-from, .upgrade-to {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.from-icon, .to-icon {
  font-size: 18px;
}

.from-icon-svg, .to-icon-svg {
  flex-shrink: 0;
}

.upgrade-chance {
  margin-left: auto;
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

</style>
