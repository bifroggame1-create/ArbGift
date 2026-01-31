<template>
  <div class="market-view min-h-screen bg-[#0e0f14] pb-20">
    <!-- Header (Portals-style) -->
    <div class="bg-[#1a1b23] px-4 pt-4 pb-3 sticky top-0 z-10 border-b border-[#2a2b35]">
      <div class="flex items-center justify-between mb-3">
        <h1 class="text-2xl font-bold text-white">Маркет</h1>
        <div class="flex items-center gap-2">
          <div class="flex items-center gap-1.5 bg-[#2a2b35] px-3 py-1.5 rounded-full">
            <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            <span class="text-xs text-gray-400">{{ onlineCount }} онлайн</span>
          </div>
        </div>
      </div>

      <!-- Search Bar (Portals-style) -->
      <div class="relative mb-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по имени или адресу..."
          class="w-full bg-[#2a2b35] text-white px-4 py-2.5 rounded-xl text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          @input="onSearchInput"
        />
        <svg class="w-5 h-5 text-gray-500 absolute right-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>

      <!-- Filters Row (Portals-style) -->
      <div class="flex gap-2 overflow-x-auto scrollbar-hide">
        <button
          v-for="filter in filters"
          :key="filter.id"
          @click="toggleFilter(filter.id)"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all',
            activeFilters.includes(filter.id)
              ? 'bg-blue-600 text-white'
              : 'bg-[#2a2b35] text-gray-400 hover:bg-[#353642]'
          ]"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <!-- Tabs (Portals-style) -->
    <div class="sticky top-[180px] bg-[#0e0f14] z-10 px-4 py-2">
      <div class="flex gap-6">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-2 font-semibold transition-all relative text-sm',
            activeTab === tab.id
              ? 'text-white'
              : 'text-gray-500'
          ]"
        >
          {{ tab.label }}
          <div
            v-if="activeTab === tab.id"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 rounded-full"
          ></div>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="px-4 py-12 text-center">
      <div class="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-400 mt-3">Загрузка...</p>
    </div>

    <!-- Gifts Grid (Portals 1:1 Design) -->
    <div v-else class="px-4 pt-3">
      <div class="grid grid-cols-2 gap-3">
        <div
          v-for="listing in displayedListings"
          :key="`${listing.nft_address}-${listing.market}`"
          class="gift-card rounded-2xl overflow-hidden cursor-pointer transform hover:scale-[1.02] active:scale-[0.98] transition-all"
          :style="{ background: getGiftBackground(listing) }"
          @click="openGift(listing)"
        >
          <!-- Gift Visual (3D Icon/Image) -->
          <div class="aspect-square flex items-center justify-center p-6 relative">
            <!-- 3D Model or Image -->
            <img
              v-if="listing.image_url"
              :src="listing.image_url"
              :alt="listing.name"
              class="w-full h-full object-contain drop-shadow-2xl"
            />
            <div v-else class="text-7xl drop-shadow-2xl">
              {{ getGiftIcon(listing) }}
            </div>

            <!-- Market Badge (top-right corner) -->
            <div class="absolute top-2 right-2 px-2 py-1 bg-black/50 backdrop-blur-sm rounded-md">
              <span class="text-[10px] font-semibold text-white uppercase">{{ listing.market }}</span>
            </div>
          </div>

          <!-- Gift Info Footer -->
          <div class="p-3 bg-black/30 backdrop-blur-md">
            <div class="text-white font-bold text-sm mb-0.5 truncate">{{ listing.name || 'Unknown Gift' }}</div>
            <div class="text-white/50 text-xs mb-2">#{{ getSerialNumber(listing.nft_address) }}</div>

            <!-- Price Badge (Portals-style) -->
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-1.5 bg-blue-600/90 hover:bg-blue-600 px-3 py-2 rounded-lg flex-1 justify-center">
                <span class="text-white font-bold text-sm">{{ formatPrice(listing.price) }}</span>
                <span class="text-xs text-white/80">TON</span>
              </div>

              <!-- Quick Buy Button -->
              <button
                class="w-9 h-9 bg-green-600/90 hover:bg-green-600 rounded-lg flex items-center justify-center"
                @click.stop="quickBuy(listing)"
              >
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="mt-6 pb-4 text-center">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="bg-[#2a2b35] hover:bg-[#353642] disabled:opacity-50 text-white px-8 py-3 rounded-xl font-semibold text-sm"
        >
          {{ loadingMore ? 'Загрузка...' : 'Загрузить ещё' }}
        </button>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && displayedListings.length === 0" class="py-16 text-center">
        <div class="text-6xl mb-4">🎁</div>
        <p class="text-gray-400 text-lg">Нет доступных NFT</p>
        <p class="text-gray-500 text-sm mt-2">Попробуйте изменить фильтры</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'
import axios from 'axios'

const router = useRouter()
const { hapticImpact } = useTelegram()

