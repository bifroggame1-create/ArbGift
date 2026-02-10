<template>
  <div class="market-view">
    <!-- Tabs: Gifts / Stickers -->
    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tabs__item"
        :class="{ active: activeTab === tab.id }"
        @click="setTab(tab.id)"
      >{{ tab.label }}</button>
    </nav>

    <!-- Search + sort/refresh -->
    <div class="search-row">
      <div class="search-box">
        <svg class="search-box__icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Enter a keyword to search"
          class="search-box__input"
          @keyup.enter="applyFilters()"
        />
      </div>
      <button class="icon-btn" @click="showSortMenu = !showSortMenu">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>
        </svg>
      </button>
      <button class="icon-btn" @click="fetchGifts()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/>
          <path d="M21 3v5h-5"/>
        </svg>
      </button>
    </div>

    <!-- Filter chips (horizontal scroll) -->
    <div class="filters">
      <button
        v-for="f in filterButtons"
        :key="f.key"
        class="filter-btn"
        :class="{ active: isFilterActive(f.key) }"
        @click="openDropdown = openDropdown === f.key ? null : f.key"
      >
        <span>{{ getFilterLabel(f) }}</span>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <path d="m6 9 6 6 6-6"/>
        </svg>
      </button>
    </div>

    <!-- Gift Grid (2 columns) -->
    <div class="grid-wrap">
      <div v-if="loading" class="grid">
        <SkeletonCard v-for="i in 8" :key="'sk-' + i" />
      </div>

      <div v-else class="grid">
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

      <!-- Pagination -->
      <div v-if="!loading && totalPages > 1" class="pagination">
        <button class="pagination__btn" :disabled="currentPage <= 1" @click="prevPage">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <span class="pagination__info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="pagination__btn" :disabled="currentPage >= totalPages" @click="nextPage">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>

      <!-- Empty -->
      <div v-if="!loading && gifts.length === 0" class="empty">
        <p class="empty__title">No gifts found</p>
        <p class="empty__hint">Try adjusting your filters</p>
      </div>
    </div>

    <!-- Cart bar (bottom) -->
    <div class="cart-bar">
      <div class="cart-bar__counter">
        <button class="cart-bar__btn" :disabled="selectedGifts.length === 0" @click="selectedGifts.pop()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/></svg>
        </button>
        <span class="cart-bar__count">{{ selectedGifts.length }}</span>
        <button class="cart-bar__btn" @click="bulkMode = !bulkMode">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
        </button>
      </div>
      <button class="cart-bar__checkout" :disabled="selectedGifts.length === 0" @click="bulkBuy">
        <span>Cart</span>
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z" fill="currentColor"/>
        </svg>
        <span>0.00</span>
      </button>
    </div>

    <!-- Sort Overlay -->
    <Teleport to="body">
      <Transition name="sort-fade">
        <div v-if="showSortMenu" class="sort-overlay" @click.self="showSortMenu = false">
          <div class="sort-menu">
            <div class="sort-menu__header">Sort by</div>
            <button
              v-for="opt in sortOptions"
              :key="opt.value"
              class="sort-menu__option"
              :class="{ active: sortBy === opt.value }"
              @click="setSortBy(opt.value)"
            >
              <span>{{ opt.label }}</span>
              <svg v-if="sortBy === opt.value" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M20 6 9 17l-5-5"/>
              </svg>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Filter Bottom Sheet -->
    <Teleport to="body">
      <Transition name="filter-overlay">
        <div v-if="openDropdown" class="filter-sheet-overlay" @click.self="openDropdown = null">
          <Transition name="sheet-slide">
            <div v-if="openDropdown" class="filter-sheet">
              <div class="filter-sheet__handle"></div>
              <div class="filter-sheet__header">
                <h3 class="filter-sheet__title">{{ dropdownTitle }}</h3>
                <button class="filter-sheet__close" @click="openDropdown = null">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
                  </svg>
                </button>
              </div>
              <div class="filter-sheet__body">
                <div class="filter-chips">
                  <button
                    v-for="opt in dropdownOptions"
                    :key="opt"
                    class="filter-chip"
                    :class="{ active: isDropdownOptionActive(opt) }"
                    @click="toggleDropdownOption(opt)"
                  >{{ opt }}</button>
                </div>
              </div>
              <div class="filter-sheet__footer">
                <button class="filter-sheet__done" @click="openDropdown = null; applyFilters()">Done</button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GiftCard from '../components/GiftCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import { useTelegram } from '../composables/useTelegram'
