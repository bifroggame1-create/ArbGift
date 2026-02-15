<template>
  <div class="upgrade-view min-h-screen bg-gray-950 pb-24">
    <!-- Header -->
    <div class="px-4 pt-6 pb-4 bg-gradient-to-b from-purple-900/20 to-transparent">
      <button
        @click="router.back()"
        class="mb-4 text-gray-400 hover:text-white transition-colors flex items-center space-x-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span>Back</span>
      </button>

      <h1 class="text-3xl font-bold text-white mb-2">⚡ Upgrade</h1>
      <p class="text-gray-400 text-sm">Transform one gift into another • Spin the wheel</p>
    </div>

    <!-- Gift Selection -->
    <div class="mx-4 mt-6">
      <h2 class="text-lg font-semibold text-white mb-4">Select Gifts</h2>
      <div class="gift-selection">
        <!-- Input Gift -->
        <div class="selection-slot">
          <div class="slot-label">From</div>
          <div v-if="inputGift" class="selected-gift">
            <TelegramGiftCard :gift="inputGift" @click="selectInputGift" />
          </div>
          <button
            v-else
            @click="selectInputGift"
            class="selection-placeholder"
          >
            <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span class="text-sm text-gray-400">Select Gift</span>
          </button>
        </div>

        <!-- Arrow -->
        <div class="arrow-container">
          <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>

        <!-- Target Gift -->
        <div class="selection-slot">
          <div class="slot-label">To</div>
          <div v-if="targetGift" class="selected-gift">
            <TelegramGiftCard :gift="targetGift" @click="selectTargetGift" />
          </div>
          <button
            v-else
            @click="selectTargetGift"
            class="selection-placeholder"
          >
            <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span class="text-sm text-gray-400">Select Target</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Probability Wheel -->
    <div v-if="inputGift && targetGift" class="mx-4 mt-8">
      <h2 class="text-lg font-semibold text-white mb-4 text-center">Success Probability</h2>

      <div class="wheel-container">
        <ProbabilityWheel
          :probability="probability"
          :is-spinning="isSpinning"
          :result-angle="resultAngle"
        />

        <div class="probability-info">
          <div class="probability-percentage">{{ (probability * 100).toFixed(1) }}%</div>
          <div class="probability-label">Chance to Win</div>
        </div>
      </div>

      <!-- Value Comparison -->
      <div class="value-comparison">
        <div class="comparison-row">
          <div class="comparison-item">
            <div class="comparison-label">Input Value</div>
            <div class="comparison-value">
              <svg width="12" height="12" viewBox="0 0 56 56" fill="none" style="display:inline-block;vertical-align:middle;margin-right:2px">
                <circle cx="28" cy="28" r="28" fill="#0098EA"/>
                <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
              </svg>
              {{ inputValue.toFixed(2) }}
            </div>
          </div>
          <div class="comparison-arrow">→</div>
          <div class="comparison-item">
            <div class="comparison-label">Target Value</div>
            <div class="comparison-value highlight">
              <svg width="12" height="12" viewBox="0 0 56 56" fill="none" style="display:inline-block;vertical-align:middle;margin-right:2px">
                <circle cx="28" cy="28" r="28" fill="#0098EA"/>
                <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
              </svg>
              {{ targetValue.toFixed(2) }}
            </div>
          </div>
        </div>

        <div class="comparison-ratio">
          <span class="ratio-label">Multiplier:</span>
          <span class="ratio-value">x{{ (targetValue / inputValue).toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- Gift Selection Modal -->
    <GiftSelectionModal
      v-if="showGiftSelector"
      :mode="selectionMode"
      :exclude-id="selectionMode === 'target' ? inputGift?.id : undefined"
      @select="onGiftSelected"
      @close="showGiftSelector = false"
    />

    <!-- Action Bar -->
    <div class="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-sm border-t border-gray-800 p-4 pb-safe z-40">
      <button
        :disabled="!canSpin"
        :class="canSpin ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700' : 'bg-gray-700 cursor-not-allowed'"
        class="w-full py-4 rounded-xl font-bold text-white transition-all transform active:scale-[0.98] disabled:opacity-50"
        @click="spinWheel"
      >
        <span v-if="!inputGift || !targetGift">
          Select both gifts to spin
        </span>
        <span v-else-if="isSpinning">
          Spinning...
        </span>
        <span v-else>
          ⚡ Spin the Wheel
        </span>
      </button>
    </div>

    <!-- Result Modal -->
    <UpgradeResultModal
      v-if="showResult"
      :result="upgradeResult"
      @close="closeResult"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'
import TelegramGiftCard from '../components/TelegramGiftCard.vue'
import ProbabilityWheel from '../components/ProbabilityWheel.vue'
import GiftSelectionModal from '../components/GiftSelectionModal.vue'
import UpgradeResultModal from '../components/UpgradeResultModal.vue'
import type { Gift } from '../api/client'

const router = useRouter()
const { hapticImpact } = useTelegram()

// State
const inputGift = ref<Gift | null>(null)
const targetGift = ref<Gift | null>(null)
const showGiftSelector = ref(false)
const selectionMode = ref<'input' | 'target'>('input')
const isSpinning = ref(false)
const resultAngle = ref(0)
const showResult = ref(false)
const upgradeResult = ref<any>(null)

// Computed
const inputValue = computed(() => {
  if (!inputGift.value) return 0
  return parseFloat(String(inputGift.value.min_price_ton || 0))
})

const targetValue = computed(() => {
  if (!targetGift.value) return 0
  return parseFloat(String(targetGift.value.min_price_ton || 0))
})

const probability = computed(() => {
  if (!inputValue.value || !targetValue.value) return 0.5

  // Dynamic probability: BASE_RATE * (input / target)
  const BASE_RATE = 0.50
  const ratio = inputValue.value / targetValue.value
  const prob = BASE_RATE * ratio

  // Clamp between 1% and 95%
  return Math.max(0.01, Math.min(prob, 0.95))
})

const canSpin = computed(() => {
  return inputGift.value && targetGift.value && !isSpinning.value
})

// Methods
const selectInputGift = () => {
  hapticImpact('light')
  selectionMode.value = 'input'
  showGiftSelector.value = true
}

const selectTargetGift = () => {
  hapticImpact('light')
  selectionMode.value = 'target'
  showGiftSelector.value = true
}

const onGiftSelected = (gift: Gift) => {
  if (selectionMode.value === 'input') {
    inputGift.value = gift
  } else {
    targetGift.value = gift
  }
  showGiftSelector.value = false
}

const spinWheel = async () => {
  if (!canSpin.value) return

  hapticImpact('heavy')
  isSpinning.value = true

  // Spin animation: 3 full rotations + final position
  const spins = 3
  const finalAngle = Math.random() * 360
  const totalRotation = spins * 360 + finalAngle

  // Animate
  const duration = 3000
  const startTime = Date.now()

  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    // Easing: cubic-bezier
    const eased = 1 - Math.pow(1 - progress, 3)
    resultAngle.value = eased * totalRotation

    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      // Determine result
      const successAngle = probability.value * 360
      const normalizedAngle = finalAngle % 360
      const won = normalizedAngle < successAngle

      // Show result
      upgradeResult.value = {
        won,
        input_gift: inputGift.value,
        target_gift: targetGift.value,
        probability: probability.value,
        result_angle: finalAngle,
      }

      showResult.value = true
      isSpinning.value = false
    }
  }

  animate()
}

