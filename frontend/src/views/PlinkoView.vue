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
          <CurrencyIcon :currency="selectedCurrency" :size="12" />
          {{ amount }}
        </button>
        <button class="bet-pill max-pill" @click="betAmount = Math.floor(currentBalance * 10) / 10">Max</button>
      </div>

      <!-- Main Action Button -->
      <button
        class="main-btn play-btn"
        :disabled="isPlaying || currentBalance < betAmount"
        @click="handlePlay"
      >
        <CurrencyIcon :currency="selectedCurrency" :size="18" />
        <span class="btn-label">{{ isPlaying ? 'Playing...' : `Play ${formatAmount(betAmount)}` }}</span>
      </button>
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
  balanceStars,
  betAmount,
  riskLevel,
  rowCount,
  ballCount,
  isPlaying,
  history,
  currentMultipliers,
  lastDrops,
  showWinPopup,
  gameNumber,
  play,
  onAnimationComplete,
  fetchConfig,
} = usePlinko()

const { hapticImpact } = useTelegram()

const boardRef = ref<InstanceType<typeof PlinkoBoard> | null>(null)
const betAmounts = [10, 50, 100, 500]

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

.main-btn {
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  border: none;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.main-btn:active {
  transform: scale(0.98);
}

.main-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.play-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: #fff;
}

.btn-label {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
