<template>
  <div class="earn-view">
    <!-- Purple gradient header -->
    <div class="earn-header">
      <div class="earn-header__content">
        <!-- Countdown timer -->
        <div class="countdown">
          <div class="countdown__group">
            <span class="countdown__digit">{{ timerDigits.d1 }}</span>
            <span class="countdown__digit">{{ timerDigits.d2 }}</span>
          </div>
          <span class="countdown__sep">:</span>
          <div class="countdown__group">
            <span class="countdown__digit">{{ timerDigits.h1 }}</span>
            <span class="countdown__digit">{{ timerDigits.h2 }}</span>
          </div>
          <span class="countdown__sep">:</span>
          <div class="countdown__group">
            <span class="countdown__digit">{{ timerDigits.m1 }}</span>
            <span class="countdown__digit">{{ timerDigits.m2 }}</span>
          </div>
          <span class="countdown__sep">:</span>
          <div class="countdown__group">
            <span class="countdown__digit">{{ timerDigits.s1 }}</span>
            <span class="countdown__digit">{{ timerDigits.s2 }}</span>
          </div>
        </div>

        <!-- Farming Pool -->
        <div class="farming-pool">
          <div class="farming-pool__label">Farming Pool</div>
          <div class="farming-pool__amount">
            <svg class="farming-pool__ton-icon" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
            <span class="farming-pool__value">{{ farmingPool.toFixed(3) }}</span>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="action-buttons">
          <button class="action-btn" @click="hapticImpact('light')">
            <div class="action-btn__icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <line x1="10" y1="9" x2="8" y2="9"/>
              </svg>
            </div>
            <span class="action-btn__label">Onboarding</span>
          </button>
          <button class="action-btn" @click="hapticImpact('light')">
            <div class="action-btn__icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8 21h8"/>
                <path d="M12 17v4"/>
                <path d="M7 4h10"/>
                <path d="M5 8h14"/>
                <rect x="3" y="12" width="18" height="5" rx="1"/>
              </svg>
            </div>
            <span class="action-btn__label">Leaderboard</span>
          </button>
        </div>
      </div>
    </div>

    <!-- User card -->
    <div class="user-card">
      <div class="user-card__top">
        <div class="user-card__info">
          <div class="user-card__avatar">
            <span>{{ userInitial }}</span>
          </div>
          <div class="user-card__details">
            <div class="user-card__name">@{{ username }}</div>
            <div class="user-card__balance">Balance: <span>{{ userBalance }} BP</span></div>
          </div>
        </div>
        <div class="user-card__rank">
          Top {{ userRank }} <span class="user-card__rank-total">/{{ totalUsers }}</span>
        </div>
      </div>
      <button class="user-card__cta" @click="hapticImpact('medium')">
        Farm more to win the prize
      </button>
    </div>

    <!-- Modules section -->
    <div class="modules">
      <h2 class="modules__title">Modules</h2>

      <div class="modules__list">
        <!-- Tasks module -->
        <div class="module-card module-card--tasks" @click="hapticImpact('light')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap module-card__icon-wrap--tasks">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 11l3 3L22 4"/>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
            </div>
            <div class="module-card__bp">{{ tasksEarned }} BP</div>
          </div>
          <div class="module-card__title">Tasks</div>
          <div class="module-card__subtitle">{{ tasksCompleted }} / {{ tasksTotal }} tasks completed</div>
          <div class="module-card__link">Open Tasks</div>
        </div>

        <!-- Gift Staking module - 600% APR -->
        <router-link to="/staking" class="module-card module-card--staking" @click.native="hapticImpact('medium')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap module-card__icon-wrap--staking">
              🎁
            </div>
            <div class="module-card__apr">🔥 600% APR</div>
          </div>
          <div class="module-card__title">Gift Staking</div>
          <div class="module-card__subtitle--hot">Stake gifts, earn up to 3000% effective APR!</div>
          <div class="module-card__progress">
            <div class="progress-bar progress-bar--staking">
              <div class="progress-bar__fill progress-bar__fill--staking" :style="{ width: stakingProgress + '%' }"></div>
            </div>
          </div>
          <div class="module-card__link">Open Staking →</div>
        </router-link>

        <!-- Ice Arena module -->
        <div class="module-card" @click="hapticImpact('light')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
            </div>
            <div class="module-card__badge">LvL {{ arenaLevel }}</div>
          </div>
          <div class="module-card__title">Ice Arena</div>
          <div class="module-card__progress">
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: arenaProgress + '%' }"></div>
            </div>
          </div>
          <div class="module-card__subtitle">{{ arenaCurrentTon }} / {{ arenaNextLvlTon }} <img src="/images/ton_symbol.svg" width="10" height="10" style="display:inline-block;vertical-align:middle" /> next LvL</div>
        </div>

        <!-- Ball Race module -->
        <div class="module-card" @click="hapticImpact('light')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
                <path d="M2 12h20"/>
              </svg>
            </div>
            <div class="module-card__badge">LvL {{ ballRaceLevel }}</div>
          </div>
          <div class="module-card__title">Ball Race</div>
          <div class="module-card__rate">{{ ballRaceRate }} BP/h</div>
          <div class="module-card__progress">
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: ballRaceProgress + '%' }"></div>
            </div>
          </div>
          <div class="module-card__earned">+{{ ballRaceEarned }} BP</div>
        </div>

        <!-- Trading PnL module -->
        <div class="module-card" @click="hapticImpact('light')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
                <polyline points="16 7 22 7 22 13"/>
              </svg>
            </div>
            <div class="module-card__badge">LvL {{ tradingLevel }}</div>
          </div>
          <div class="module-card__title">Trading PnL</div>
          <div class="module-card__rate">{{ tradingRate }} BP/h</div>
          <div class="module-card__progress">
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: tradingProgress + '%' }"></div>
            </div>
          </div>
          <div class="module-card__earned">+{{ tradingEarned }} BP</div>
        </div>

        <!-- Ball Escape module -->
        <div class="module-card" @click="hapticImpact('light')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </div>
            <div class="module-card__badge">LvL {{ escapeLevel }}</div>
          </div>
          <div class="module-card__title">Ball Escape</div>
          <div class="module-card__rate">{{ escapeRate }} BP/h</div>
          <div class="module-card__progress">
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: escapeProgress + '%' }"></div>
            </div>
          </div>
          <div class="module-card__earned">+{{ escapeEarned }} BP</div>
        </div>

        <!-- Gift Plinko module -->
        <div class="module-card" @click="hapticImpact('light')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div class="module-card__badge">LvL {{ plinkoLevel }}</div>
          </div>
          <div class="module-card__title">Gift Plinko</div>
          <div class="module-card__rate">{{ plinkoRate }} BP/h</div>
          <div class="module-card__progress">
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: plinkoProgress + '%' }"></div>
            </div>
          </div>
          <div class="module-card__earned">+{{ plinkoEarned }} BP</div>
        </div>

        <!-- Gonka module -->
        <div class="module-card" @click="hapticImpact('light')">
          <div class="module-card__header">
            <div class="module-card__icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 8h1a4 4 0 1 1 0 8h-1"/>
                <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V8z"/>
                <line x1="6" y1="2" x2="6" y2="4"/>
                <line x1="10" y1="2" x2="10" y2="4"/>
                <line x1="14" y1="2" x2="14" y2="4"/>
              </svg>
            </div>
            <div class="module-card__badge">LvL {{ gonkaLevel }}</div>
          </div>
          <div class="module-card__title">Gonka</div>
          <div class="module-card__rate">{{ gonkaRate }} BP/h</div>
          <div class="module-card__progress">
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: gonkaProgress + '%' }"></div>
            </div>
          </div>
          <div class="module-card__earned">+{{ gonkaEarned }} BP</div>
        </div>
      </div>
    </div>

    <!-- Bottom spacer for tab bar -->
    <div class="earn-view__spacer"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import { stakingGetStats, stakingGetUserStakes } from '../api/client'