import { useMarketAggregator } from '../composables/useMarketAggregator'
import { getGifts, searchGifts, getStats } from '../api/client'

const router = useRouter()
const { hapticImpact } = useTelegram()
const { preloadPrices, enrichGiftsWithPrices } = useMarketAggregator()

// Tabs
const tabs = [
  { id: 'all', label: 'Gifts' },
  { id: 'upgrades', label: 'Upgrades' },
]
const activeTab = ref('all')

// State
const loading = ref(true)
const gifts = ref<any[]>([])
const searchQuery = ref('')
const sortBy = ref('listed_at desc')
const showSortMenu = ref(false)
const openDropdown = ref<string | null>(null)
const bulkMode = ref(false)
const selectedGifts = ref<number[]>([])

// Pagination
const currentPage = ref(1)
const totalPages = ref(50)
const limit = 50

// Market stats
const tonPrice = ref('1.33')
const volume24h = ref('247.5K')

// Filters (Thermos-style)
interface Filters {
  names: string[]
  models: string[]
  backdrops: string[]
  patterns: string[]
  symbols: string[]
  rarities: string[]
  minPrice: number | null
  maxPrice: number | null
}

const filters = reactive<Filters>({
  names: [],
  models: [],
  backdrops: [],
  patterns: [],
  symbols: [],
  rarities: [],
  minPrice: null,
  maxPrice: null,
})

// Available filter options (populated from loaded gifts)
const allLoadedGifts = ref<any[]>([])
const availableNames = computed(() => [...new Set(allLoadedGifts.value.map(g => g.name).filter(Boolean))].sort())
const availableModels = computed(() => [...new Set(allLoadedGifts.value.map(g => g.model).filter(Boolean))].sort())
const availableBackdrops = computed(() => [...new Set(allLoadedGifts.value.map(g => g.backdrop).filter(Boolean))].sort())

// Filter buttons config
const filterButtons = [
  { key: 'type', label: 'Collections', filterGroup: 'names' },
  { key: 'model', label: 'Model', filterGroup: 'models' },
  { key: 'backdrop', label: 'Background', filterGroup: 'backdrops' },
]

const isFilterActive = (key: string) => {
  const btn = filterButtons.find(f => f.key === key)
  if (!btn) return false
  const arr = filters[btn.filterGroup as keyof typeof filters]
  return Array.isArray(arr) && arr.length > 0
}

const getFilterLabel = (f: typeof filterButtons[number]) => {
  const arr = filters[f.filterGroup as keyof typeof filters]
  if (Array.isArray(arr) && arr.length > 0) {
    return arr[0] + (arr.length > 1 ? ` +${arr.length - 1}` : '')
  }
  return f.label
}

// Dropdown helpers for bottom sheet
const dropdownTitle = computed(() => {
  switch (openDropdown.value) {
    case 'type': return 'Type'
    case 'model': return 'Skin'
    case 'backdrop': return 'Backdrop'
    default: return ''
  }
})

const dropdownOptions = computed(() => {
  switch (openDropdown.value) {
    case 'type': return availableNames.value
    case 'model': return availableModels.value
    case 'backdrop': return availableBackdrops.value
    default: return []
  }
})

const isDropdownOptionActive = (opt: string) => {
  switch (openDropdown.value) {
    case 'type': return filters.names.includes(opt)
    case 'model': return filters.models.includes(opt)
    case 'backdrop': return filters.backdrops.includes(opt)
    default: return false
  }
}

const toggleDropdownOption = (opt: string) => {
  switch (openDropdown.value) {
    case 'type': toggleFilter('names', opt); break
    case 'model': toggleFilter('models', opt); break
    case 'backdrop': toggleFilter('backdrops', opt); break
  }
}

const toggleFilter = (group: 'names' | 'models' | 'backdrops' | 'patterns' | 'symbols' | 'rarities', value: string) => {
  const arr = filters[group]
  const idx = arr.indexOf(value)
  if (idx > -1) {
    arr.splice(idx, 1)
  } else {
    arr.push(value)
  }
}

const applyFilters = () => {
  currentPage.value = 1
  fetchGifts()
}

// Sort options
const sortOptions = [
  { value: 'listed_at desc', label: 'Newest first' },
  { value: 'listed_at asc', label: 'Oldest first' },
  { value: 'price asc', label: 'Price: Low to High' },
  { value: 'price desc', label: 'Price: High to Low' },
]

