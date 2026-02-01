<template>
  <div class="pvp-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 30" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="pvp-header">
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
            <path d="M6 9l6 6 6-6"/>
          </svg>
        </button>
        <button class="header-icon-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- Top Stats Cards -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-avatar">
          <img v-if="prevGame.avatar" :src="prevGame.avatar" />
          <span v-else>{{ prevGame.name?.charAt(0) }}</span>
        </div>
        <div class="stat-content">
          <div class="stat-name">{{ prevGame.name }}</div>
          <div class="stat-label">ПРЕД. ИГРА</div>
        </div>
        <div class="stat-right">
          <div class="stat-amount">+{{ prevGame.amount }} TON</div>
          <div class="stat-chance">ШАНС {{ prevGame.chance }}%</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-avatar">
          <img v-if="topGame.avatar" :src="topGame.avatar" />
          <span v-else>{{ topGame.name?.charAt(0) }}</span>
        </div>
        <div class="stat-content">
          <div class="stat-name">{{ topGame.name }}</div>
          <div class="stat-label">ТОП ИГРА</div>
        </div>
        <div class="stat-right">
          <div class="stat-amount">+{{ topGame.amount }} TON</div>
          <div class="stat-chance">ШАНС {{ topGame.chance }}%</div>
        </div>
      </div>
    </div>

    <!-- Pool Bar -->
    <div class="pool-bar">
      <button class="pool-icon-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
      </button>
      <div class="pool-total">
        <span class="pool-label">ВСЕГО</span>
        <span class="pool-value">{{ totalPool }} TON</span>
      </div>
      <button class="pool-icon-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
        </svg>
      </button>
    </div>

    <!-- Roulette Container -->
    <div class="roulette-wrapper">
      <!-- Pointer -->
      <div class="roulette-pointer">
        <svg width="24" height="28" viewBox="0 0 24 28" fill="white">
          <path d="M12 28L0 6h24L12 28z"/>
        </svg>
      </div>

      <!-- Wheel -->
      <svg
        class="roulette-wheel"
        :class="{ spinning: isSpinning }"
        :style="{ transform: `rotate(${wheelRotation}deg)` }"
        viewBox="0 0 300 300"
      >
        <!-- Empty state -->
        <g v-if="players.length === 0">
          <circle cx="150" cy="150" r="140" fill="#3a3a3c"/>
          <circle cx="150" cy="150" r="50" fill="#000"/>
          <text x="150" y="155" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="14">Ожидание</text>
        </g>

        <!-- Player segments -->
        <g v-else>
          <g v-for="(player, index) in players" :key="player.id">
            <path
              :d="getSegmentPath(index)"
              :fill="player.color"
              stroke="#1a1a1a"
              stroke-width="1"
            />
            <!-- Avatar circle -->
            <g :transform="getAvatarTransform(index)">
              <circle r="18" fill="rgba(255,255,255,0.2)"/>
              <image
                v-if="player.avatar"
                :href="player.avatar"
                x="-14" y="-14" width="28" height="28"
                clip-path="url(#avatarClip)"
                preserveAspectRatio="xMidYMid slice"
              />
              <text v-else x="0" y="5" text-anchor="middle" fill="white" font-size="12" font-weight="bold">
                {{ player.name?.charAt(0) }}
              </text>
            </g>
          </g>
        </g>

        <!-- Center circle -->
        <circle cx="150" cy="150" r="50" fill="#000"/>
        <text x="150" y="155" text-anchor="middle" fill="white" font-size="16" font-weight="600">
          {{ gameStatus }}
        </text>

        <defs>
          <clipPath id="avatarClip"><circle r="14"/></clipPath>
        </defs>
      </svg>
    </div>

    <!-- Game Status Text -->
    <div class="status-line">
      <span class="status-icon">⚔️</span>
      <span class="status-text">{{ statusText }}</span>
    </div>

    <!-- Players Section -->
    <div class="players-section">
      <div class="players-header">
        <span class="players-count">{{ players.length }} Игрока</span>
        <span class="game-id">ИГРА #{{ gameId }}</span>
      </div>

      <div class="players-list">
        <div
          v-for="player in players"
          :key="player.id"
          class="player-item"
        >
          <div class="player-avatar" :style="{ background: player.color }">
            <img v-if="player.avatar" :src="player.avatar" />
            <span v-else>{{ player.name?.charAt(0) }}</span>
          </div>
          <div class="player-info">
            <span class="player-name">@{{ player.username }}</span>
            <span class="player-role">Игрок</span>
          </div>
          <div class="player-stats">
            <span class="player-chance">{{ player.chance }}%</span>
            <span class="player-bet">{{ player.bet }} TON</span>
          </div>
          <div class="player-badge" :style="{ background: player.color }">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <span>{{ player.bet }}</span>
          </div>
          <svg class="player-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Filter Buttons -->
    <div class="filter-bar">
      <div class="filter-btns">
        <button class="filter-btn red"><span>🎲</span></button>
        <button class="filter-btn blue"><span>💎</span></button>
        <button class="filter-btn yellow"><span>⭐</span></button>
      </div>
      <div class="balance-pill">
        <span class="balance-icon">💎</span>
        <span class="balance-value">{{ userBalance }}</span>
        <button class="balance-add">+</button>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-row">
      <button class="btn-add" @click="showBetModal = true">
        + Добавить в PvP
      </button>
      <button class="btn-pool">
        <span>👑</span>
        <span>{{ totalPool }} TON</span>
      </button>
    </div>

    <!-- Hash Footer -->
    <div class="hash-footer">
      <span class="hash-hint">Добавь гифт. Войди первым в игру</span>
      <div class="hash-row">
        <span>Hash {{ serverHash }}</span>
        <button class="hash-copy">🔗</button>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/pvp" class="nav-item active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4l4 4m8 8l4 4M4 20l4-4m8-8l4-4M12 12l-8 8m16 0l-8-8m0 0l8-8M4 4l8 8"/>
        </svg>
        <span>ПвП</span>
      </router-link>
      <router-link to="/solo" class="nav-item">
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

    <!-- Bet Modal -->
    <Teleport to="body">
      <div v-if="showBetModal" class="modal-overlay" @click.self="showBetModal = false">
        <div class="bet-modal">
          <div class="modal-handle"></div>
          <div class="modal-header">
            <h3>Выберите подарок</h3>
            <button class="modal-close" @click="showBetModal = false">×</button>
          </div>

          <div class="modal-tabs">
            <button :class="['tab', { active: giftTab === 'ton' }]" @click="giftTab = 'ton'">
              <span>💎</span> TON Гифты
            </button>
            <button :class="['tab', { active: giftTab === 'stars' }]" @click="giftTab = 'stars'">
              <span>⭐</span> Stars Гифты
            </button>
          </div>

          <div class="modal-search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            <input type="text" placeholder="Поиск гифта или ID гифта" v-model="giftSearch" />
          </div>

          <div class="gifts-section">
            <h4 class="section-title">🔥 В тренде</h4>
            <div class="gifts-grid">
              <div
                v-for="gift in trendingGifts"
                :key="gift.id"
                :class="['gift-card', { selected: selectedGift?.id === gift.id }]"
                @click="selectedGift = gift"
              >
                <div class="gift-radio" :class="{ checked: selectedGift?.id === gift.id }"></div>
                <img :src="gift.image" :alt="gift.name" class="gift-img" />
                <span class="gift-name">{{ gift.name }}</span>
                <span class="gift-price">
                  {{ giftTab === 'ton' ? '💎' : '⭐' }} {{ gift.price }} {{ giftTab === 'ton' ? 'TON' : 'Stars' }}
                </span>
              </div>
            </div>
          </div>

          <div class="gifts-section">
            <h4 class="section-title">🎁 Все</h4>
            <div class="gifts-grid">
              <div
                v-for="gift in allGifts"
                :key="gift.id"
                :class="['gift-card', { selected: selectedGift?.id === gift.id }]"
                @click="selectedGift = gift"
              >
                <div class="gift-radio" :class="{ checked: selectedGift?.id === gift.id }"></div>
                <img :src="gift.image" :alt="gift.name" class="gift-img" />
                <span class="gift-name">{{ gift.name }}</span>
                <span class="gift-price">
                  {{ giftTab === 'ton' ? '💎' : '⭐' }} {{ gift.price }} {{ giftTab === 'ton' ? 'TON' : 'Stars' }}
                </span>
              </div>
            </div>
          </div>

          <button class="modal-submit" :disabled="!selectedGift" @click="placeBet">
            Поставить
          </button>
        </div>
      </div>
    </Teleport>

    <!-- Winner Modal -->
    <Teleport to="body">
      <div v-if="showWinnerModal" class="modal-overlay" @click.self="showWinnerModal = false">
        <div class="winner-modal">
          <div class="winner-header">
            <h3>Игра #{{ gameId }}</h3>
            <button class="modal-close" @click="showWinnerModal = false">×</button>
          </div>
          <div class="winner-content">
            <div class="winner-avatar">
              <img v-if="winner?.avatar" :src="winner.avatar" />
              <span v-else>{{ winner?.name?.charAt(0) }}</span>
            </div>
            <div class="winner-info">
              <span class="winner-name">@{{ winner?.username }}</span>
              <span class="winner-label">Победитель</span>
            </div>
            <div class="winner-prize">
              <span class="prize-amount">Выиграл {{ winAmount }} TON</span>
              <span class="prize-chance">{{ winner?.chance }}%</span>
            </div>
          </div>
          <div class="winner-gift">
            <div class="gift-won">
              <span class="gift-icon">💎</span>
            </div>
            <span class="gift-value">💎 {{ winAmount }} TON</span>
          </div>
          <button class="btn-done" @click="showWinnerModal = false">Готово</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Player {
  id: number
  name: string
  username: string
  avatar?: string
  bet: number
  chance: number
  color: string
}

