<template>
  <div class="plinko-view">
    <!-- Header -->
    <header class="game-header-bar">
      <button class="header-back" @click="$router.push('/solo')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="header-title">
        <span class="title-main">Plinko</span>
        <span class="title-badge" style="background:#8b5cf6">CLASSIC</span>
      </div>
      <div class="header-balance">
        <CurrencyIcon :currency="selectedCurrency" :size="16" />
        <span class="balance-val">{{ formatAmount(currentBalance) }}</span>
        <button class="balance-plus">+</button>
      </div>
    </header>

    <!-- Board Container -->
    <div class="board-wrapper">
      <div class="board-container">
        <PlinkoBoard
          ref="boardRef"
          :row-count="rowCount"
          :risk-level="riskLevel"
          :multipliers="currentMultipliers"
          @landed="onBallLanded"
          @all-landed="onAllLanded"
        />
      </div>
      <PlinkoWinFeed :history="history" />
    </div>

    <!-- Currency Switcher -->
    <div class="currency-bar">
      <CurrencySwitcher />
    </div>

    <!-- Bet Controls -->
    <div class="bet-controls">
      <!-- Bet Amount Pills -->
      <div class="bet-amounts">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          class="bet-pill"
          :class="{ active: betAmount === amount }"
          @click="betAmount = amount"
        >
          {{ amount }} {{ currencySymbol }}
        </button>
        <button class="bet-pill max-pill" @click="betAmount = Math.floor(currentBalance * 10) / 10">Макс</button>
      </div>

      <!-- Action Row -->
      <div class="action-row">
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
          class="main-btn play-btn"
          :class="currencyClass"
          :disabled="isPlaying || currentBalance < betAmount"
          @click="handlePlay"
        >
          <span class="btn-text-main">{{ isPlaying ? 'Играем...' : 'Играть' }}</span>
          <span class="btn-text-sub">{{ currencySymbol }} {{ formatAmount(betAmount) }}</span>
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

    <WinPopup
      v-if="showWinPopup && bestWinDrop"
      :multiplier="bestWinDrop.multiplier"
      :payout="bestWinDrop.payout"
      @close="showWinPopup = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePlinko } from '@/composables/usePlinko'
import { useCurrency } from '@/composables/useCurrency'
import { useTelegram } from '@/composables/useTelegram'
import PlinkoBoard from '@/components/plinko/PlinkoBoard.vue'
import PlinkoWinFeed from '@/components/plinko/PlinkoWinFeed.vue'
import WinPopup from '@/components/plinko/WinPopup.vue'
import CurrencySwitcher from '@/components/CurrencySwitcher.vue'
import CurrencyIcon from '@/components/CurrencyIcon.vue'

import '@/styles/plinko-theme.css'

const { selectedCurrency, currentBalance, formatAmount } = useCurrency()

const {
  betAmount,
  riskLevel,
  rowCount,
  isPlaying,
  history,
  currentMultipliers,
  lastDrops,
  showWinPopup,
  play,
  onAnimationComplete,
  fetchConfig,
} = usePlinko()

const { hapticImpact } = useTelegram()

const boardRef = ref<InstanceType<typeof PlinkoBoard> | null>(null)

// Currency-specific presets
const betAmounts = computed(() => {
  return selectedCurrency.value === 'stars'
    ? [150, 500, 1000, 5000, 10000]
    : [1, 3, 10, 30, 50]
})

const currencySymbol = computed(() => {
  return selectedCurrency.value === 'stars' ? '★' : '▽'
})

const currencyClass = computed(() => {
  return selectedCurrency.value === 'stars' ? 'stars-mode' : 'ton-mode'
})

const bestWinDrop = computed(() => {
  if (!lastDrops.value.length) return null
  return lastDrops.value.reduce((best, d) =>
    d.multiplier > best.multiplier ? d : best,
    lastDrops.value[0]
  )
})

let landedCount = 0

async function handlePlay() {
  const drops = await play()
  if (!drops.length) return

  landedCount = 0

  // Stagger ball drops
  for (let i = 0; i < drops.length; i++) {
    setTimeout(() => {
      boardRef.value?.dropBall(drops[i].path, i)
    }, i * 400) // 400ms between each ball
  }
}

function onBallLanded(_slotIndex: number, _dropIndex: number) {
  landedCount++
  hapticImpact?.('light')
}

function onAllLanded() {
  if (landedCount >= (lastDrops.value?.length || 1)) {
    onAnimationComplete()
  }
}

function handleSwap() {
  // Currency switching is handled by CurrencySwitcher component
  hapticImpact?.('light')
}

function handleDeposit() {
  // Navigate to deposit/top-up page
  hapticImpact?.('light')
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.plinko-view {
  min-height: 100vh;
  background: #0C0C0C;
  color: #fff;
  font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 15px;
  padding-bottom: 100px;
}

/* Header */
.game-header-bar {
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
  cursor: pointer;
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

.balance-val {
  font-size: 14px;
  font-weight: 600;
}

.balance-plus {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

/* Board */
.board-wrapper {
  width: 100%;
  aspect-ratio: 1;
  margin-bottom: 12px;
  position: relative;
}

.board-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0E0F14;
  border: 2px solid #191919;
  border-radius: 32px;
  overflow: hidden;
}

/* Currency Bar */
.currency-bar {
  margin-bottom: 12px;
}

/* Bet Controls */
.bet-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bet-amounts {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
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

/* Action Row */
.action-row {
  display: flex;
  align-items: center;
  gap: 12px;
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

.play-btn.stars-mode {
  background: linear-gradient(135deg, #FFB800 0%, #FF8C00 100%);
  color: #000;
  box-shadow: 0 0 24px rgba(255, 184, 0, 0.4);
}

.play-btn.ton-mode {
  background: linear-gradient(135deg, #34CDEF 0%, #0EA5E9 100%);
  color: #000;
  box-shadow: 0 0 24px rgba(52, 205, 239, 0.4);
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
</style>