// Methods
const setTab = (tab: string) => {
  hapticImpact('light')
  activeTab.value = tab
  if (tab === 'upgrades') {
    router.push('/upgrade')
  }
}

const setSortBy = (value: string) => {
  hapticImpact('light')
  sortBy.value = value
  showSortMenu.value = false
  fetchGifts()
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
    const query = searchQuery.value?.trim()

    let data
    if (query) {
      data = await searchGifts(query, { limit, collection_id: undefined })
    } else {
      const params: Record<string, any> = {
        is_on_sale: true,
        sort: sortBy.value,
        limit,
        offset,
      }
      // Apply filters
      if (filters.rarities.length === 1) params.rarity = filters.rarities[0]
      if (filters.models.length === 1) params.model = filters.models[0]
      if (filters.backdrops.length === 1) params.backdrop = filters.backdrops[0]
      if (filters.patterns.length === 1) params.pattern = filters.patterns[0]
      if (filters.symbols.length === 1) params.symbol = filters.symbols[0]
      if (filters.minPrice !== null) params.min_price = filters.minPrice
      if (filters.maxPrice !== null) params.max_price = filters.maxPrice

      data = await getGifts(params)
    }

    let items = data.items || data || []

    // Client-side filtering for multi-select and name filters
    if (filters.names.length > 0) {
      items = items.filter((g: any) => filters.names.includes(g.name))
    }
    if (filters.rarities.length > 1) {
      items = items.filter((g: any) => filters.rarities.includes(g.rarity))
    }
    if (filters.models.length > 1) {
      items = items.filter((g: any) => filters.models.includes(g.model))
    }
    if (filters.backdrops.length > 1) {
      items = items.filter((g: any) => filters.backdrops.includes(g.backdrop))
    }
    if (filters.patterns.length > 1) {
      items = items.filter((g: any) => filters.patterns.includes(g.pattern))
    }
    if (filters.symbols.length > 1) {
      items = items.filter((g: any) => filters.symbols.includes(g.symbol))
    }

    // Populate filter options from first page load
    if (allLoadedGifts.value.length === 0 && items.length > 0) {
      allLoadedGifts.value = items
    }

    if (data.total) {
      totalPages.value = Math.ceil(data.total / limit)
    }

    // Preload aggregated prices from multiple markets
    const giftIds = items.map((g: any) => g.id || g.gift_id).filter(Boolean)
    if (giftIds.length > 0) {
      // Start with API data immediately
      gifts.value = items

      // Enrich with aggregated prices in background
      preloadPrices(giftIds).then(() => {
        gifts.value = enrichGiftsWithPrices(items)
      })
    } else {
      gifts.value = items
    }
  } catch (err) {
    console.error('Fetch gifts error:', err)
    gifts.value = []
  } finally {
    loading.value = false
  }
}

const fetchFilterOptions = async () => {
  try {
    const data = await getGifts({ is_on_sale: true, limit: 500 })
    const items = data.items || data || []
    if (items.length > 0) {
      allLoadedGifts.value = items
    }
  } catch {
    // Use whatever is loaded
  }
}

const fetchMarketStats = async () => {
  try {
    const data = await getStats()
    if (data.volume_24h) {
      volume24h.value = formatVolume(data.volume_24h)
    }
    if (data.ton_price) {
      tonPrice.value = data.ton_price.toFixed(2)
    }
  } catch (e) {
    // Use defaults
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

const handleBuy = (_gift: any) => {
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
  fetchFilterOptions()
})
</script>

<style scoped>
.market-view {
  min-height: 100vh;
  background: #0C0C0C;
  color: #fff;
  padding-bottom: 80px;
}

/* === Tabs === */
.tabs {
  display: flex;
  gap: 24px;
  padding: 12px 16px 0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.tabs__item {
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  font-size: 18px;
  font-weight: 600;
  padding: 8px 0 12px;
  cursor: pointer;
  position: relative;
  -webkit-tap-highlight-color: transparent;
}
.tabs__item.active {
  color: #fff;
}
.tabs__item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #fff;
  border-radius: 1px;
}

/* === Search row === */
.search-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
}
.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.06);
  border-radius: 12px;
}
.search-box__icon {
  color: rgba(255,255,255,0.3);
  flex-shrink: 0;
}
.search-box__input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: #fff;
  font-size: 14px;
}
.search-box__input::placeholder {
  color: rgba(255,255,255,0.3);
}
.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.06);
  border: none;
  border-radius: 12px;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
}
.icon-btn:active {
  background: rgba(255,255,255,0.12);
  color: #fff;
}

