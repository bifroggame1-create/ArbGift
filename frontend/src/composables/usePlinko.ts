import { ref, computed, type Ref } from 'vue'
import { plinkoPlay, plinkoGetConfig, type DropResult, type PlinkoConfig } from '@/api/plinko'
import { useTelegram } from '@/composables/useTelegram'
import { useCurrency } from '@/composables/useCurrency'

export interface PlinkoHistoryItem {
  multiplier: number
  payout: number
  profit: number
  isWin: boolean
}

export function usePlinko() {
  const { user } = useTelegram()
  const { currentBalance, deductBalance } = useCurrency()

  // Config (fetched from server)
  const config: Ref<PlinkoConfig | null> = ref(null)

  // Game state
  const betAmount = ref(100)
  const riskLevel = ref<'low' | 'medium' | 'high'>('medium')
  const rowCount = ref<8 | 12 | 16>(12)
  const ballCount = ref(1)
  const isPlaying = ref(false)
  const history = ref<PlinkoHistoryItem[]>([])

  // Last result for win popup
  const lastDrops = ref<DropResult[]>([])
  const showWinPopup = ref(false)
  const gameNumber = ref(0)

  // Default multiplier sets (used before config loads)
  const defaultMultiplierSets: Record<string, Record<string, number[]>> = {
    low: {
      '8': [5.6, 1.5, 0.8, 0.5, 0.3, 0.5, 0.8, 1.5, 5.6],
      '12': [8.9, 3, 1.2, 0.7, 0.5, 0.3, 0.2, 0.3, 0.5, 0.7, 1.2, 3, 8.9],
      '16': [16, 9, 2, 1, 0.7, 0.4, 0.3, 0.2, 0.2, 0.3, 0.4, 0.7, 1, 2, 9, 16],
    },
    medium: {
      '8': [13, 3, 0.9, 0.4, 0.2, 0.4, 0.9, 3, 13],
      '12': [33, 11, 3, 1.2, 0.5, 0.3, 0.2, 0.3, 0.5, 1.2, 3, 11, 33],
      '16': [110, 41, 10, 3, 1.2, 0.5, 0.3, 0.2, 0.2, 0.3, 0.5, 1.2, 3, 10, 41, 110],
    },
    high: {
      '8': [29, 4, 0.9, 0.2, 0.1, 0.2, 0.9, 4, 29],
      '12': [170, 24, 8.1, 1.5, 0.4, 0.1, 0.1, 0.4, 1.5, 8.1, 24, 170],
      '16': [1000, 130, 26, 9, 2, 0.5, 0.1, 0.1, 0.1, 0.1, 0.5, 2, 9, 26, 130, 1000],
    },
  }

  const multiplierSets = computed(() =>
    config.value?.multiplier_sets || defaultMultiplierSets
  )

  const currentMultipliers = computed(() => {
    const sets = multiplierSets.value
    return sets[riskLevel.value]?.[String(rowCount.value)] || []
  })

  async function fetchConfig() {
    try {
      config.value = await plinkoGetConfig()
    } catch {
      // Use defaults
    }
  }

  async function play(): Promise<DropResult[]> {
    if (isPlaying.value) return []

    const totalCost = betAmount.value * ballCount.value
    if (currentBalance.value < totalCost) {
      console.log('Insufficient balance:', currentBalance.value, 'needed:', totalCost)
      return []
    }

    isPlaying.value = true

    let drops: DropResult[]

    // Server-side play
    const userId = String(user.value?.id || '0')
    try {
      const response = await plinkoPlay({
        userId,
        betAmountStars: betAmount.value,
        riskLevel: riskLevel.value,
        rowCount: rowCount.value,
        ballCount: ballCount.value,
      })
      drops = response.drops

      // Update balance from server response
      if (response.new_balance_stars > 0) {
        // Deduct the cost and add the payout
        const totalPayout = drops.reduce((sum, d) => sum + d.payout, 0)
        deductBalance(totalCost)
        if (totalPayout > 0) {
          deductBalance(-totalPayout) // Add payout (negative deduction)
        }
      }
    } catch (error) {
      console.error('Plinko play error:', error)
      isPlaying.value = false
      return []
    }

    // Add to history
    for (const drop of drops) {
      history.value.unshift({
        multiplier: drop.multiplier,
        payout: drop.payout,
        profit: drop.profit,
        isWin: drop.profit > 0,
      })
    }
    // Keep last 50
    if (history.value.length > 50) {
      history.value = history.value.slice(0, 50)
    }

    lastDrops.value = drops
    gameNumber.value++

    // Show win popup for significant wins
    const bestDrop = drops.reduce((best, d) => d.multiplier > best.multiplier ? d : best, drops[0])
    if (bestDrop.multiplier >= 2) {
      showWinPopup.value = true
    }

    // Note: isPlaying is set to false by the board component after animation completes

    return drops
  }

  function onAnimationComplete() {
    isPlaying.value = false
  }

  return {
    // Config
    config,
    multiplierSets,
    currentMultipliers,
    fetchConfig,

    // State
    currentBalance,
    betAmount,
    riskLevel,
    rowCount,
    ballCount,
    isPlaying,
    history,

    // Results
    lastDrops,
    showWinPopup,
    gameNumber,

    // Actions
    play,
    onAnimationComplete,
  }
}
