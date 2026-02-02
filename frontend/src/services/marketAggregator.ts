/**
 * Market Price Aggregator Service
 *
 * Aggregates gift prices from multiple markets:
 * - MRKT-API (api.tgmrkt.io)
 * - Tonnel (market.tonnel.network)
 * - Thermos (thermos.gifts)
 * - Fragment (fragment.com)
 */

export interface MarketPrice {
  source: 'mrkt' | 'tonnel' | 'thermos' | 'fragment' | 'internal'
  price: number
  currency: 'TON'
  listingUrl: string
  updatedAt: Date
}

export interface AggregatedGift {
  giftId: string
  name: string
  model: string
  image?: string
  prices: MarketPrice[]
  minPrice: number
  medianPrice: number
  bestDeal: MarketPrice | null
}

interface MarketAdapter {
  name: string
  getPrice(giftId: string): Promise<MarketPrice | null>
  getPrices(giftIds: string[]): Promise<Map<string, MarketPrice>>
  isAvailable(): Promise<boolean>
}

// Cache for prices
const priceCache = new Map<string, { price: MarketPrice; timestamp: number }>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

// ============================================
// MRKT-API Adapter (api.tgmrkt.io)
// ============================================
class MRKTAdapter implements MarketAdapter {
  name = 'mrkt'
  private baseUrl = 'https://api.tgmrkt.io'
  private authToken: string | null = null

  async setAuthToken(token: string) {
    this.authToken = token
  }

  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/gifts/saling`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 1 })
      })
      return response.ok
    } catch {
      return false
    }
  }

  async getPrice(giftId: string): Promise<MarketPrice | null> {
    try {
      const response = await fetch(`${this.baseUrl}/gifts/saling`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {})
        },
        body: JSON.stringify({
          filters: { gift_id: giftId },
          limit: 1
        })
      })

      if (!response.ok) return null

      const data = await response.json()
      if (!data.gifts || data.gifts.length === 0) return null

      const gift = data.gifts[0]
      return {
        source: 'mrkt',
        price: parseFloat(gift.price) || 0,
        currency: 'TON',
        listingUrl: `https://tgmrkt.io/gift/${giftId}`,
        updatedAt: new Date()
      }
    } catch (e) {
      console.warn('MRKT adapter error:', e)
      return null
    }
  }

  async getPrices(giftIds: string[]): Promise<Map<string, MarketPrice>> {
    const result = new Map<string, MarketPrice>()

    try {
      const response = await fetch(`${this.baseUrl}/gifts/saling`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {})
        },
        body: JSON.stringify({ limit: 100 })
      })

      if (!response.ok) return result

      const data = await response.json()
      if (!data.gifts) return result

      for (const gift of data.gifts) {
        if (giftIds.includes(gift.gift_id)) {
          result.set(gift.gift_id, {
            source: 'mrkt',
            price: parseFloat(gift.price) || 0,
            currency: 'TON',
            listingUrl: `https://tgmrkt.io/gift/${gift.gift_id}`,
            updatedAt: new Date()
          })
        }
      }
    } catch (e) {
      console.warn('MRKT batch error:', e)
    }

    return result
  }
}

// ============================================
// Tonnel Adapter (market.tonnel.network)
// ============================================
class TonnelAdapter implements MarketAdapter {
  name = 'tonnel'
  private baseUrl = 'https://market.tonnel.network'

  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/gifts`, { method: 'HEAD' })
      return response.ok || response.status === 405
    } catch {
      return false
    }
  }

  async getPrice(giftId: string): Promise<MarketPrice | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/gifts/${giftId}`)
      if (!response.ok) return null

      const data = await response.json()
      if (!data.price) return null

      return {
        source: 'tonnel',
        price: parseFloat(data.price) || 0,
        currency: 'TON',
        listingUrl: `${this.baseUrl}/gift/${giftId}`,
        updatedAt: new Date()
      }
    } catch (e) {
      console.warn('Tonnel adapter error:', e)
      return null
    }
  }

  async getPrices(giftIds: string[]): Promise<Map<string, MarketPrice>> {
    const result = new Map<string, MarketPrice>()

    // Tonnel might need individual requests or batch endpoint
    const promises = giftIds.map(id => this.getPrice(id).then(p => p && result.set(id, p)))
    await Promise.allSettled(promises)

    return result
  }
}

