<template>
  <!--
    PIXEL-PERFECT копия маркета portals.tg
    API: https://portal-market.com/api/nfts/search
    CSS: --background: #141414, --primary: #1689ff
  -->
  <div class="market-view">
    <!-- Navigation Tabs (как у portals) -->
    <nav class="market-nav">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="nav-tab"
        :class="{ active: activeTab === tab.id }"
        @click="setTab(tab.id)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <!-- Toolbar: Фильтры, Поиск, Сортировка -->
    <div class="market-toolbar">
      <button class="toolbar-btn filter-btn" @click="showFilters = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>
        </svg>
        <span>Фильтры</span>
      </button>

      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Быстрый поиск"
          class="search-input"
          @input="debounceSearch"
        />
      </div>

      <button class="toolbar-btn sort-btn" @click="showSortMenu = !showSortMenu">
        <div class="sort-content">
          <span class="sort-label">Сортировать по</span>
          <span class="sort-value">{{ currentSortLabel }}</span>
        </div>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m6 9 6 6 6-6"/>
        </svg>
      </button>

      <button class="toolbar-btn activity-btn" @click="showActivity = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
        <span>Активность</span>
      </button>

      <!-- View mode buttons -->
      <div class="view-modes">
        <button
          class="view-btn"
          :class="{ active: gridSize === 'small' }"
          @click="gridSize = 'small'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
          </svg>
        </button>
        <button
          class="view-btn"
          :class="{ active: gridSize === 'large' }"
          @click="gridSize = 'large'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <rect x="3" y="3" width="8" height="8"/>
            <rect x="13" y="3" width="8" height="8"/>
            <rect x="3" y="13" width="8" height="8"/>
            <rect x="13" y="13" width="8" height="8"/>
          </svg>
        </button>
      </div>

      <button class="toolbar-btn refresh-btn" @click="fetchGifts">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 4v6h-6"/>
          <path d="M1 20v-6h6"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
      </button>
    </div>

    <!-- Sort Dropdown -->
    <div v-if="showSortMenu" class="sort-dropdown" @click.self="showSortMenu = false">
      <div class="sort-menu">
        <button
          v-for="opt in sortOptions"
          :key="opt.value"
          class="sort-option"
          :class="{ active: sortBy === opt.value }"
          @click="setSortBy(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
    </div>

    <!-- Gift Grid -->
    <div v-else class="gift-grid-container">
      <div class="gift-grid" :class="gridSize">
        <GiftCard
          v-for="gift in gifts"
          :key="gift.id"
          :gift="gift"
          :selectable="bulkMode"
          :is-selected="selectedGifts.includes(gift.id)"
          @click="handleGiftClick"
          @buy="handleBuy"
          @select="handleSelect"
        />
      </div>

      <!-- Pagination (как у portals) -->
      <div class="pagination" v-if="totalPages > 0">
        <div class="page-controls">
          <button
            class="page-btn"
            :disabled="currentPage <= 1"
            @click="prevPage"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div class="page-info">
            <span class="current-page">{{ currentPage }}</span>
            <span class="page-divider">/</span>
            <span class="total-pages">{{ totalPages }}</span>
          </div>
          <button
            class="page-btn"
            :disabled="currentPage >= totalPages"
            @click="nextPage"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
        </div>
        <input
          type="range"
          class="page-slider"
          :min="1"
          :max="totalPages"
          v-model.number="currentPage"
          @change="fetchGifts"
        />
      </div>

      <!-- Bulk Buy Button (как у portals) -->
      <button
        v-if="selectedGifts.length > 0"
        class="bulk-buy-btn"
        @click="bulkBuy"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
          <path d="M3 6h18"/>
          <path d="M16 10a4 4 0 0 1-8 0"/>
        </svg>
        <span>{{ selectedGifts.length }}</span>
      </button>

      <!-- Empty State -->
      <div v-if="!loading && gifts.length === 0" class="empty-state">
        <span class="empty-icon">🎁</span>
        <p class="empty-text">Нет доступных гифтов</p>
        <p class="empty-hint">Попробуйте изменить фильтры</p>
      </div>
    </div>

    <!-- Footer (как у portals) -->
    <footer class="market-footer">
      <div class="footer-left">
        <div class="ton-price">
          <img src="https://ton.org/download/ton_symbol.svg" alt="TON" class="ton-logo" />
          <span class="price-value">{{ tonPrice }}$</span>
        </div>
        <div class="volume-info">
          <span class="volume-label">Общий объем 24H</span>
          <span class="volume-value">{{ volume24h }}</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" class="volume-icon">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          </svg>
        </div>
      </div>
      <div class="footer-right">
        <button class="footer-btn">Настройки</button>
        <a href="https://t.me/portals_sup" target="_blank" class="footer-btn">Поддержка</a>
        <a href="https://t.me/portals" target="_blank" class="footer-btn">Telegram</a>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GiftCard from '../components/GiftCard.vue'