interface Gift {
  id: number
  name: string
  image: string
  price: number
}

// Rolls.codes colors
const playerColors = [
  '#22d3ee', // cyan
  '#22c55e', // green
  '#ec4899', // pink
  '#8b5cf6', // purple
  '#f97316', // orange
  '#eab308', // yellow
  '#3b82f6', // blue
  '#14b8a6', // teal
]

// State
const onlineCount = ref(98)
const totalPool = ref(3.98)
const gameId = ref(315993)
const gameStatus = ref('ИГРА')
const statusText = ref('PvP начался')
const wheelRotation = ref(0)
const isSpinning = ref(false)
const showBetModal = ref(false)
const showWinnerModal = ref(false)
const giftTab = ref<'ton' | 'stars'>('ton')
const giftSearch = ref('')
const selectedGift = ref<Gift | null>(null)
const userBalance = ref(0)
const serverHash = ref('1a418...f6d87')
const winner = ref<Player | null>(null)
const winAmount = ref(0)

const prevGame = ref({ name: 'Сосредоточен', avatar: '', amount: 53, chance: 4 })
const topGame = ref({ name: '@giftgambl...', avatar: '', amount: 48603, chance: 82 })

const players = ref<Player[]>([
  { id: 1, name: 'ybuval', username: 'ybuval', bet: 1.59, chance: 40.2, color: playerColors[0] },
  { id: 2, name: 'Player2', username: 'player2', bet: 1.2, chance: 30.2, color: playerColors[1] },
  { id: 3, name: 'Player3', username: 'player3', bet: 0.8, chance: 20.1, color: playerColors[2] },
  { id: 4, name: 'Player4', username: 'player4', bet: 0.39, chance: 9.5, color: playerColors[3] },
])