const { user, initWebApp, hapticImpact } = useTelegram()

// --- Farming pool & timer ---
const farmingPool = ref(3441.017)

// Countdown: target = end of current season (stub: 3 days from now)
const targetTime = ref(Date.now() + 3 * 24 * 60 * 60 * 1000)
const now = ref(Date.now())
let timerInterval: ReturnType<typeof setInterval> | null = null

const timerDigits = computed(() => {
  const diff = Math.max(0, targetTime.value - now.value)
  const totalSec = Math.floor(diff / 1000)
  const d = Math.floor(totalSec / 86400)
  const h = Math.floor((totalSec % 86400) / 3600)
  const m = Math.floor((totalSec % 3600) / 60)
  const s = totalSec % 60
  const pad = (n: number) => String(n).padStart(2, '0')
  const dd = pad(d)
  const hh = pad(h)
  const mm = pad(m)
  const ss = pad(s)
  return {
    d1: dd[0], d2: dd[1],
    h1: hh[0], h2: hh[1],
    m1: mm[0], m2: mm[1],
    s1: ss[0], s2: ss[1],
  }
})

// --- User card ---
const username = ref('user')
const userInitial = computed(() => (username.value[0] || 'U').toUpperCase())
const userBalance = ref(0)
const userRank = ref(0)
const totalUsers = ref(0)

