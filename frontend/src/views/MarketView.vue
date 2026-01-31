<template>
  <div class="market-view min-h-screen bg-[#1a1a2e]">
    <!-- Header -->
    <div class="header-section px-4 pt-3 pb-2">
      <!-- Filter Dropdowns Row 1 -->
      <div class="grid grid-cols-2 gap-2 mb-2">
        <div class="filter-dropdown" @click="toggleDropdown('collection')">
          <span class="filter-label">Коллекции</span>
          <div class="filter-value">
            <span v-if="selectedCollection">{{ selectedCollection }}</span>
            <span v-else class="text-gray-500">Все</span>
            <svg class="w-4 h-4 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
        <div class="filter-dropdown" @click="toggleDropdown('model')">
          <span class="filter-label">Модель</span>
          <div class="filter-value">
            <span v-if="selectedModel">{{ selectedModel }}</span>
            <span v-else class="text-gray-500">Люб</span>
            <svg class="w-4 h-4 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Filter Dropdowns Row 2 -->
      <div class="grid grid-cols-2 gap-2 mb-3">
        <div class="filter-dropdown" @click="toggleDropdown('background')">
          <span class="filter-label">Фон</span>
          <div class="filter-value">
            <span v-if="selectedBg">{{ selectedBg }}</span>
            <span v-else class="text-gray-500">Люб</span>
            <svg class="w-4 h-4 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
        <div class="filter-dropdown" @click="toggleDropdown('symbol')">
          <span class="filter-label">Символ</span>
          <div class="filter-value">
            <span v-if="selectedSymbol">{{ selectedSymbol }}</span>
            <span v-else class="text-gray-500">Люб</span>
            <svg class="w-4 h-4 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Filter & Reset Buttons -->
      <button class="filter-btn w-full mb-2" @click="applyFilters">
        <span>Фильтры</span>
        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
        </svg>
      </button>
      <button class="reset-btn w-full" @click="resetFilters">
        <span>Сбросить фильтры</span>
        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      </button>
    </div>

    <!-- Dropdown Overlay -->
    <div v-if="activeDropdown" class="dropdown-overlay" @click="activeDropdown = null">
      <div class="dropdown-menu" @click.stop>
        <div
          v-for="option in dropdownOptions"
          :key="option.value"
          class="dropdown-item"
          :class="{ active: isOptionSelected(option.value) }"
          @click="selectOption(option.value)"
        >
          {{ option.label }}
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- NFT Grid -->
    <div v-else class="px-2 pt-2 pb-24">
      <div class="grid grid-cols-3 gap-1.5">
        <div
          v-for="item in displayedListings"
          :key="item.address"
          class="nft-card"
          @click="openListing(item)"
        >
          <!-- Market Badge (top-left) -->
          <div class="market-badge">
            <span class="market-dot" :class="item.market_type || 'getgems'"></span>
          </div>

          <!-- Cart Button (top-right) -->
          <button class="cart-btn" @click.stop="addToCart(item)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"/>
            </svg>
          </button>

          <!-- NFT Image -->
          <div class="nft-image-container">
            <img
              v-if="item.image"
              :src="item.image"
              :alt="item.name"
              class="nft-image"
              loading="lazy"
            />
            <div v-else class="nft-placeholder">
              <span class="text-4xl">🎁</span>
            </div>
          </div>

          <!-- Price Badge -->
          <div class="price-badge" :class="getPriceColor(item.min_bid)">
            <span class="price-text">{{ formatPrice(item.min_bid) }}</span>
            <span class="ton-icon">💎</span>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !loading" class="flex justify-center mt-4 mb-4">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="load-more-btn"
        >
          {{ loadingMore ? 'Загрузка...' : 'Загрузить ещё' }}
        </button>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && displayedListings.length === 0" class="empty-state">
        <span class="text-5xl mb-3">🎁</span>
        <p class="text-gray-400">Нет доступных гифтов</p>
        <p class="text-gray-500 text-sm mt-1">Попробуйте изменить фильтры</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import axios from 'axios'

const { hapticImpact } = useTelegram()

// Major.tg public API - works without auth, no backend needed
const MAJOR_API = 'https://major.tg/api/v1'

// Loading
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(true)

// Pagination
const limit = ref(30)
const offset = ref(0)

// Filters
const selectedCollection = ref('')
const selectedModel = ref('')
const selectedBg = ref('')
const selectedSymbol = ref('')
const activeDropdown = ref<string | null>(null)
const sortOrder = ref('price_asc')

// Data
interface MajorNFT {
  address: string
  name: string
  slug: string
  image: string
  min_bid: number
  max_bid: number
  market_type: string
  is_on_sale: boolean
  currency: string
  description: string
  owner: string
}

const listings = ref<MajorNFT[]>([])

