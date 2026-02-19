import { ref, computed, type Ref } from 'vue'
import { plinkoPlay, plinkoGetConfig, plinkoCommit, revealRound, type DropResult, type PlinkoConfig } from '@/api/plinko'
import { useTelegram } from '@/composables/useTelegram'
import { useCurrency } from '@/composables/useCurrency'

export interface PlinkoHistoryItem {
  multiplier: number
  payout: number
  profit: number
  isWin: boolean
}

// Demo mode config - use when API is unavailable
const DEMO_MODE = false  // Enable backend mode by default
const DEMO_BALANCE = 1000  // Starting demo balance

export function usePlinko() {
  const { user } = useTelegram()
  const { currentBalance, deductBalance, addBalance, setBalance, balanceLoaded } = useCurrency()

  // Initialize demo balance if needed
  if (DEMO_MODE && !balanceLoaded.value) {
    setBalance(10, DEMO_BALANCE)  // 10 TON, 1000 Stars
  }

  // Config (fetched from server)
  const config: Ref<PlinkoConfig | null> = ref(null)

  // Game state
  const betAmount = ref(100)
  const riskLevel = ref<'low' | 'medium' | 'high'>('medium')
  const rowCount = ref<8 | 12 | 16>(12)
  const ballCount = ref(1)
  const isPlaying = ref(false)
  const history = ref<PlinkoHistoryItem[]>([])
  const lastRoundId = ref<string | null>(null)
  const lastHash = ref<string | null>(null)
  const lastReveal = ref<{ server_seed: string; server_seed_hash: string } | null>(null)

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

  /**
   * Generate provably fair random path for demo mode
   */
  function generateDemoPath(rows: number): number[][] {
    const path: number[][] = []
    let x = 0.5 // Start at center (0-1 range)

    for (let row = 0; row < rows; row++) {
      // Random left (-1) or right (+1) at each peg
      const direction = Math.random() < 0.5 ? -1 : 1
      const step = 1 / (rows + 1) // Step size based on row count
      x += direction * step * 0.5

      // Clamp to valid range
      x = Math.max(0.05, Math.min(0.95, x))
      path.push([x, (row + 1) / rows])
    }

    return path
  }

  /**
   * Calculate landing slot from final X position
   */
  function calculateSlot(finalX: number, numSlots: number): number {
    return Math.min(numSlots - 1, Math.max(0, Math.floor(finalX * numSlots)))
  }

  async function play(): Promise<DropResult[]> {
    console.log('🎲 [usePlinko] play() called')
    console.log('🎲 [usePlinko] isPlaying:', isPlaying.value)
    console.log('🎲 [usePlinko] DEMO_MODE:', DEMO_MODE)

    if (isPlaying.value) {
      console.log('❌ [usePlinko] Already playing, aborting')
      return []
    }

    const totalCost = betAmount.value * ballCount.value
    console.log('🎲 [usePlinko] Balance check:', {
      currentBalance: currentBalance.value,
      betAmount: betAmount.value,
      ballCount: ballCount.value,
      totalCost,
      hasEnough: currentBalance.value >= totalCost
    })

    if (currentBalance.value < totalCost) {
      console.log('❌ [usePlinko] Insufficient balance:', currentBalance.value, 'needed:', totalCost)
      return []
    }

    console.log('✅ [usePlinko] Balance check passed, setting isPlaying = true')
    isPlaying.value = true

    let drops: DropResult[]

    // DEMO MODE: Generate results locally without API
    if (DEMO_MODE) {
      console.log('🎮 [usePlinko] Using DEMO MODE - generating local results')

      const multipliers = currentMultipliers.value
      const numSlots = multipliers.length

      drops = []
      for (let i = 0; i < ballCount.value; i++) {
        const path = generateDemoPath(rowCount.value)
        const finalX = path[path.length - 1][0]
        const slot = calculateSlot(finalX, numSlots)
        const multiplier = multipliers[slot] || 0.2
        const payout = Math.round(betAmount.value * multiplier * 100) / 100
        const profit = payout - betAmount.value

        drops.push({
          id: `demo_${Date.now()}_${i}`,
          path,
          landing_slot: slot,
          multiplier,
          bet_amount: betAmount.value,
          payout,
          profit,
          server_seed_hash: 'demo_mode',
          server_seed: 'demo_mode',
          client_seed: 'demo_mode',
          nonce: i,
          risk_level: riskLevel.value,
          row_count: rowCount.value,
          created_at: new Date().toISOString(),
        })
      }

      // Update balance locally
      const totalPayout = drops.reduce((sum, d) => sum + d.payout, 0)
      deductBalance(totalCost)
      if (totalPayout > 0) {
        addBalance(totalPayout)
      }

      console.log('🎮 [usePlinko] Demo drops generated:', drops)
    } else {
      // Server-side play
      const userId = String(user.value?.id || '0')
      console.log('🎲 [usePlinko] Calling API with:', {
        userId,
        betAmountStars: betAmount.value,
        riskLevel: riskLevel.value,
        rowCount: rowCount.value,
        ballCount: ballCount.value,
      })

      try {
        const commit = await plinkoCommit()
        lastRoundId.value = commit.round_id
        lastHash.value = commit.server_seed_hash

        const response = await plinkoPlay({
          userId,
          betAmountStars: betAmount.value,
          riskLevel: riskLevel.value,
          rowCount: rowCount.value,
          ballCount: ballCount.value,
          roundId: commit.round_id,
        })
        console.log('✅ [usePlinko] API response:', response)
        drops = response.drops
        lastRoundId.value = response.round_id || commit.round_id
        lastHash.value = response.server_seed_hash || commit.server_seed_hash

        // Update balance from server response
        if (typeof response.new_balance_stars === 'number') {
          setBalance(currentBalance.value, response.new_balance_stars)
        }
      } catch (error) {
        console.error('❌ [usePlinko] Plinko play error:', error)
        isPlaying.value = false
        return []
      }
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
    lastRoundId,
    lastHash,
    lastReveal,

    // Actions
    play,
    onAnimationComplete,
    async reveal() {
      if (!lastRoundId.value) return null
      const rev = await revealRound(lastRoundId.value)
      lastReveal.value = rev
      return rev
    },
  }
}