// --- Staking data from API ---
const totalEarned = ref(0)
const dailyRate = ref(0)

// --- Tasks ---
const tasksEarned = ref(0)
const tasksCompleted = ref(0)
const tasksTotal = ref(10)

// --- Module states ---
const stakingLevel = ref(0)
const stakingRate = ref(0)
const stakingProgress = ref(0)
const stakingEarned = ref(0)

const arenaLevel = ref(0)
const arenaProgress = ref(50)
const arenaCurrentTon = ref(0.5)
const arenaNextLvlTon = ref(1)

const ballRaceLevel = ref(0)
const ballRaceRate = ref(0)
const ballRaceProgress = ref(0)
const ballRaceEarned = ref(0)

const tradingLevel = ref(0)
const tradingRate = ref(0)
const tradingProgress = ref(0)
const tradingEarned = ref(0)

const escapeLevel = ref(0)
const escapeRate = ref(0)
const escapeProgress = ref(0)
const escapeEarned = ref(0)

const plinkoLevel = ref(0)
const plinkoRate = ref(0)
const plinkoProgress = ref(0)
const plinkoEarned = ref(0)

const gonkaLevel = ref(0)
const gonkaRate = ref(0)
const gonkaProgress = ref(0)
const gonkaEarned = ref(0)

onMounted(async () => {
  initWebApp()

  // Start countdown
  timerInterval = setInterval(() => {
    now.value = Date.now()
  }, 1000)

  // Set username from Telegram
  if (user.value?.username) {
    username.value = user.value.username
  } else if (user.value?.first_name) {
    username.value = user.value.first_name
  }

  if (!user.value?.id) return

  try {
    const [statsData, stakes] = await Promise.all([
      stakingGetStats(user.value.id),
      stakingGetUserStakes(user.value.id, 'active'),
    ])

    totalEarned.value = parseFloat(statsData.total_rewards_earned_ton || '0')
    farmingPool.value = parseFloat(statsData.total_staked_ton || '3441.017')

    // Calculate daily rate from active stakes
    if (stakes.length > 0) {
      const totalDailyReward = stakes.reduce((sum: number, s: any) => {
        const reward = parseFloat(s.estimated_reward_ton || '0')
        const days = s.period_days || 30
        return sum + reward / days
      }, 0)
      dailyRate.value = parseFloat(totalDailyReward.toFixed(4))

      // Update staking module
      stakingLevel.value = Math.min(Math.floor(stakes.length / 2), 10)
      stakingRate.value = Math.round(dailyRate.value * 100)
      stakingEarned.value = Math.round(totalEarned.value * 100)
      stakingProgress.value = Math.min(100, (stakes.length / 10) * 100)
    }

    // Update user balance from staking stats
    userBalance.value = Math.round(totalEarned.value * 100)

    // Check completed tasks
    if (stakes.length > 0) {
      tasksCompleted.value = Math.min(stakes.length, tasksTotal.value)
      tasksEarned.value = tasksCompleted.value * 10
    }
  } catch (e) {
    // Staking data not available — keep defaults
  }
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
})
</script>

