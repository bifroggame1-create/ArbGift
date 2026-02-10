/**
 * Market Aggregator Composable
 *
 * Vue composable for accessing aggregated market prices
 */
import { ref, onMounted } from 'vue'
import {
  marketAggregator,
  type AggregatedGift,
} from '../services/marketAggregator'

export function useMarketAggregator() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const aggregatedData = ref<Map<string, AggregatedGift>>(new Map())

  // Load cached prices on mount
  onMounted(() => {
    marketAggregator.loadCache()
  })

  /**
   * Preload prices for a list of gifts
   */
  const preloadPrices = async (giftIds: string[]): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      aggregatedData.value = await marketAggregator.getAggregatedGifts(giftIds)
      marketAggregator.persistCache()
    } catch (e) {
      error.value = 'Failed to load prices'
      console.error('Preload prices error:', e)
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    aggregatedData,
    preloadPrices,
  }
}