// Unique models from data
const models = computed(() => {
  const names = new Set<string>()
  listings.value.forEach(l => {
    const base = l.name?.replace(/#\d+$/, '').trim()
    if (base) names.add(base)
  })
  return Array.from(names).sort()
})

// Computed
const displayedListings = computed(() => {
  let filtered = [...listings.value]

  if (selectedModel.value) {
    filtered = filtered.filter(l =>
      l.name?.startsWith(selectedModel.value)
    )
  }

  return filtered
})

// Dropdown logic
const dropdownOptions = computed(() => {
  if (activeDropdown.value === 'collection') {
    return [
      { label: 'Все', value: '' },
      ...models.value.map(c => ({ label: c, value: c }))
    ]
  }
  if (activeDropdown.value === 'model') {
    return [
      { label: 'Любой', value: '' },
      ...models.value.map(c => ({ label: c, value: c }))
    ]
  }
  if (activeDropdown.value === 'background') {
    return [
      { label: 'Любой', value: '' },
      { label: 'Зелёный', value: 'green' },
      { label: 'Синий', value: 'blue' },
      { label: 'Красный', value: 'red' },
      { label: 'Фиолетовый', value: 'purple' },
      { label: 'Оранжевый', value: 'orange' },
    ]
  }
  if (activeDropdown.value === 'symbol') {
    return [
      { label: 'Любой', value: '' },
    ]
  }
  return []
})

const toggleDropdown = (type: string) => {
  hapticImpact('light')
  activeDropdown.value = activeDropdown.value === type ? null : type
}

const isOptionSelected = (value: string) => {
  const map: Record<string, any> = {
    collection: selectedCollection,
    model: selectedModel,
    background: selectedBg,
    symbol: selectedSymbol,
  }
  return map[activeDropdown.value!]?.value === value
}

const selectOption = (value: string) => {
  const map: Record<string, any> = {
    collection: selectedCollection,
    model: selectedModel,
    background: selectedBg,
    symbol: selectedSymbol,
  }
  if (map[activeDropdown.value!]) {
    map[activeDropdown.value!].value = value
  }
  activeDropdown.value = null
}

// Fetch directly from Major.tg API
const fetchListings = async (append = false) => {
  try {
    if (!append) {
      loading.value = true
      offset.value = 0
    } else {
      loadingMore.value = true
    }

    const response = await axios.get(`${MAJOR_API}/nft/list/`, {
      params: {
        order_by: sortOrder.value,
        limit: limit.value,
        offset: offset.value,
      }
    })

    const items: MajorNFT[] = response.data.items || []

    if (append) {
      listings.value.push(...items)
    } else {
      listings.value = items
    }

    hasMore.value = items.length >= limit.value
  } catch (error) {
    console.error('Fetch error:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  hapticImpact('light')
  offset.value += limit.value
  fetchListings(true)
}

// Helpers
const formatPrice = (price: number): string => {
  if (price >= 1000) return price.toLocaleString('ru-RU', { maximumFractionDigits: 0 })
  if (price >= 100) return price.toFixed(0)
  if (price >= 10) return price.toFixed(2)
  return price.toFixed(2)
}

const getPriceColor = (price: number): string => {
  if (price < 5) return 'price-green'
  if (price < 25) return 'price-blue'
  if (price < 100) return 'price-purple'
  return 'price-orange'
}

const applyFilters = () => {
  hapticImpact('medium')
  fetchListings()
}

const resetFilters = () => {
  hapticImpact('light')
  selectedCollection.value = ''
  selectedModel.value = ''
  selectedBg.value = ''
  selectedSymbol.value = ''
  sortOrder.value = 'price_asc'
  fetchListings()
}

const openListing = (item: MajorNFT) => {
  hapticImpact('medium')
  window.open(`https://major.tg/nft/${item.slug}`, '_blank')
}

const addToCart = (_item: MajorNFT) => {
  hapticImpact('heavy')
}

onMounted(() => {
  fetchListings()
})
</script>

<style scoped>
.market-view {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #1a1a2e;
}

/* Filter Dropdowns */
.filter-dropdown {
  background: #252540;
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.filter-dropdown:active {
  background: #2d2d50;
}
.filter-label {
  display: block;
  font-size: 11px;
  color: #888;
  margin-bottom: 2px;
}
.filter-value {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #fff;
}

/* Filter/Reset Buttons */
.filter-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #252540;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  padding: 12px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.filter-btn:active {
  background: #2d2d50;
}
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(180, 40, 40, 0.3);
  color: #e74c4c;
  font-size: 14px;
  font-weight: 500;
  padding: 12px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.reset-btn:active {
  background: rgba(180, 40, 40, 0.5);
}

/* Dropdown Overlay */
.dropdown-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 100;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.dropdown-menu {
  background: #252540;
  border-radius: 16px 16px 0 0;
  width: 100%;
  max-height: 60vh;
  overflow-y: auto;
  padding: 8px 0;
}
.dropdown-item {
  padding: 14px 20px;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.15s;
}
.dropdown-item:active,
.dropdown-item.active {
  background: #3a3a60;
  color: #4fc3f7;
}

/* NFT Card */
.nft-card {
  position: relative;
  background: #252540;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.nft-card:active {
  transform: scale(0.97);
}

/* Market Badge */
.market-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  z-index: 2;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.market-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.market-dot.getgems {
  background: #4fc3f7;
}
.market-dot.fragment {
  background: #ab47bc;
}
.market-dot.major {
  background: #66bb6a;
}

/* Cart Button */
.cart-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  z-index: 2;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  cursor: pointer;
  transition: all 0.15s;
}
.cart-btn:active {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
}

/* NFT Image */
.nft-image-container {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
}
.nft-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}
.nft-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

/* Price Badge */
.price-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin: 0 8px 8px 8px;
  padding: 4px 10px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
}
.price-text {
  color: #fff;
}
.ton-icon {
  font-size: 11px;
}
.price-green {
  background: #2e7d32;
}
.price-blue {
  background: #1565c0;
}
.price-purple {
  background: #7b1fa2;
}
.price-orange {
  background: #e65100;
}

/* Load More */
.load-more-btn {
  background: #252540;
  color: #fff;
  border: none;
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.load-more-btn:active {
  background: #2d2d50;
}
.load-more-btn:disabled {
  opacity: 0.5;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 0;
  height: 0;
}
</style>