import { useTelegram } from '../composables/useTelegram'
import axios from 'axios'

const router = useRouter()
const { hapticImpact } = useTelegram()

// API - используем portal-market.com API
const PORTALS_API = 'https://portal-market.com/api'

// Tabs
const tabs = [
  { id: 'all', label: 'Все подарки' },
  { id: 'collections', label: 'Коллекции' },
  { id: 'bundles', label: 'Бандлы' },
]
const activeTab = ref('all')

// State
const loading = ref(true)
const gifts = ref<any[]>([])
const searchQuery = ref('')
const sortBy = ref('listed_at desc')
const gridSize = ref<'small' | 'large'>('large')
const showSortMenu = ref(false)
const showFilters = ref(false)
const showActivity = ref(false)
const bulkMode = ref(false)
const selectedGifts = ref<number[]>([])

// Pagination
const currentPage = ref(1)
const totalPages = ref(50)
const limit = 50

// Market stats
const tonPrice = ref('1.33')
const volume24h = ref('247.5K')

// Sort options (как у portals)
const sortOptions = [
  { value: 'listed_at desc', label: 'Сначала новые' },
  { value: 'listed_at asc', label: 'Сначала старые' },
  { value: 'price asc', label: 'Дешевле' },
  { value: 'price desc', label: 'Дороже' },
]

const currentSortLabel = computed(() => {
  return sortOptions.find(o => o.value === sortBy.value)?.label || 'Сначала новые'
})

// Methods
const setTab = (tab: string) => {
  hapticImpact('light')
  activeTab.value = tab
  if (tab === 'collections') {
    router.push('/collection-list')
  } else if (tab === 'bundles') {
    router.push('/bundles')
  }
}

const setSortBy = (value: string) => {
  hapticImpact('light')
  sortBy.value = value
  showSortMenu.value = false
  fetchGifts()
}

let searchTimeout: ReturnType<typeof setTimeout>
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchGifts()
  }, 300)
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchGifts()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchGifts()
  }
}

const fetchGifts = async () => {
  loading.value = true
  try {
    const offset = (currentPage.value - 1) * limit
    const response = await axios.get(`${PORTALS_API}/nfts/search`, {
      params: {
        offset,
        limit,
        sort_by: sortBy.value,
        search: searchQuery.value || undefined,
        exclude_bundled: true,
        status: 'listed',
      }
    })

    gifts.value = response.data.nfts || []

    // Calculate total pages
    if (response.data.total) {
      totalPages.value = Math.ceil(response.data.total / limit)
    }
  } catch (error) {
    console.error('Fetch error:', error)
    // Fallback to Major.tg if portals fails
    try {
      const response = await axios.get('https://major.tg/api/v1/nft/list/', {
        params: {
          order_by: 'price_asc',
          limit: 30,
          offset: 0,
        }
      })
      gifts.value = (response.data.items || []).map((item: any) => ({
        id: item.address,
        name: item.name,
        tg_id: item.slug,
        image_url: item.image,
        min_price_ton: item.min_bid,
        price: item.min_bid,
      }))
    } catch (e) {
      console.error('Fallback error:', e)
    }
  } finally {
    loading.value = false
  }
}

const fetchMarketStats = async () => {
  try {
    const response = await axios.get(`${PORTALS_API}/market/volume`)
    if (response.data) {
      volume24h.value = formatVolume(response.data.volume_24h || 0)
    }
  } catch (e) {
    // Use default
  }
}

const formatVolume = (vol: number): string => {
  if (vol >= 1000000) return (vol / 1000000).toFixed(1) + 'M'
  if (vol >= 1000) return (vol / 1000).toFixed(1) + 'K'
  return vol.toString()
}

const handleGiftClick = (gift: any) => {
  hapticImpact('light')
  router.push(`/gift/${gift.id}`)
}

const handleBuy = (gift: any) => {
  hapticImpact('medium')
  // Open buy modal
}