// ============================================
// Thermos Adapter (thermos.gifts)
// ============================================
class ThermosAdapter implements MarketAdapter {
  name = 'thermos'
  private baseUrl = 'https://thermos.gifts'

  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/gifts`, { method: 'HEAD' })
      return response.ok || response.status === 405
    } catch {
      return false
    }
  }

  async getPrice(giftId: string): Promise<MarketPrice | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/gifts/${giftId}`)
      if (!response.ok) return null

      const data = await response.json()
      if (!data.floor_price) return null

      return {
        source: 'thermos',
        price: parseFloat(data.floor_price) || 0,
        currency: 'TON',
        listingUrl: `${this.baseUrl}/gift/${giftId}`,
        updatedAt: new Date()
      }
    } catch (e) {
      console.warn('Thermos adapter error:', e)
      return null
    }
  }

  async getPrices(giftIds: string[]): Promise<Map<string, MarketPrice>> {
    const result = new Map<string, MarketPrice>()

    const promises = giftIds.map(id => this.getPrice(id).then(p => p && result.set(id, p)))
    await Promise.allSettled(promises)

    return result
  }
}

// ============================================
// Internal API Adapter (our backend)
// ============================================
class InternalAdapter implements MarketAdapter {
  name = 'internal'
  private baseUrl = '/api/v1'

  async isAvailable(): Promise<boolean> {
    return true // Always available
  }

  async getPrice(giftId: string): Promise<MarketPrice | null> {
    try {
      const response = await fetch(`${this.baseUrl}/gifts/${giftId}`)
      if (!response.ok) return null

      const data = await response.json()
      if (!data.floor_price) return null

      return {
        source: 'internal',
        price: parseFloat(data.floor_price) || 0,
        currency: 'TON',
        listingUrl: `/gift/${giftId}`,
        updatedAt: new Date()
      }
    } catch (e) {
      console.warn('Internal adapter error:', e)
      return null
    }
  }

  async getPrices(giftIds: string[]): Promise<Map<string, MarketPrice>> {
    const result = new Map<string, MarketPrice>()

    try {
      const response = await fetch(`${this.baseUrl}/gifts?page=0&page_size=100`)
      if (!response.ok) return result

      const data = await response.json()
      if (!data.gifts) return result

      for (const gift of data.gifts) {
        const id = gift.id || gift.gift_id
        if (giftIds.length === 0 || giftIds.includes(id)) {
          if (gift.floor_price) {
            result.set(id, {
              source: 'internal',
              price: parseFloat(gift.floor_price) || 0,
              currency: 'TON',
              listingUrl: `/gift/${id}`,
              updatedAt: new Date()
            })
          }
        }
      }
    } catch (e) {
      console.warn('Internal batch error:', e)
    }

    return result
  }
}

// ============================================
// Market Aggregator
// ============================================
class MarketAggregator {
  private adapters: MarketAdapter[] = [
    new InternalAdapter(),
    new MRKTAdapter(),
    new TonnelAdapter(),
    new ThermosAdapter(),
  ]

  /**
   * Get prices for a single gift from all markets
   */
  async getAggregatedPrice(giftId: string): Promise<MarketPrice[]> {
    // Check cache first
    const cached = priceCache.get(giftId)
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return [cached.price]
    }

    const results = await Promise.allSettled(
      this.adapters.map(adapter => adapter.getPrice(giftId))
    )

