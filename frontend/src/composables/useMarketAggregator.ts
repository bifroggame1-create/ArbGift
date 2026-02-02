/**
 * Market Aggregator Composable
 *
 * Vue composable for accessing aggregated market prices
 */
import { ref, onMounted } from 'vue'
import {
  marketAggregator,
  type MarketPrice,
  type AggregatedGift,
  calculateMinPrice,
  calculateMedianPrice,
  getBestDeal
} from '../services/marketAggregator'

export interface GiftWithPrices {
  id: string
  name: string
  model: string
  image?: string
  floorPrice: number
  prices: MarketPrice[]
  bestDeal: MarketPrice | null
  priceSource: string
}

export function useMarketAggregator() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const gifts = ref<GiftWithPrices[]>([])
  const aggregatedData = ref<Map<string, AggregatedGift>>(new Map())

  // Load cached prices on mount
  onMounted(() => {
    marketAggregator.loadCache()
  })

  /**
   * Get cached price for a gift (instant, no network)
   */
  const getCachedPrice = (giftId: string): number => {
    return marketAggregator.getCachedPrice(giftId)
  }

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

  /**
   * Get aggregated price for a single gift
   */
  const getGiftPrices = async (giftId: string): Promise<MarketPrice[]> => {
    try {
      return await marketAggregator.getAggregatedPrice(giftId)
    } catch (e) {
      console.error('Get gift prices error:', e)
      return []
    }
  }

  /**
   * Get best price for a gift (uses cache if available)
   */
  const getBestPrice = (giftId: string): number => {
    const cached = getCachedPrice(giftId)
    if (cached > 0) return cached

    const aggregated = aggregatedData.value.get(giftId)
    if (aggregated) return aggregated.minPrice

    return 0
  }

  /**
   * Get price display string with source indicator
   */
  const getPriceDisplay = (giftId: string): { price: string; source: string } => {
    const aggregated = aggregatedData.value.get(giftId)

    if (aggregated && aggregated.bestDeal) {
      return {
        price: aggregated.minPrice.toFixed(2),
        source: aggregated.bestDeal.source
      }
    }

    const cached = getCachedPrice(giftId)
    if (cached > 0) {
      return { price: cached.toFixed(2), source: 'cached' }
    }

    return { price: '—', source: 'unavailable' }
  }

  /**
   * Enrich gift list with aggregated prices
   */
  const enrichGiftsWithPrices = (
    rawGifts: Array<{
      id?: string
      gift_id?: string
      name?: string
      model?: string
      image?: string
      floor_price?: string | number
    }>
  ): GiftWithPrices[] => {
    return rawGifts.map(gift => {
      const id = gift.id || gift.gift_id || ''
      const aggregated = aggregatedData.value.get(id)

      let floorPrice = 0
      let prices: MarketPrice[] = []
      let bestDeal: MarketPrice | null = null
      let priceSource = 'api'

      if (aggregated) {
        floorPrice = aggregated.minPrice
        prices = aggregated.prices
        bestDeal = aggregated.bestDeal
        priceSource = bestDeal?.source || 'aggregated'
      } else if (gift.floor_price) {
        floorPrice = typeof gift.floor_price === 'string'
          ? parseFloat(gift.floor_price)
          : gift.floor_price
        priceSource = 'api'
      } else {
        const cached = getCachedPrice(id)
        if (cached > 0) {
          floorPrice = cached
          priceSource = 'cached'
        }
      }

      return {
        id,
        name: gift.name || '',
        model: gift.model || '',
        image: gift.image,
        floorPrice,
        prices,
        bestDeal,
        priceSource
      }
    })
  }

  /**
   * Force refresh prices (bypass cache)
   */
  const refreshPrices = async (giftIds: string[]): Promise<void> => {
    marketAggregator.clearCache()
    await preloadPrices(giftIds)
  }

  /**
   * Get price comparison for a gift
   */
  const getPriceComparison = (giftId: string): {
    min: number
    median: number
    sources: string[]
  } | null => {
    const aggregated = aggregatedData.value.get(giftId)
    if (!aggregated || aggregated.prices.length === 0) return null

    return {
      min: aggregated.minPrice,
      median: aggregated.medianPrice,
      sources: aggregated.prices.map((p: MarketPrice) => p.source)
    }
  }

  return {
    // State
    isLoading,
    error,
    gifts,
    aggregatedData,

    // Methods
    getCachedPrice,
    preloadPrices,
    getGiftPrices,
    getBestPrice,
    getPriceDisplay,
    enrichGiftsWithPrices,
    refreshPrices,
    getPriceComparison,

    // Re-export utilities
    calculateMinPrice,
    calculateMedianPrice,
    getBestDeal
  }
}
