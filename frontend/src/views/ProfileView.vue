<template>
  <div class="mb-profile">
    <!-- Cyan gradient header background -->
    <div class="mb-gradient-header"></div>

    <!-- Play Balance Section -->
    <div class="mb-balance-section">
      <span class="mb-balance-label">Play Balance</span>
      <div class="mb-balance-row">
        <span class="mb-balance-value">{{ tonBalance.toFixed(2) }}</span>
        <svg class="mb-ton-icon" width="28" height="28" viewBox="0 0 56 56" fill="none">
          <circle cx="28" cy="28" r="28" fill="#0098EA"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
        </svg>
      </div>
    </div>

    <!-- Action Circles Row -->
    <div class="mb-actions-row">
      <router-link to="/stars" class="mb-action-item" style="text-decoration:none;color:inherit">
        <div class="mb-action-circle">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#FFCE4F" stroke="#FFCE4F" stroke-width="1"/>
          </svg>
        </div>
        <span class="mb-action-label">Top Up Stars</span>
      </router-link>
      <button class="mb-action-item" @click="openDepositModal">
        <div class="mb-action-circle">
          <svg width="24" height="24" viewBox="0 0 56 56" fill="none">
            <circle cx="28" cy="28" r="28" fill="#0098EA"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
          </svg>
        </div>
        <span class="mb-action-label">Top Up TON</span>
      </button>
      <button class="mb-action-item" @click="$router.push('/inventory')">
        <div class="mb-action-circle">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="8" width="18" height="13" rx="2"/>
            <path d="M16 8V6a4 4 0 0 0-8 0v2"/>
            <path d="M12 14v2"/>
            <circle cx="12" cy="14" r="1"/>
          </svg>
        </div>
        <span class="mb-action-label">Deposit Gifts</span>
      </button>
    </div>

    <!-- User Section -->
    <div class="mb-user-section">
      <div class="mb-user-row">
        <div class="mb-user-avatar" :style="{ background: avatarGradient }">
          <span>{{ userInitial }}</span>
        </div>
        <div class="mb-user-info">
          <span class="mb-username">@{{ username }}</span>
        </div>
        <button class="mb-settings-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- My Inventory Card -->
    <div class="mb-card mb-inventory-card">
      <div class="mb-inventory-header">
        <span class="mb-inventory-title">My Inventory</span>
        <div class="mb-inventory-meta">
          <span class="mb-inventory-count">{{ stats.totalGifts }} Items</span>
          <span class="mb-inventory-value">
            {{ stats.totalWon.toFixed(1) }}
            <svg width="12" height="12" viewBox="0 0 56 56" fill="none" style="vertical-align: middle; margin-left: 2px;">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
          </span>
        </div>
      </div>
      <div class="mb-inventory-grid">
        <div class="mb-inventory-placeholder" v-for="i in 3" :key="i">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="8" width="18" height="13" rx="2"/>
            <path d="M16 8V6a4 4 0 0 0-8 0v2"/>
          </svg>
        </div>
      </div>
      <router-link to="/inventory" class="mb-inventory-link">
        <span>All Items</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </router-link>
      <div class="mb-inventory-empty">
        <span class="mb-empty-text">You have no items yet.</span>
        <router-link to="/inventory" class="mb-deposit-link">
          Deposit Gift
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </router-link>
      </div>
    </div>

    <!-- Referral Card -->
    <div class="mb-card mb-referral-card">
      <div class="mb-referral-content">
        <div class="mb-referral-text-block">
          <p class="mb-referral-description">
            Invite referrals to earn
            <span class="mb-referral-badge">10%</span>
            of their game fees
          </p>
        </div>
        <div class="mb-referral-illustration">
          <svg width="72" height="72" viewBox="0 0 80 80" fill="none">
            <circle cx="40" cy="32" r="16" fill="#22C55E" opacity="0.3"/>
            <circle cx="40" cy="32" r="10" fill="#22C55E" opacity="0.6"/>
            <circle cx="40" cy="28" r="8" fill="#22C55E"/>
            <rect x="32" y="40" width="16" height="20" rx="4" fill="#22C55E" opacity="0.8"/>
            <circle cx="60" cy="28" r="6" fill="#4ADE80" opacity="0.5"/>
            <rect x="57" y="22" width="6" height="1.5" rx="0.75" fill="#fff" opacity="0.8"/>
            <rect x="59.25" y="19.75" width="1.5" height="6" rx="0.75" fill="#fff" opacity="0.8"/>
          </svg>
        </div>
      </div>
      <div class="mb-referral-actions">
        <button class="mb-btn-invite" @click="shareReferralLink">
          Invite Friends
        </button>
        <button class="mb-btn-copy" @click="copyReferralLink">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Claim Section -->
    <div class="mb-card mb-claim-card">
      <div class="mb-claim-header">
        <svg class="mb-claim-ton-icon" width="32" height="32" viewBox="0 0 56 56" fill="none">
          <circle cx="28" cy="28" r="28" fill="#0098EA"/>
          <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
        </svg>
        <div class="mb-claim-amounts">
          <span class="mb-claim-value">{{ referrals.earned.toFixed(2) }} TON</span>
          <span class="mb-claim-label">Claimable amount</span>
        </div>
      </div>
      <div class="mb-claim-stats">
        <div class="mb-claim-stat">
          <span class="mb-claim-stat-value">{{ referrals.count }}</span>
          <span class="mb-claim-stat-label">Invited users</span>
        </div>
        <div class="mb-claim-stat">
          <span class="mb-claim-stat-value">{{ referrals.earned.toFixed(2) }}</span>
          <span class="mb-claim-stat-label">Total claimed amount</span>
        </div>
      </div>
      <button class="mb-btn-claim" :disabled="referrals.earned <= 0">
        Claim
      </button>
    </div>

    <!-- Spacer for bottom nav -->
    <div class="mb-bottom-spacer"></div>

    <!-- Deposit Modal -->
    <Teleport to="body">
      <div v-if="showDepositModal" class="mb-modal-overlay" @click.self="closeDepositModal">
        <div class="mb-modal-content">
          <div class="mb-modal-header">
            <h3 class="mb-modal-title">
              <svg width="18" height="18" viewBox="0 0 56 56" fill="none">
                <circle cx="28" cy="28" r="28" fill="#0098EA"/>
                <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
              </svg>
              Top Up TON
            </h3>
            <button class="mb-modal-close" @click="closeDepositModal">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="mb-modal-body">
            <div v-if="!tonConnect.isConnected.value" class="mb-connect-section">
              <p class="mb-modal-text">Connect wallet to see deposit address</p>
              <button class="mb-btn-connect" @click="connectWallet" :disabled="tonConnect.isConnecting.value">
                {{ tonConnect.isConnecting.value ? 'Connecting...' : 'Connect Wallet' }}
              </button>
            </div>
            <div v-else class="mb-deposit-info">
              <p class="mb-modal-text">Send TON to the project address:</p>
              <div class="mb-address-box">
                <span class="mb-address">{{ projectWalletAddress }}</span>
                <button class="mb-btn-copy-sm" @click="copyProjectAddress">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2"/>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                  </svg>
                </button>
              </div>
              <p class="mb-modal-hint">Balance will update automatically after transfer</p>
              <div class="mb-wallet-info">
                <span class="mb-wallet-label">Your wallet:</span>
                <span class="mb-wallet-value">{{ tonConnect.shortAddress.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import { useTonConnect } from '../composables/useTonConnect'
import { stakingGetStats } from '../api/client'


const { user, initWebApp } = useTelegram()
const tonConnect = useTonConnect()

// User data from Telegram
const username = computed(() => user.value?.username || user.value?.first_name || 'Player')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())

const avatarGradient = 'linear-gradient(135deg, #3b82f6, #8b5cf6)'

// Balance
const tonBalance = ref(0)

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

// Deposit Modal
const showDepositModal = ref(false)
const projectWalletAddress = 'UQBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' // TODO: Replace with actual project wallet

const openDepositModal = () => {
  showDepositModal.value = true
}

const closeDepositModal = () => {
  showDepositModal.value = false
}


const connectWallet = async () => {
  try {
    await tonConnect.connect()
  } catch (e) {
    console.error('Wallet connection failed:', e)
  }
}

const copyProjectAddress = () => {
  navigator.clipboard.writeText(projectWalletAddress)
}

const copyReferralLink = () => {
  navigator.clipboard.writeText(referralLink.value)
}

const shareReferralLink = () => {
  const text = 'Join me and play! Use my referral link:'
  const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(referralLink.value)}&text=${encodeURIComponent(text)}`
  if (window.Telegram?.WebApp?.openTelegramLink) {
    window.Telegram.WebApp.openTelegramLink(shareUrl)
  } else {
    window.open(shareUrl, '_blank')
  }
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
/* ============================================
   MyBalls.io Profile Design System
   ============================================ */

/* CSS Variables */
.mb-profile {
  --mb-bg: #0C0C0C;
  --mb-primary: #34CDEF;
  --mb-card: rgba(255, 255, 255, 0.05);
  --mb-card-border: rgba(255, 255, 255, 0.08);
  --mb-gradient-cyan: linear-gradient(180deg, rgba(52, 205, 239, 0.3) 0%, rgba(12, 12, 12, 0) 50%);
  --mb-text-secondary: rgba(255, 255, 255, 0.5);
  --mb-text-tertiary: rgba(255, 255, 255, 0.3);
  --mb-radius-lg: 16px;
  --mb-radius-md: 12px;
  --mb-radius-sm: 8px;
  --mb-font-mono: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  --mb-green: #22C55E;
}

.mb-profile {
  min-height: 100vh;
  background: var(--mb-bg);
  color: #fff;
  position: relative;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', system-ui, sans-serif;
}

/* Cyan Gradient Header */
.mb-gradient-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 300px;
  background: var(--mb-gradient-cyan);
  pointer-events: none;
  z-index: 0;
}

/* ============================================
   Play Balance Section
   ============================================ */
.mb-balance-section {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 16px 24px;
}

.mb-balance-label {
  font-size: 13px;
  color: var(--mb-primary);
  font-weight: 500;
  letter-spacing: 0.02em;
  margin-bottom: 4px;
}

.mb-balance-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mb-balance-value {
  font-size: 40px;
  font-weight: 700;
  font-family: var(--mb-font-mono);
  color: #fff;
  line-height: 1.1;
}

.mb-ton-icon {
  flex-shrink: 0;
}

/* ============================================
   Action Circles Row
   ============================================ */
.mb-actions-row {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  gap: 28px;
  padding: 0 16px 28px;
}

.mb-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.mb-action-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
}

.mb-action-item:active .mb-action-circle {
  transform: scale(0.93);
  background: rgba(255, 255, 255, 0.08);
}

.mb-action-label {
  font-size: 10px;
  color: var(--mb-text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

/* ============================================
   User Section
   ============================================ */
.mb-user-section {
  position: relative;
  z-index: 1;
  padding: 0 16px 20px;
}

.mb-user-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mb-user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.mb-user-info {
  flex: 1;
  min-width: 0;
}

.mb-username {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mb-settings-btn {
  width: 40px;
  height: 40px;
  background: var(--mb-card);
  border: 1px solid var(--mb-card-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s;
}

.mb-settings-btn:active {
  background: rgba(255, 255, 255, 0.1);
}

/* ============================================
   Card Base
   ============================================ */
.mb-card {
  position: relative;
  z-index: 1;
  margin: 0 16px 16px;
  background: var(--mb-card);
  border: 1px solid var(--mb-card-border);
  border-radius: var(--mb-radius-lg);
  overflow: hidden;
}

/* ============================================
   Inventory Card
   ============================================ */
.mb-inventory-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 12px;
}

.mb-inventory-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.mb-inventory-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mb-inventory-count {
  font-size: 13px;
  color: var(--mb-text-secondary);
}

.mb-inventory-value {
  font-size: 13px;
  color: var(--mb-text-secondary);
  display: flex;
  align-items: center;
}

.mb-inventory-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 0 16px;
}

.mb-inventory-placeholder {
  aspect-ratio: 1;
  border: 1.5px dashed rgba(255, 255, 255, 0.1);
  border-radius: var(--mb-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.02);
}

.mb-inventory-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 14px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--mb-primary);
  text-decoration: none;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  margin-top: 12px;
  transition: opacity 0.2s;
}

.mb-inventory-link:active {
  opacity: 0.7;
}

.mb-inventory-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px 16px;
}

.mb-empty-text {
  font-size: 12px;
  color: var(--mb-text-tertiary);
}

.mb-deposit-link {
  font-size: 12px;
  color: var(--mb-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 2px;
  font-weight: 500;
}

.mb-deposit-link:active {
  opacity: 0.7;
}

/* ============================================
   Referral Card
   ============================================ */
.mb-referral-card {
  padding: 20px 16px 16px;
}

.mb-referral-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.mb-referral-text-block {
  flex: 1;
}

.mb-referral-description {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  line-height: 1.4;
  margin: 0;
}

.mb-referral-badge {
  display: inline-block;
  background: var(--mb-green);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  vertical-align: middle;
  margin: 0 2px;
}

.mb-referral-illustration {
  flex-shrink: 0;
}

.mb-referral-actions {
  display: flex;
  gap: 10px;
}

.mb-btn-invite {
  flex: 1;
  padding: 14px;
  background: #fff;
  color: #000;
  border: none;
  border-radius: var(--mb-radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
}

.mb-btn-invite:active {
  transform: scale(0.97);
  opacity: 0.9;
}

.mb-btn-copy {
  width: 48px;
  height: 48px;
  background: var(--mb-card);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--mb-radius-md);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s;
}

.mb-btn-copy:active {
  background: rgba(255, 255, 255, 0.1);
}

/* ============================================
   Claim Section
   ============================================ */
.mb-claim-card {
  padding: 20px 16px 16px;
}

.mb-claim-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.mb-claim-ton-icon {
  flex-shrink: 0;
}

.mb-claim-amounts {
  display: flex;
  flex-direction: column;
}

.mb-claim-value {
  font-size: 20px;
  font-weight: 700;
  font-family: var(--mb-font-mono);
  color: #fff;
}

.mb-claim-label {
  font-size: 12px;
  color: var(--mb-text-secondary);
  margin-top: 2px;
}

.mb-claim-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.mb-claim-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mb-claim-stat-value {
  font-size: 16px;
  font-weight: 600;
  font-family: var(--mb-font-mono);
  color: #fff;
}

.mb-claim-stat-label {
  font-size: 11px;
  color: var(--mb-text-secondary);
}

.mb-btn-claim {
  width: 100%;
  padding: 14px;
  background: var(--mb-card);
  border: 1px solid var(--mb-card-border);
  border-radius: var(--mb-radius-md);
  font-size: 14px;
  font-weight: 600;
  color: var(--mb-text-secondary);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.mb-btn-claim:disabled {
  cursor: not-allowed;
  color: var(--mb-text-tertiary);
}

.mb-btn-claim:not(:disabled):active {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* ============================================
   Bottom Spacer
   ============================================ */
.mb-bottom-spacer {
  height: 100px;
}

/* ============================================
   Modal Styles
   ============================================ */
.mb-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.mb-modal-content {
  background: #1A1A1A;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  width: 100%;
  max-width: 360px;
  overflow: hidden;
}

.mb-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.mb-modal-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mb-modal-close {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.mb-modal-close:active {
  background: rgba(255, 255, 255, 0.12);
}

.mb-modal-body {
  padding: 20px;
}

.mb-modal-text {
  font-size: 14px;
  color: var(--mb-text-secondary);
  margin: 0 0 16px;
  text-align: center;
}

.mb-modal-hint {
  font-size: 12px;
  color: var(--mb-text-tertiary);
  text-align: center;
  margin-top: 12px;
}

/* Connect Section */
.mb-connect-section {
  text-align: center;
}

.mb-btn-connect {
  width: 100%;
  padding: 14px;
  background: var(--mb-primary);
  border: none;
  border-radius: var(--mb-radius-md);
  color: #000;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.mb-btn-connect:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Deposit Info */
.mb-deposit-info {
  text-align: center;
}

.mb-address-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--mb-radius-md);
  padding: 12px;
  margin-bottom: 12px;
}

.mb-address {
  flex: 1;
  font-family: var(--mb-font-mono);
  font-size: 11px;
  color: var(--mb-text-secondary);
  word-break: break-all;
  text-align: left;
}

.mb-btn-copy-sm {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: var(--mb-radius-sm);
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.mb-wallet-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.mb-wallet-label {
  font-size: 12px;
  color: var(--mb-text-secondary);
}

.mb-wallet-value {
  font-size: 12px;
  font-family: var(--mb-font-mono);
  color: var(--mb-green);
}

/* Stars Modal Grid */
.mb-stars-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}

.mb-stars-pkg {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--mb-radius-md);
  color: #fff;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.mb-stars-pkg.selected {
  border-color: var(--mb-primary);
  background: rgba(52, 205, 239, 0.08);
}

.mb-pkg-amount {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

.mb-pkg-price {
  font-size: 12px;
  color: var(--mb-text-secondary);
}

.mb-btn-buy {
  width: 100%;
  padding: 14px;
  background: var(--mb-primary);
  border: none;
  border-radius: var(--mb-radius-md);
  color: #000;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.mb-btn-buy:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