const trendingGifts = ref<Gift[]>([
  { id: 1, name: 'Input Key', image: '/gifts/key.webp', price: 0.06 },
  { id: 2, name: 'Diamond Ring', image: '/gifts/ring.webp', price: 1.02 },
  { id: 3, name: 'Voodoo Doll', image: '/gifts/doll.webp', price: 0.45 },
])

const allGifts = ref<Gift[]>([
  { id: 4, name: 'Eternal Rose', image: '/gifts/rose.webp', price: 0.27 },
  { id: 5, name: 'Cupid Charm', image: '/gifts/cupid.webp', price: 0.24 },
  { id: 6, name: 'Love Potion', image: '/gifts/potion.webp', price: 0.18 },
])

// Stars background
const getStarStyle = (_i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

// Wheel calculations based on chance percentages
const getSegmentPath = (index: number) => {
  const total = players.value.reduce((sum, p) => sum + p.chance, 0)
  let startAngle = -90
  for (let i = 0; i < index; i++) {
    startAngle += (players.value[i].chance / total) * 360
  }
  const sweepAngle = (players.value[index].chance / total) * 360
  const endAngle = startAngle + sweepAngle

  const cx = 150, cy = 150, r = 140
  const start = polarToCartesian(cx, cy, r, endAngle)
  const end = polarToCartesian(cx, cy, r, startAngle)
  const largeArc = sweepAngle > 180 ? 1 : 0

  return `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y} Z`
}

const getAvatarTransform = (index: number) => {
  const total = players.value.reduce((sum, p) => sum + p.chance, 0)
  let startAngle = -90
  for (let i = 0; i < index; i++) {
    startAngle += (players.value[i].chance / total) * 360
  }
  const midAngle = startAngle + (players.value[index].chance / total) * 180
  const pos = polarToCartesian(150, 150, 95, midAngle)
  return `translate(${pos.x}, ${pos.y})`
}

const polarToCartesian = (cx: number, cy: number, r: number, angle: number) => {
  const rad = (angle * Math.PI) / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}

const placeBet = () => {
  if (!selectedGift.value) return
  showBetModal.value = false
  selectedGift.value = null
}

let pollInterval: number | null = null

onMounted(() => {
  pollInterval = window.setInterval(() => {
    onlineCount.value = Math.floor(Math.random() * 50) + 80
  }, 5000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.pvp-view {
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
.pvp-header {
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

/* Stats Row */
.stats-row {
  display: flex;
  gap: 8px;
  padding: 0 12px;
  margin-bottom: 12px;
  position: relative;
  z-index: 10;
}

.stat-card {
  flex: 1;
  background: #1c1c1e;
  border-radius: 12px;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #3a3a3c;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  overflow: hidden;
}

.stat-avatar img { width: 100%; height: 100%; object-fit: cover; }

.stat-content { flex: 1; min-width: 0; }
.stat-name { font-size: 11px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-label { font-size: 9px; color: #6b7280; }
.stat-right { text-align: right; }
.stat-amount { font-size: 11px; font-weight: 600; color: #4ade80; }
.stat-chance { font-size: 9px; color: #6b7280; }

/* Pool Bar */
.pool-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 16px;
  position: relative;
  z-index: 10;
}

.pool-icon-btn {
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

.pool-total {
  background: #1c1c1e;
  padding: 8px 20px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pool-label { font-size: 12px; color: #6b7280; }
.pool-value { font-size: 14px; font-weight: 600; color: #4ade80; }

/* Roulette */
.roulette-wrapper {
  position: relative;
  width: 280px;
  height: 280px;
  margin: 0 auto 20px;
  z-index: 10;
}

.roulette-pointer {
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
}

.roulette-wheel {
  width: 100%;
  height: 100%;
  transition: transform 5s cubic-bezier(0.17, 0.67, 0.12, 0.99);
}

.roulette-wheel.spinning {
  transition: transform 8s cubic-bezier(0.17, 0.67, 0.12, 0.99);
}

/* Status */
.status-line {
  text-align: center;
  margin-bottom: 16px;
  position: relative;
  z-index: 10;
}

.status-icon { font-size: 18px; margin-right: 8px; }
.status-text { font-size: 16px; font-weight: 600; }

/* Players */
.players-section {
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.players-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.players-count { font-size: 16px; font-weight: 700; }
.game-id { font-size: 12px; color: #6b7280; }

.players-list { display: flex; flex-direction: column; gap: 8px; }

.player-item {
  background: #1c1c1e;
  border-radius: 14px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.player-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
}

.player-avatar img { width: 100%; height: 100%; object-fit: cover; }

.player-info { flex: 1; min-width: 0; }
.player-name { display: block; font-size: 14px; font-weight: 500; }
.player-role { font-size: 12px; color: #6b7280; }

.player-stats { text-align: right; margin-right: 8px; }
.player-chance { display: block; font-size: 14px; font-weight: 600; }
.player-bet { font-size: 12px; color: #6b7280; }

.player-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.player-arrow { color: #6b7280; }

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  position: relative;
  z-index: 10;
}

.filter-btns { display: flex; gap: 8px; }

.filter-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.filter-btn.red { background: #dc2626; }
.filter-btn.blue { background: #3b82f6; }
.filter-btn.yellow { background: #eab308; }

.balance-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1c1c1e;
  padding: 10px 14px;
  border-radius: 14px;
}

.balance-icon { font-size: 16px; }
.balance-value { font-size: 14px; font-weight: 600; }

.balance-add {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 16px;
}

/* Action Row */
.action-row {
  display: flex;
  gap: 12px;
  padding: 0 16px;
  margin-bottom: 16px;
  position: relative;
  z-index: 10;
}

.btn-add {
  flex: 1;
  background: #facc15;
  color: #000;
  border: none;
  padding: 16px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
}

.btn-pool {
  flex: 1;
  background: #3b82f6;
  color: #fff;
  border: none;
  padding: 16px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Hash Footer */
.hash-footer {
  text-align: center;
  padding: 0 16px 20px;
  position: relative;
  z-index: 10;
}

.hash-hint { display: block; font-size: 13px; color: #6b7280; margin-bottom: 8px; }

.hash-row {
  font-size: 12px;
  color: #4b5563;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.hash-copy { background: none; border: none; color: #6b7280; font-size: 14px; }

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

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.bet-modal {
  width: 100%;
  max-width: 500px;
  background: #1c1c1e;
  border-radius: 24px 24px 0 0;
  padding: 16px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-handle {
  width: 40px;
  height: 4px;
  background: #3a3a3c;
  border-radius: 2px;
  margin: 0 auto 16px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-header h3 { font-size: 18px; font-weight: 600; }

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3a3a3c;
  border: none;
  color: #fff;
  font-size: 20px;
}

.modal-tabs {
  display: flex;
  background: #27272a;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 16px;
}

.tab {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tab.active { background: #3a3a3c; color: #fff; }

.modal-search {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #27272a;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.modal-search input {
  flex: 1;
  background: none;
  border: none;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.modal-search input::placeholder { color: #6b7280; }

.gifts-section { margin-bottom: 20px; }
.section-title { font-size: 14px; font-weight: 600; margin-bottom: 12px; }

.gifts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.gift-card {
  background: #27272a;
  border-radius: 14px;
  padding: 12px;
  text-align: center;
  position: relative;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.gift-card.selected { border-color: #3b82f6; }

.gift-radio {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 18px;
  height: 18px;
  border: 2px solid #4b5563;
  border-radius: 50%;
}

.gift-radio.checked { border-color: #3b82f6; background: #3b82f6; }

.gift-img {
  width: 56px;
  height: 56px;
  object-fit: contain;
  margin-bottom: 8px;
}

.gift-name {
  display: block;
  font-size: 11px;
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gift-price { font-size: 10px; color: #facc15; }

.modal-submit {
  width: 100%;
  background: #fff;
  color: #000;
  border: none;
  padding: 16px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
}

.modal-submit:disabled { background: #3a3a3c; color: #6b7280; }

/* Winner Modal */
.winner-modal {
  width: calc(100% - 32px);
  max-width: 400px;
  background: #1c1c1e;
  border-radius: 20px;
  padding: 20px;
  margin: auto;
}

.winner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.winner-header h3 { font-size: 16px; font-weight: 600; }

.winner-content {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.winner-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #3a3a3c;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.winner-info { flex: 1; }
.winner-name { display: block; font-size: 14px; font-weight: 500; }
.winner-label { font-size: 12px; color: #6b7280; }

.winner-prize { text-align: right; }
.prize-amount { display: block; font-size: 14px; font-weight: 600; color: #4ade80; }
.prize-chance { font-size: 12px; color: #6b7280; }

.winner-gift { margin-bottom: 20px; text-align: center; }

.gift-won {
  width: 80px;
  height: 80px;
  background: #27272a;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.gift-icon { font-size: 32px; }
.gift-value { font-size: 14px; color: #3b82f6; }

.btn-done {
  width: 100%;
  background: #fff;
  color: #000;
  border: none;
  padding: 16px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
}
</style>