<style scoped>
/* === CSS Variables === */
.earn-view {
  --mb-bg: #0C0C0C;
  --mb-primary: #34CDEF;
  --mb-card: rgba(255, 255, 255, 0.05);
  --mb-card-border: rgba(255, 255, 255, 0.08);
  --mb-gradient-purple: linear-gradient(180deg, #7B2FBE 0%, #0C0C0C 100%);
  --mb-text-primary: #FFFFFF;
  --mb-text-secondary: rgba(255, 255, 255, 0.5);
  --mb-text-tertiary: rgba(255, 255, 255, 0.3);
  --mb-radius-lg: 16px;
  --mb-radius-md: 12px;
  --mb-radius-sm: 8px;
  --mb-radius-pill: 100px;

  min-height: 100vh;
  background-color: var(--mb-bg);
  color: var(--mb-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

/* === Header with purple gradient === */
.earn-header {
  background: var(--mb-gradient-purple);
  padding: 0 0 32px;
}

.earn-header__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 20px 0;
}

/* === Countdown Timer === */
.countdown {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 28px;
}

.countdown__group {
  display: flex;
  gap: 3px;
}

.countdown__digit {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--mb-radius-sm);
  font-family: 'SF Mono', 'Menlo', 'Courier New', monospace;
  font-size: 22px;
  font-weight: 700;
  color: var(--mb-text-primary);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.countdown__sep {
  font-family: 'SF Mono', 'Menlo', 'Courier New', monospace;
  font-size: 22px;
  font-weight: 700;
  color: var(--mb-text-secondary);
  margin: 0 2px;
}

/* === Farming Pool === */
.farming-pool {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 28px;
}

.farming-pool__label {
  font-size: 14px;
  font-weight: 500;
  color: var(--mb-text-secondary);
  margin-bottom: 8px;
  letter-spacing: 0.02em;
}

.farming-pool__amount {
  display: flex;
  align-items: center;
  gap: 10px;
}

.farming-pool__ton-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.farming-pool__value {
  font-size: 42px;
  font-weight: 800;
  color: var(--mb-text-primary);
  letter-spacing: -0.02em;
  line-height: 1;
}

/* === Action Buttons === */
.action-buttons {
  display: flex;
  gap: 32px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.action-btn__icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--mb-text-primary);
  transition: background 0.2s ease;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.action-btn:active .action-btn__icon {
  background: rgba(255, 255, 255, 0.2);
}

.action-btn__label {
  font-size: 12px;
  font-weight: 500;
  color: var(--mb-text-secondary);
}

/* === User Card === */
.user-card {
  margin: -16px 16px 24px;
  background: var(--mb-card);
  border: 1px solid var(--mb-card-border);
  border-radius: var(--mb-radius-lg);
  padding: 16px;
  position: relative;
  z-index: 1;
}

.user-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.user-card__info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-card__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7B2FBE, #34CDEF);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: var(--mb-text-primary);
  flex-shrink: 0;
}

.user-card__details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-card__name {
  font-size: 14px;
  font-weight: 600;
  color: var(--mb-text-primary);
}

.user-card__balance {
  font-size: 12px;
  color: var(--mb-text-secondary);
}

.user-card__balance span {
  color: var(--mb-text-primary);
  font-weight: 600;
}

.user-card__rank {
  font-size: 13px;
  font-weight: 600;
  color: var(--mb-text-primary);
}

.user-card__rank-total {
  color: var(--mb-text-secondary);
  font-weight: 400;
}

.user-card__cta {
  width: 100%;
  height: 44px;
  background: var(--mb-primary);
  border: none;
  border-radius: var(--mb-radius-md);
  font-size: 14px;
  font-weight: 600;
  color: #0C0C0C;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: opacity 0.2s ease;
}

.user-card__cta:active {
  opacity: 0.85;
}

/* === Modules Section === */
.modules {
  padding: 0 16px;
}

.modules__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--mb-text-primary);
  margin: 0 0 16px;
}