const handleSelect = (gift: any) => {
  hapticImpact('light')
  const idx = selectedGifts.value.indexOf(gift.id)
  if (idx > -1) {
    selectedGifts.value.splice(idx, 1)
  } else {
    selectedGifts.value.push(gift.id)
  }
}

const bulkBuy = () => {
  hapticImpact('heavy')
  // Process bulk buy
}

onMounted(() => {
  fetchGifts()
  fetchMarketStats()
})
</script>

<style scoped>
/*
  PORTALS.TG Design System
  --background: #141414
  --primary: #1689ff
  --secondary: #282727
  --radius: 16px
*/

.market-view {
  min-height: 100vh;
  background: #141414;
  color: #fff;
  font-family: "SFProText", -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
  padding-bottom: 34px;
}

/* Navigation Tabs */
.market-nav {
  display: flex;
  gap: 24px;
  padding: 16px 16px 0;
  border-bottom: 1px solid #282727;
}

.nav-tab {
  background: none;
  border: none;
  color: #6d6d71;
  font-size: 16px;
  font-weight: 600;
  padding: 12px 0;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.nav-tab.active {
  color: #fff;
}

.nav-tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #1689ff;
  border-radius: 2px 2px 0 0;
}

/* Toolbar */
.market-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  flex-wrap: wrap;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: #282727;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.toolbar-btn:hover {
  background: #3a3a3a;
}

.filter-btn svg {
  stroke: #1689ff;
}

.search-box {
  flex: 1;
  min-width: 150px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #282727;
  border-radius: 12px;
}

.search-icon {
  stroke: #6d6d71;
}

.search-input {
  flex: 1;
  background: none;
  border: none;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: #6d6d71;
}

.sort-btn {
  min-width: 180px;
}

.sort-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.sort-label {
  font-size: 11px;
  color: #6d6d71;
}

.sort-value {
  font-size: 13px;
  color: #fff;
}

.view-modes {
  display: flex;
  background: #282727;
  border-radius: 10px;
  overflow: hidden;
}

.view-btn {
  padding: 10px 12px;
  background: none;
  border: none;
  color: #6d6d71;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn.active {
  background: #3a3a3a;
  color: #fff;
}

.refresh-btn {
  padding: 10px;
}

/* Sort Dropdown */
.sort-dropdown {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sort-menu {
  background: #282727;
  border-radius: 16px;
  padding: 8px 0;
  min-width: 200px;
}

.sort-option {
  display: block;
  width: 100%;
  padding: 12px 20px;
  background: none;
  border: none;
  color: #fff;
  font-size: 15px;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.sort-option:hover {
  background: #3a3a3a;
}

.sort-option.active {
  color: #1689ff;
}

/* Loading */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #282727;
  border-top-color: #1689ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Gift Grid */
.gift-grid-container {
  padding: 0 16px 80px;
}

.gift-grid {
  display: grid;
  gap: 12px;
}

.gift-grid.large {
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
}

.gift-grid.small {
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
}

/* Pagination */
.pagination {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-top: 24px;
  padding: 16px;
  background: #191919;
  border-radius: 16px;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #282727;
  border: none;
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  background: #3a3a3a;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.current-page {
  color: #fff;
  font-weight: 600;
}

.page-divider {
  color: #6d6d71;
}

.total-pages {
  color: #6d6d71;
}

.page-slider {
  width: 100%;
  max-width: 300px;
  -webkit-appearance: none;
  height: 4px;
  background: #282727;
  border-radius: 2px;
  outline: none;
}

.page-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #1689ff;
  border-radius: 50%;
  cursor: pointer;
}

/* Bulk Buy Button */
.bulk-buy-btn {
  position: fixed;
  bottom: 50px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  background: #1689ff;
  border: none;
  border-radius: 16px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(22, 137, 255, 0.4);
  transition: transform 0.2s;
  z-index: 50;
}

.bulk-buy-btn:active {
  transform: scale(0.95);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: #fff;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 14px;
  color: #6d6d71;
}

/* Footer */
.market-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: #191919;
  border-top: 1px solid #282727;
  height: 34px;
  z-index: 40;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ton-price {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ton-logo {
  width: 16px;
  height: 16px;
}

.price-value {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
}

.volume-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.volume-label {
  font-size: 12px;
  color: #6d6d71;
}

.volume-value {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
}

.volume-icon {
  fill: #1689ff;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #6d6d71;
  font-size: 12px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-btn:hover {
  color: #fff;
}
</style>
