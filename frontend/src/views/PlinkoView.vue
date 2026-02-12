<template>
  <div class="plinko-view">
    <PlinkoHeader
      :balance="balanceStars"
      :is-demo="isDemoMode"
      @toggle-demo="isDemoMode = !isDemoMode"
      @top-up="handleTopUp"
    />

    <div class="board-wrapper">
      <PlinkoBoard
        ref="boardRef"
        :row-count="rowCount"
        :risk-level="riskLevel"
        :multipliers="currentMultipliers"
        @landed="onBallLanded"
        @all-landed="onAllLanded"
      />
      <PlinkoWinFeed :history="history" />
    </div>

    <PlinkoControls
      :bet="betAmount"
      :risk="riskLevel"
      :rows="rowCount"
      :ball-count="ballCount"
      :is-playing="isPlaying"
      :balance="balanceStars"
      @update:bet="betAmount = $event"
      @update:risk="riskLevel = $event"
      @update:rows="rowCount = $event as 8 | 12 | 16"
      @update:ball-count="ballCount = $event"
      @play="handlePlay"
    />

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
import { useTelegram } from '@/composables/useTelegram'
import PlinkoHeader from '@/components/plinko/PlinkoHeader.vue'
import PlinkoBoard from '@/components/plinko/PlinkoBoard.vue'
import PlinkoControls from '@/components/plinko/PlinkoControls.vue'
import PlinkoWinFeed from '@/components/plinko/PlinkoWinFeed.vue'
import WinPopup from '@/components/plinko/WinPopup.vue'

import '@/styles/plinko-theme.css'

const {
  balanceStars,
  betAmount,
  riskLevel,
  rowCount,
  ballCount,
  isDemoMode,
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

function handleTopUp() {
  // TODO: open Stars purchase flow
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.plinko-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-height: 100dvh;
}

.board-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  padding: 0 4px;
}
</style>