// State
const searchQuery = ref('')
const activeTab = ref('all')
const activeFilters = ref<string[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(true)
const onlineCount = ref(42)

// Pagination
const limit = ref(20)
const offset = ref(0)

// Data
interface Listing {
  nft_address: string
  market: string
  price: string
  seller: string
  listing_url: string
  name?: string
  image_url?: string
  collection_name?: string
}

const listings = ref<Listing[]>([])

// Tabs Configuration (Portals-style)
const tabs = [
  { id: 'all', label: 'Все' },
  { id: 'getgems', label: 'GetGems' },
  { id: 'fragment', label: 'Fragment' },
  { id: 'major', label: 'Major' },
  { id: 'portals', label: 'Portals' },
]

// Filters Configuration
const filters = [
  { id: 'price_asc', label: '💰 Цена ↑' },
  { id: 'price_desc', label: '💰 Цена ↓' },
  { id: 'recent', label: '🆕 Новые' },
  { id: 'on_sale', label: '🔥 На продаже' },
]

// Computed
const displayedListings = computed(() => {
  let filtered = [...listings.value]

  // Filter by market tab
  if (activeTab.value !== 'all') {
    filtered = filtered.filter(l => l.market === activeTab.value)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(l =>
      (l.name?.toLowerCase().includes(query)) ||
      l.nft_address.toLowerCase().includes(query) ||
      (l.collection_name?.toLowerCase().includes(query))
    )
  }

  // Sort by active filters
  if (activeFilters.value.includes('price_asc')) {
    filtered.sort((a, b) => parseFloat(a.price) - parseFloat(b.price))
  } else if (activeFilters.value.includes('price_desc')) {
    filtered.sort((a, b) => parseFloat(b.price) - parseFloat(a.price))
  }

  return filtered
})

// API Base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001'

// Fetch Listings from Backend
const fetchListings = async (append = false) => {
  try {
    if (!append) {
      loading.value = true
      offset.value = 0
    } else {
      loadingMore.value = true
    }

    const response = await axios.get(`${API_BASE}/api/nfts`, {
      params: {
        on_sale: true,
        limit: limit.value,
        offset: offset.value,
      }
    })

    const newListings = response.data.nfts || []

    // Extract listings from NFTs
    const extractedListings: Listing[] = []
    for (const nft of newListings) {
      if (nft.listings && nft.listings.length > 0) {
        for (const listing of nft.listings) {
          extractedListings.push({
            nft_address: nft.address,
            market: listing.market,
            price: listing.price,
            seller: listing.seller,
            listing_url: listing.listing_url,
            name: nft.name,
            image_url: nft.image_url,
            collection_name: nft.collection_name,
          })
        }
      }
    }

    if (append) {
      listings.value.push(...extractedListings)
    } else {
      listings.value = extractedListings
    }

    hasMore.value = newListings.length >= limit.value
  } catch (error) {
    console.error('Error fetching listings:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// Load More
const loadMore = () => {
  hapticImpact('light')
  offset.value += limit.value
  fetchListings(true)
}

// Helpers
const getGiftBackground = (listing: Listing): string => {
  // Generate gradient based on market or price
  const gradients: Record<string, string> = {
    getgems: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    fragment: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    major: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    portals: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
    'ton.diamonds': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
  }

  return gradients[listing.market] || 'linear-gradient(135deg, #64748b 0%, #475569 100%)'
}

const getGiftIcon = (listing: Listing): string => {
  // Default icons by market
  const icons: Record<string, string> = {
    getgems: '💎',
    fragment: '👤',
    major: '🎮',
    portals: '🎁',
    'ton.diamonds': '💍',
  }

  return icons[listing.market] || '🎁'
}

const getSerialNumber = (address: string): string => {
  // Extract last 6 chars as serial
  return address.slice(-6).toUpperCase()
}

const formatPrice = (price: string): string => {
  const num = parseFloat(price)
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  if (num >= 1) return num.toFixed(2)
  return num.toFixed(4)
}

// Actions
const toggleFilter = (filterId: string) => {
  hapticImpact('light')

  // Only one sort filter at a time
  if (filterId.startsWith('price_') || filterId === 'recent') {
    activeFilters.value = activeFilters.value.filter(f => !f.startsWith('price_') && f !== 'recent')
  }

  const index = activeFilters.value.indexOf(filterId)
  if (index > -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push(filterId)
  }
}

const onSearchInput = () => {
  // Debounce search would go here
}

const openGift = (listing: Listing) => {
  hapticImpact('medium')
  router.push(`/gift/${listing.nft_address}`)
}

const quickBuy = (listing: Listing) => {
  hapticImpact('heavy')
  // Open listing URL in new tab or modal
  window.open(listing.listing_url, '_blank')
}

// Watch tab changes
watch(activeTab, () => {
  hapticImpact('light')
})

// Initialize
onMounted(() => {
  fetchListings()

  // Simulate online count updates
  setInterval(() => {
    onlineCount.value = Math.floor(Math.random() * 20) + 30
  }, 10000)
})
</script>

<style scoped>
.market-view {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.gift-card {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  will-change: transform;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