    const prices: MarketPrice[] = results
      .filter((r): r is PromiseFulfilledResult<MarketPrice | null> =>
        r.status === 'fulfilled' && r.value !== null && r.value.price > 0
      )
      .map(r => r.value!)

    // Cache the best price
    if (prices.length > 0) {
      const best = prices.reduce((a, b) => a.price < b.price ? a : b)
      priceCache.set(giftId, { price: best, timestamp: Date.now() })
    }

    return prices
  }

  /**
   * Get aggregated data for multiple gifts
   */
  async getAggregatedGifts(giftIds: string[]): Promise<Map<string, AggregatedGift>> {
    const result = new Map<string, AggregatedGift>()

    // Fetch prices from all adapters in parallel
    const adapterResults = await Promise.allSettled(
      this.adapters.map(adapter => adapter.getPrices(giftIds))
    )

    // Merge results by gift ID
    const pricesByGift = new Map<string, MarketPrice[]>()

    for (const adapterResult of adapterResults) {
      if (adapterResult.status !== 'fulfilled') continue

      const prices = adapterResult.value
      for (const [giftId, price] of prices) {
        if (price.price <= 0) continue

        if (!pricesByGift.has(giftId)) {
          pricesByGift.set(giftId, [])
        }
        pricesByGift.get(giftId)!.push(price)
      }
    }

    // Build aggregated gifts
    for (const [giftId, prices] of pricesByGift) {
      if (prices.length === 0) continue

      const sortedPrices = [...prices].sort((a, b) => a.price - b.price)
      const minPrice = sortedPrices[0].price
      const medianPrice = sortedPrices[Math.floor(sortedPrices.length / 2)].price

      result.set(giftId, {
        giftId,
        name: '',
        model: '',
        prices: sortedPrices,
        minPrice,
        medianPrice,
        bestDeal: sortedPrices[0]
      })
    }

    return result
  }

  /**
   * Get cached price if available, otherwise return 0
   */
  getCachedPrice(giftId: string): number {
    const cached = priceCache.get(giftId)
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.price.price
    }
    return 0
  }

  /**
   * Preload prices for a list of gifts
   */
  async preloadPrices(giftIds: string[]): Promise<void> {
    await this.getAggregatedGifts(giftIds)
  }

  /**
   * Clear price cache
   */
  clearCache(): void {
    priceCache.clear()
  }

  /**
   * Save cache to localStorage
   */
  persistCache(): void {
    const cacheData: Record<string, { price: MarketPrice; timestamp: number }> = {}
    for (const [key, value] of priceCache) {
      cacheData[key] = value
    }
    localStorage.setItem('marketPriceCache', JSON.stringify(cacheData))
  }

  /**
   * Load cache from localStorage
   */
  loadCache(): void {
    try {
      const data = localStorage.getItem('marketPriceCache')
      if (!data) return

      const cacheData = JSON.parse(data)
      for (const [key, value] of Object.entries(cacheData)) {
        const entry = value as { price: MarketPrice; timestamp: number }
        // Only load if not expired
        if (Date.now() - entry.timestamp < CACHE_TTL) {
          entry.price.updatedAt = new Date(entry.price.updatedAt)
          priceCache.set(key, entry)
        }
      }
    } catch (e) {
      console.warn('Failed to load price cache:', e)
    }
  }
}

// Export singleton instance
export const marketAggregator = new MarketAggregator()

// Export helper functions
export function calculateMinPrice(prices: MarketPrice[]): number {
  if (prices.length === 0) return 0
  return Math.min(...prices.map(p => p.price))
}

export function calculateMedianPrice(prices: MarketPrice[]): number {
  if (prices.length === 0) return 0
  const sorted = [...prices].map(p => p.price).sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
}

export function getBestDeal(prices: MarketPrice[]): MarketPrice | null {
  if (prices.length === 0) return null
  return prices.reduce((best, current) =>
    current.price < best.price ? current : best
  )
}
