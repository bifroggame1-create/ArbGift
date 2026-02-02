<template>
  <div class="profile-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 20" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="profile-header">
      <div class="header-title">Профиль</div>
      <button class="settings-btn">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
        </svg>
      </button>
    </header>

    <!-- User Card -->
    <div class="user-card">
      <div class="user-avatar" :style="{ background: avatarGradient }">
        <span>{{ userInitial }}</span>
      </div>
      <div class="user-info">
        <h2 class="user-name">@{{ username }}</h2>
        <span class="user-id">ID: {{ userId }}</span>
      </div>
      <div class="user-badge vip" v-if="isVip">
        <span>⭐ VIP</span>
      </div>
    </div>

    <!-- Balance Card -->
    <div class="balance-card">
      <div class="balance-row">
        <div class="balance-item">
          <span class="balance-icon">💎</span>
          <div class="balance-info">
            <span class="balance-label">TON Баланс</span>
            <span class="balance-value">{{ tonBalance.toFixed(2) }} TON</span>
          </div>
        </div>
        <div class="balance-divider"></div>
        <div class="balance-item">
          <span class="balance-icon">⭐</span>
          <div class="balance-info">
            <span class="balance-label">Stars</span>
            <span class="balance-value">{{ starsBalance }} Stars</span>
          </div>
        </div>
      </div>
      <div class="balance-actions">
        <button class="btn-deposit" @click="$router.push('/topup')">
          <span>+</span> Пополнить
        </button>
        <button class="btn-withdraw">
          <span>↓</span> Вывести
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-section">
      <h3 class="section-title">📊 Статистика</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-icon">🎁</span>
          <span class="stat-value">{{ stats.totalGifts }}</span>
          <span class="stat-label">Гифтов</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">🎮</span>
          <span class="stat-value">{{ stats.gamesPlayed }}</span>
          <span class="stat-label">Игр</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">🏆</span>
          <span class="stat-value">{{ stats.wins }}</span>
          <span class="stat-label">Побед</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">💰</span>
          <span class="stat-value">{{ stats.totalWon.toFixed(1) }}</span>
          <span class="stat-label">TON выиграно</span>
        </div>
      </div>
    </div>

    <!-- Referral Section -->
    <div class="referral-section">
      <div class="referral-header">
        <h3 class="section-title">👥 Реферальная программа</h3>
        <span class="referral-bonus">+10%</span>
      </div>
      <div class="referral-card">
        <div class="referral-stats">
          <div class="ref-stat">
            <span class="ref-value">{{ referrals.count }}</span>
            <span class="ref-label">Приглашено</span>
          </div>
          <div class="ref-stat">
            <span class="ref-value">{{ referrals.earned.toFixed(2) }} TON</span>
            <span class="ref-label">Заработано</span>
          </div>
        </div>
        <div class="referral-link">
          <input
            type="text"
            :value="referralLink"
            readonly
            class="link-input"
          />
          <button class="copy-btn" @click="copyReferralLink">
            📋
          </button>
        </div>
        <button class="btn-share">
          <span>📤</span> Пригласить друзей
        </button>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="activity-section">
      <h3 class="section-title">📜 Последняя активность</h3>
      <div v-if="recentActivity.length > 0" class="activity-list">
        <div
          v-for="activity in recentActivity"
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon" :class="activity.type">
            {{ activity.icon }}
          </div>
          <div class="activity-info">
            <span class="activity-title">{{ activity.title }}</span>
            <span class="activity-time">{{ activity.time }}</span>
          </div>
          <span class="activity-amount" :class="{ positive: activity.amount > 0 }">
            {{ activity.amount > 0 ? '+' : '' }}{{ activity.amount }} TON
          </span>
        </div>
      </div>
      <div v-else class="empty-activity">
        <span>Нет активности</span>
      </div>
    </div>

    <!-- Menu Items -->
    <div class="menu-section">
      <button class="menu-item" @click="$router.push('/inventory')">
        <span class="menu-icon">📦</span>
        <span class="menu-label">Мой инвентарь</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
      <button class="menu-item">
        <span class="menu-icon">📜</span>
        <span class="menu-label">История транзакций</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
      <button class="menu-item">
        <span class="menu-icon">🔔</span>
        <span class="menu-label">Уведомления</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
      <button class="menu-item">
        <span class="menu-icon">🛡️</span>
        <span class="menu-label">Безопасность</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
      <button class="menu-item">
        <span class="menu-icon">❓</span>
        <span class="menu-label">Помощь</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
    </div>

    <!-- Version -->
    <div class="version-info">
      <span>Gift Aggregator v1.0.0</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import { useTonConnect } from '../composables/useTonConnect'
import { stakingGetStats } from '../api/client'

interface Activity {
  id: number
  type: 'win' | 'loss' | 'deposit' | 'withdraw'
  icon: string
  title: string
  time: string
  amount: number
}

