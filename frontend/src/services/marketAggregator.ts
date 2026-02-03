/**
 * Market Price Aggregator Service
 *
 * Aggregates gift prices from multiple marketplaces
 */

export interface MarketPrice {
  source: 'mrkt' | 'tonnel' | 'thermos' | 'fragment' | 'getgems' | 'api'
  price: number
  currency: 'TON'
  listingUrl?: string
  updatedAt: Date
}

export interface AggregatedGift {
  giftId: string
  name: string
  model: string
  prices: MarketPrice[]
  minPrice: number
  medianPrice: number
  bestDeal: MarketPrice | null
}

// Cache configuration
const CACHE_KEY = 'market_prices_cache'
const CACHE_TTL_MS = 5 * 60 * 1000 // 5 minutes

interface CacheEntry {
  prices: MarketPrice[]
  timestamp: number
}

interface PriceCache {
  [giftId: string]: CacheEntry
}

// Utility functions
export function calculateMinPrice(prices: MarketPrice[]): number {
  if (prices.length === 0) return 0
  return Math.min(...prices.map(p => p.price))
}

export function calculateMedianPrice(prices: MarketPrice[]): number {
  if (prices.length === 0) return 0
  const sorted = [...prices].sort((a, b) => a.price - b.price)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 !== 0
    ? sorted[mid].price
    : (sorted[mid - 1].price + sorted[mid].price) / 2
}

export function getBestDeal(prices: MarketPrice[]): MarketPrice | null {
  if (prices.length === 0) return null
  return prices.reduce((best, current) =>
    current.price < best.price ? current : best
  )
}

class MarketAggregatorService {
  private cache: PriceCache = {}

  constructor() {
    this.loadCache()
  }

  /**
   * Load cache from localStorage
   */
  loadCache(): void {
    try {
      const stored = localStorage.getItem(CACHE_KEY)
      if (stored) {
        this.cache = JSON.parse(stored)
        // Clean expired entries
        this.cleanExpiredCache()
      }
    } catch (e) {
      console.warn('Failed to load price cache:', e)
      this.cache = {}
    }
  }

  /**
   * Persist cache to localStorage
   */
  persistCache(): void {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(this.cache))
    } catch (e) {
      console.warn('Failed to persist price cache:', e)
    }
  }

  /**
   * Clean expired cache entries
   */
  private cleanExpiredCache(): void {
    const now = Date.now()
    for (const [key, entry] of Object.entries(this.cache)) {
      if (now - entry.timestamp > CACHE_TTL_MS) {
        delete this.cache[key]
      }
    }
  }

  /**
   * Clear all cache
   */
  clearCache(): void {
    this.cache = {}
    localStorage.removeItem(CACHE_KEY)
  }

  /**
   * Get cached price for a gift (returns 0 if not found)
   */
  getCachedPrice(giftId: string): number {
    const entry = this.cache[giftId]
    if (!entry) return 0

    // Check if expired
    if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
      delete this.cache[giftId]
      return 0
    }

    return calculateMinPrice(entry.prices)
  }

  /**
   * Set cached prices for a gift
   */
  private setCachedPrice(giftId: string, prices: MarketPrice[]): void {
    this.cache[giftId] = {
      prices,
      timestamp: Date.now()
    }
  }

  /**
   * Fetch prices from internal API
   */
  private async fetchFromApi(giftId: string): Promise<MarketPrice | null> {
    try {
      const response = await fetch(`/api/v1/gifts/${giftId}`)
      if (!response.ok) return null

      const data = await response.json()
      if (data.min_price_ton && parseFloat(data.min_price_ton) > 0) {
        return {
          source: 'api',
          price: parseFloat(data.min_price_ton),
          currency: 'TON',
          updatedAt: new Date()
        }
      }
      return null
    } catch {
      return null
    }
  }

  /**
   * Get aggregated price for a single gift
   */
  async getAggregatedPrice(giftId: string): Promise<MarketPrice[]> {
    // Check cache first
    const cachedEntry = this.cache[giftId]
    if (cachedEntry && Date.now() - cachedEntry.timestamp < CACHE_TTL_MS) {
      return cachedEntry.prices
    }

    // Fetch from all sources in parallel
    const results = await Promise.allSettled([
      this.fetchFromApi(giftId)
    ])

    const prices: MarketPrice[] = results
      .filter((r): r is PromiseFulfilledResult<MarketPrice | null> => r.status === 'fulfilled')
      .map(r => r.value)
      .filter((p): p is MarketPrice => p !== null && p.price > 0)

    // Cache the results
    if (prices.length > 0) {
      this.setCachedPrice(giftId, prices)
    }

    return prices
  }

  /**
   * Get aggregated data for multiple gifts
   */
  async getAggregatedGifts(giftIds: string[]): Promise<Map<string, AggregatedGift>> {
    const results = new Map<string, AggregatedGift>()

    // Process in batches to avoid overwhelming the API
    const batchSize = 10
    for (let i = 0; i < giftIds.length; i += batchSize) {
      const batch = giftIds.slice(i, i + batchSize)

      await Promise.all(
        batch.map(async (giftId) => {
          const prices = await this.getAggregatedPrice(giftId)

          if (prices.length > 0) {
            results.set(giftId, {
              giftId,
              name: '',
              model: '',
              prices,
              minPrice: calculateMinPrice(prices),
              medianPrice: calculateMedianPrice(prices),
              bestDeal: getBestDeal(prices)
            })
          }
        })
      )
    }

    return results
  }
}

// Export singleton instance
export const marketAggregator = new MarketAggregatorService()