const closeResult = () => {
  showResult.value = false
  inputGift.value = null
  targetGift.value = null
  resultAngle.value = 0
}

onMounted(() => {
  // Load initial data if needed
})
</script>

<style scoped>
.upgrade-view {
  position: relative;
}

.gift-selection {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: space-between;
}

.selection-slot {
  flex: 1;
  text-align: center;
}

.slot-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
  font-weight: 600;
}

.selected-gift {
  max-width: 160px;
  margin: 0 auto;
}

.selection-placeholder {
  width: 100%;
  aspect-ratio: 1;
  max-width: 160px;
  margin: 0 auto;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s;
}

.selection-placeholder:hover {
  border-color: rgba(168, 85, 247, 0.5);
  background: rgba(168, 85, 247, 0.1);
}

.arrow-container {
  flex-shrink: 0;
  margin-top: 24px;
}

.wheel-container {
  position: relative;
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.probability-info {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.probability-percentage {
  font-size: 32px;
  font-weight: 800;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.probability-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;
}

.value-comparison {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  padding: 20px;
}

.comparison-row {
  display: flex;
  items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.comparison-item {
  flex: 1;
  text-align: center;
}

.comparison-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.comparison-value {
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.comparison-value.highlight {
  color: #a855f7;
}

.comparison-arrow {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.4);
}

.comparison-ratio {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.ratio-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-right: 8px;
}

.ratio-value {
  font-size: 20px;
  font-weight: 800;
  color: #fbbf24;
}

.pb-safe {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