.modules__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* === Module Card === */
.module-card {
  background: var(--mb-card);
  border: 1px solid var(--mb-card-border);
  border-radius: var(--mb-radius-lg);
  padding: 16px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.2s ease;
}

.module-card:active {
  background: rgba(255, 255, 255, 0.08);
}

/* Tasks card special gradient */
.module-card--tasks {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(239, 68, 68, 0.05) 100%);
  border-color: rgba(239, 68, 68, 0.2);
}

.module-card--tasks:active {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.35) 0%, rgba(239, 68, 68, 0.1) 100%);
}

/* Staking card special gradient - 600% APR */
.module-card--staking {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.35) 0%, rgba(234, 88, 12, 0.15) 100%);
  border-color: rgba(249, 115, 22, 0.4);
  text-decoration: none;
  animation: staking-glow 2s ease-in-out infinite;
}

@keyframes staking-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(249, 115, 22, 0.3); }
  50% { box-shadow: 0 0 30px rgba(249, 115, 22, 0.5); }
}

.module-card--staking:active {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.45) 0%, rgba(234, 88, 12, 0.25) 100%);
}

.module-card__icon-wrap--staking {
  background: rgba(249, 115, 22, 0.3);
  font-size: 20px;
}

.module-card__apr {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #f97316, #ea580c);
  padding: 4px 10px;
  border-radius: var(--mb-radius-pill);
  letter-spacing: 0.02em;
}

.module-card__subtitle--hot {
  font-size: 13px;
  color: #fdba74;
  margin-bottom: 10px;
}

.progress-bar--staking {
  background: rgba(249, 115, 22, 0.2);
}

.progress-bar__fill--staking {
  background: linear-gradient(90deg, #f97316, #ea580c);
}

.module-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.module-card__icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: var(--mb-radius-md);
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--mb-text-primary);
}

.module-card__icon-wrap--tasks {
  background: rgba(239, 68, 68, 0.3);
}

.module-card__bp {
  font-size: 14px;
  font-weight: 700;
  color: var(--mb-text-primary);
}

.module-card__badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--mb-primary);
  background: rgba(52, 205, 239, 0.12);
  padding: 4px 10px;
  border-radius: var(--mb-radius-pill);
  letter-spacing: 0.02em;
}

.module-card__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--mb-text-primary);
  margin-bottom: 4px;
}

.module-card__rate {
  font-size: 13px;
  font-weight: 600;
  color: var(--mb-primary);
  margin-bottom: 10px;
}

.module-card__subtitle {
  font-size: 13px;
  color: var(--mb-text-secondary);
  margin-bottom: 4px;
}

.module-card__link {
  font-size: 13px;
  font-weight: 600;
  color: var(--mb-primary);
  margin-top: 8px;
}

.module-card__earned {
  font-size: 13px;
  font-weight: 600;
  color: var(--mb-text-secondary);
  margin-top: 6px;
  text-align: right;
}

.module-card__progress {
  margin: 8px 0 4px;
}

/* === Progress Bar === */
.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--mb-radius-pill);
  overflow: hidden;
}

.progress-bar__fill {
  height: 100%;
  background: var(--mb-primary);
  border-radius: var(--mb-radius-pill);
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 0;
}

/* === Bottom spacer === */
.earn-view__spacer {
  height: 100px;
}
</style>