/* === Filters === */
.filters {
  display: flex;
  gap: 6px;
  padding: 0 16px 12px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.filters::-webkit-scrollbar { display: none; }
.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255,255,255,0.06);
  border: none;
  border-radius: 10px;
  color: rgba(255,255,255,0.5);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
}
.filter-btn.active {
  background: rgba(38,129,255,0.15);
  color: #2681FF;
}
.filter-btn:active {
  background: rgba(255,255,255,0.1);
}

/* === Grid === */
.grid-wrap {
  padding: 0 10px 20px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

/* === Pagination === */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
  padding: 12px 0;
}
.pagination__btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.06);
  border: none;
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.pagination__btn:disabled { opacity: 0.3; }
.pagination__btn:not(:disabled):active { background: rgba(255,255,255,0.12); }
.pagination__info {
  font-size: 14px;
  color: rgba(255,255,255,0.5);
}

/* === Empty state === */
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
}
.empty__title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 6px;
}
.empty__hint {
  font-size: 14px;
  color: rgba(255,255,255,0.4);
  margin: 0;
}

/* === Cart bar === */
.cart-bar {
  position: fixed;
  bottom: 64px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #1a1a1a;
  border-top: 1px solid rgba(255,255,255,0.06);
  z-index: 40;
}
.cart-bar__counter {
  display: flex;
  align-items: center;
  gap: 0;
  background: rgba(255,255,255,0.06);
  border-radius: 10px;
  overflow: hidden;
}
.cart-bar__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.cart-bar__btn:disabled { opacity: 0.3; }
.cart-bar__btn:active { color: #fff; }
.cart-bar__count {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  min-width: 24px;
  text-align: center;
}
.cart-bar__checkout {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: #2681FF;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.cart-bar__checkout:disabled { opacity: 0.5; }
.cart-bar__checkout:active { background: #1a6ae0; }

/* === Sort overlay === */
.sort-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.sort-menu {
  background: #1A1A1A;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  min-width: 240px;
  overflow: hidden;
}
.sort-menu__header {
  padding: 14px 16px 8px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.sort-menu__option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  color: #fff;
  font-size: 15px;
  text-align: left;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.sort-menu__option:active { background: rgba(255,255,255,0.06); }
.sort-menu__option.active { color: #2681FF; }
.sort-menu__option.active svg { stroke: #2681FF; }
.sort-fade-enter-active, .sort-fade-leave-active { transition: opacity 0.2s; }
.sort-fade-enter-from, .sort-fade-leave-to { opacity: 0; }

/* === Filter bottom sheet === */
.filter-sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 300;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.filter-sheet {
  width: 100%;
  max-width: 480px;
  max-height: 65vh;
  background: #1A1A1A;
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
}
.filter-sheet__handle {
  width: 36px;
  height: 4px;
  background: rgba(255,255,255,0.2);
  border-radius: 2px;
  margin: 10px auto 0;
}
.filter-sheet__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px 10px;
}
.filter-sheet__title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}
.filter-sheet__close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.06);
  border: none;
  border-radius: 10px;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.filter-sheet__body {
  flex: 1;
  overflow-y: auto;
  padding: 8px 20px 16px;
  -webkit-overflow-scrolling: touch;
}
.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.filter-chip {
  padding: 8px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid transparent;
  border-radius: 10px;
  color: rgba(255,255,255,0.6);
  font-size: 14px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.filter-chip:active { background: rgba(255,255,255,0.1); }
.filter-chip.active {
  background: rgba(38,129,255,0.12);
  border-color: rgba(38,129,255,0.4);
  color: #2681FF;
}
.filter-sheet__footer {
  padding: 12px 20px 20px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.filter-sheet__done {
  width: 100%;
  padding: 14px;
  background: #2681FF;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.filter-sheet__done:active { opacity: 0.85; }
.filter-overlay-enter-active, .filter-overlay-leave-active { transition: opacity 0.25s; }
.filter-overlay-enter-from, .filter-overlay-leave-to { opacity: 0; }
.sheet-slide-enter-active { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.sheet-slide-leave-active { transition: transform 0.2s ease-in; }
.sheet-slide-enter-from, .sheet-slide-leave-to { transform: translateY(100%); }
</style>
