<template>
  <div class="contracts-view min-h-screen bg-gray-950 pb-24">
    <!-- Header -->
    <div class="px-4 pt-6 pb-4 bg-gradient-to-b from-red-900/20 to-transparent">
      <button
        @click="router.back()"
        class="mb-4 text-gray-400 hover:text-white transition-colors flex items-center space-x-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span>Back</span>
      </button>

      <h1 class="text-3xl font-bold text-white mb-2">🔥 Contracts</h1>
      <p class="text-gray-400 text-sm">Risk-based gift gambling • Provably Fair</p>
    </div>

    <!-- Selected Gifts Summary -->
    <div v-if="selectedGifts.length > 0" class="mx-4 mt-6 mb-4">
      <div class="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <div class="flex items-center justify-between mb-3">
          <div>
            <div class="text-xs text-gray-400 mb-1">Selected Gifts</div>
            <div class="text-2xl font-bold text-white">{{ selectedGifts.length }} / 10</div>
          </div>
          <div>
            <div class="text-xs text-gray-400 mb-1">Total Value</div>
            <div class="text-2xl font-bold text-blue-400">{{ totalValue.toFixed(2) }} TON</div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-3 border-t border-gray-700">
          <span class="text-xs text-gray-400">Tap gifts to select/deselect</span>
          <button
            v-if="selectedGifts.length > 0"
            @click="clearSelection"
            class="text-xs text-red-400 hover:text-red-300 font-medium"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>

    <!-- Risk Level Selector -->
    <div class="mx-4 mt-6">
      <h2 class="text-lg font-semibold text-white mb-4">Select Risk Level</h2>
      <div class="space-y-3">
        <RiskButton
          v-for="risk in riskLevels"
          :key="risk.level"
          :risk="risk"
          :selected="selectedRisk === risk.level"
          :disabled="!canSelectRisk(risk)"
          @click="selectRisk(risk.level)"
        />
      </div>
    </div>

    <!-- Potential Payout Info -->
    <div v-if="selectedRisk && selectedGifts.length > 0" class="mx-4 mt-6">
      <div class="bg-gradient-to-r from-yellow-900/30 to-amber-900/30 rounded-xl p-4 border border-yellow-500/30">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs text-yellow-400 mb-1">Potential Payout</div>
            <div class="text-3xl font-bold text-white">{{ potentialPayout.toFixed(2) }} TON</div>
          </div>
          <div class="text-5xl">🏆</div>
        </div>
        <div class="mt-3 text-xs text-yellow-300">
          {{ selectedRiskLevel ? (selectedRiskLevel.probability * 100).toFixed(1) : '0.0' }}% chance to win
        </div>
      </div>
    </div>

    <!-- Gift Inventory -->
    <div class="mx-4 mt-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-white">Your Gifts</h2>
        <div class="text-sm text-gray-400">{{ userGifts.length }} available</div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div
          v-for="i in 6"
          :key="i"
          class="aspect-square bg-gray-800/50 rounded-xl animate-pulse"
        ></div>
      </div>

      <!-- Gift Grid -->
      <div v-else-if="userGifts.length > 0" class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <TelegramGiftCard
          v-for="gift in userGifts"
          :key="gift.id"
          :gift="gift"
          :is-selected="isSelected(gift.id)"
          :selectable="true"
          @select="toggleGift(gift)"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">🎁</div>
        <h3 class="text-xl font-semibold mb-2 text-white">No Gifts Available</h3>
        <p class="text-gray-400 mb-6">You need to own some gifts to play Contracts</p>
        <button
          @click="router.push('/')"
          class="px-6 py-3 bg-blue-600 rounded-xl font-medium hover:bg-blue-700 transition-colors"
        >
          Browse Marketplace
        </button>
      </div>
    </div>

    <!-- Action Bar (Fixed at Bottom) -->
    <div class="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-sm border-t border-gray-800 p-4 pb-safe z-40">
      <button
        :disabled="!canExecute"
        :class="canExecute ? 'bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700' : 'bg-gray-700 cursor-not-allowed'"
        class="w-full py-4 rounded-xl font-bold text-white transition-all transform active:scale-[0.98] disabled:opacity-50"
        @click="executeContract"
      >
        <span v-if="!canExecute && selectedGifts.length < 2">
          Select at least 2 gifts
        </span>
        <span v-else-if="!canExecute && !selectedRisk">
          Choose risk level
        </span>
        <span v-else-if="!canExecute">
          Not enough value for {{ selectedRisk }} mode
        </span>
        <span v-else>
          🔥 Execute Contract
        </span>
      </button>
    </div>

    <!-- Result Modal -->
    <ContractResultModal
      v-if="showResult"
      :result="contractResult"
      @close="closeResult"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'