const { user, initWebApp } = useTelegram()
const tonConnect = useTonConnect()

// User data from Telegram
const username = computed(() => user.value?.username || user.value?.first_name || 'Player')
const userId = computed(() => String(user.value?.id || ''))
const userInitial = computed(() => username.value.charAt(0).toUpperCase())
const isVip = ref(false)

const avatarGradient = 'linear-gradient(135deg, #3b82f6, #8b5cf6)'

// Balance
const tonBalance = ref(0)
const starsBalance = ref(0)

// Stats
const stats = ref({
  totalGifts: 0,
  gamesPlayed: 0,
  wins: 0,
  totalWon: 0
})

// Referrals
const referrals = ref({
  count: 0,
  earned: 0
})

const referralLink = computed(() => {
  const id = user.value?.id || ''
  return `t.me/giftbot?start=ref${id}`
})

// Activity
const recentActivity = ref<Activity[]>([])

// Stars background
const getStarStyle = (_i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

const copyReferralLink = () => {
  navigator.clipboard.writeText(referralLink.value)
}

onMounted(async () => {
  initWebApp()
  await tonConnect.init('giftmarket_bot')

  // Load staking stats if user is available
  if (user.value?.id) {
    try {
      const stakingStats = await stakingGetStats(user.value.id)
      stats.value.totalWon = parseFloat(stakingStats.total_rewards_earned_ton || '0')
    } catch (e) {
      // Stats not available yet
    }
  }
})
</script>

<style scoped>
.profile-view {
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
.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  position: relative;
  z-index: 10;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
}

.settings-btn {
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

/* User Card */
.user-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 16px 20px;
  position: relative;
  z-index: 10;
}

.user-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
}

.user-id {
  font-size: 12px;
  color: #6b7280;
}

.user-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.user-badge.vip {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: #000;
}

/* Balance Card */
.balance-card {
  margin: 0 16px 20px;
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

.balance-actions {
  display: flex;
  gap: 10px;
}

.btn-deposit, .btn-withdraw {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-deposit {
  background: #facc15;
  color: #000;
}

.btn-withdraw {
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  color: #fff;
}

/* Section Title */
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px;
}

/* Stats Section */
.stats-section {
  padding: 0 16px 20px;
  position: relative;
  z-index: 10;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.stat-card {
  background: #1c1c1e;
  border-radius: 14px;
  padding: 14px 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.stat-icon {
  font-size: 20px;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
}

.stat-label {
  font-size: 10px;
  color: #6b7280;
}

/* Referral Section */
.referral-section {
  padding: 0 16px 20px;
  position: relative;
  z-index: 10;
}

.referral-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.referral-bonus {
  background: #22c55e;
  color: #fff;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}

.referral-card {
  background: #1c1c1e;
  border-radius: 16px;
  padding: 16px;
}

.referral-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.ref-stat {
  display: flex;
  flex-direction: column;
}

.ref-value {
  font-size: 18px;
  font-weight: 700;
}

.ref-label {
  font-size: 11px;
  color: #6b7280;
}

.referral-link {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.link-input {
  flex: 1;
  background: #27272a;
  border: 1px solid #3a3a3c;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 12px;
  color: #9ca3af;
  font-family: monospace;
}

.copy-btn {
  width: 42px;
  height: 42px;
  background: #27272a;
  border: 1px solid #3a3a3c;
  border-radius: 10px;
  font-size: 16px;
}

.btn-share {
  width: 100%;
  padding: 12px;
  background: #3b82f6;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Activity Section */
.activity-section {
  padding: 0 16px 20px;
  position: relative;
  z-index: 10;
}

.activity-list {
  background: #1c1c1e;
  border-radius: 16px;
  overflow: hidden;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-bottom: 1px solid #27272a;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: #27272a;
}

.activity-icon.win { background: rgba(34, 197, 94, 0.2); }
.activity-icon.loss { background: rgba(239, 68, 68, 0.2); }
.activity-icon.deposit { background: rgba(59, 130, 246, 0.2); }

.activity-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.activity-title {
  font-size: 13px;
  font-weight: 500;
}

.activity-time {
  font-size: 11px;
  color: #6b7280;
}

.activity-amount {
  font-size: 13px;
  font-weight: 600;
  color: #ef4444;
}

.activity-amount.positive {
  color: #4ade80;
}

.empty-activity {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

/* Menu Section */
.menu-section {
  padding: 0 16px 20px;
  position: relative;
  z-index: 10;
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #1c1c1e;
  border: none;
  border-radius: 14px;
  margin-bottom: 8px;
  color: #fff;
  text-align: left;
}

.menu-icon {
  font-size: 20px;
}

.menu-label {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.menu-item svg {
  color: #6b7280;
}

/* Version */
.version-info {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: #4b5563;
  position: relative;
  z-index: 10;
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