import TelegramGiftCard from '../components/TelegramGiftCard.vue'
import RiskButton from '../components/RiskButton.vue'
import ContractResultModal from '../components/ContractResultModal.vue'
import type { Gift } from '../api/client'
import { getGifts } from '../api/client'

const router = useRouter()
const { hapticImpact } = useTelegram()

// Risk levels configuration
const riskLevels = [
  {
    level: 'safe',
    name: 'Safe',
    icon: '🛡️',
    multiplier: 2,
    probability: 0.45,
    minValue: 1.0,
    color: 'green'
  },
  {
    level: 'normal',
    name: 'Normal',
    icon: '⚖️',
    multiplier: 8,
    probability: 0.11,
    minValue: 5.0,
    color: 'blue'
  },
  {
    level: 'risky',
    name: 'Risky',
    icon: '🔥',
    multiplier: 100,
    probability: 0.009,
    minValue: 20.0,
    color: 'red'
  },
]

// State
const selectedGifts = ref<number[]>([])
const selectedRisk = ref<string>('')
const userGifts = ref<Gift[]>([])
const loading = ref(true)
const showResult = ref(false)
const contractResult = ref<any>(null)

// Computed
const totalValue = computed(() => {
  return selectedGifts.value.reduce((sum, id) => {
    const gift = userGifts.value.find(g => g.id === id)
    const price = parseFloat(String(gift?.min_price_ton || 0))
    return sum + price
  }, 0)
})

const selectedRiskLevel = computed(() => {
  return riskLevels.find(r => r.level === selectedRisk.value)
})

const potentialPayout = computed(() => {
  if (!selectedRiskLevel.value) return 0
  return totalValue.value * selectedRiskLevel.value.multiplier
})

const canExecute = computed(() => {
  if (selectedGifts.value.length < 2 || selectedGifts.value.length > 10) return false
  if (!selectedRisk.value) return false
  const risk = selectedRiskLevel.value
  return risk ? totalValue.value >= risk.minValue : false
})

// Methods
const canSelectRisk = (risk: typeof riskLevels[0]) => {
  return totalValue.value >= risk.minValue
}

const selectRisk = (level: string) => {
  const risk = riskLevels.find(r => r.level === level)
  if (risk && canSelectRisk(risk)) {
    hapticImpact('medium')
    selectedRisk.value = level
  }
}

const toggleGift = (gift: Gift) => {
  const index = selectedGifts.value.indexOf(gift.id)
  if (index > -1) {
    selectedGifts.value.splice(index, 1)
  } else if (selectedGifts.value.length < 10) {
    selectedGifts.value.push(gift.id)
  }
}

const isSelected = (giftId: number) => {
  return selectedGifts.value.includes(giftId)
}

const clearSelection = () => {
  hapticImpact('light')
  selectedGifts.value = []
  selectedRisk.value = ''
}

const executeContract = async () => {
  if (!canExecute.value) return

  hapticImpact('heavy')

  try {
    // TODO: API call to create and execute contract
    // const result = await createContract({
    //   gift_ids: selectedGifts.value,
    //   risk_level: selectedRisk.value,
    //   client_seed: generateClientSeed()
    // })

    // Mock result for now
    const won = Math.random() < (selectedRiskLevel.value?.probability || 0)
    contractResult.value = {
      won,
      multiplier: selectedRiskLevel.value?.multiplier,
      input_value: totalValue.value,
      payout_value: won ? potentialPayout.value : 0,
      risk_level: selectedRisk.value,
    }

    showResult.value = true
  } catch (error) {
    console.error('Failed to execute contract:', error)
  }
}

const closeResult = () => {
  showResult.value = false
  clearSelection()
  // Refresh gift list
  loadGifts()
}

const loadGifts = async () => {
  try {
    loading.value = true
    // TODO: Load user's owned gifts from API
    // For now, load from marketplace as mock data
    const response = await getGifts({ limit: 20 })
    userGifts.value = response.gifts || []
  } catch (error) {
    console.error('Failed to load gifts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadGifts()
})
</script>

<style scoped>
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
