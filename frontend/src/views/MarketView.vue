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
      <button class="icon-btn" @click="fetchGifts()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/>
          <path d="M21 3v5h-5"/>
        </svg>
      </button>
    </div>

    <!-- Filter chips (horizontal scroll) — Thermos-style -->
    <div class="filters">
      <button
        v-for="f in filterButtons"
        :key="f.key"
        class="filter-btn"
        :class="{ active: isFilterActive(f.key) }"
        @click="openFilter(f.key)"
      >
        <span>{{ getFilterLabel(f) }}</span>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <path d="m6 9 6 6 6-6"/>
        </svg>
      </button>
    </div>

    <!-- Sort + quantity row -->
    <div class="controls-row">
      <div class="controls-row__left">
        <div class="cart-bar__counter">
          <button class="cart-bar__btn" :disabled="selectedGifts.length === 0" @click="selectedGifts.pop()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/></svg>
          </button>
          <span class="cart-bar__count">{{ selectedGifts.length }}</span>
          <button class="cart-bar__btn" @click="bulkMode = !bulkMode">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
          </button>
        </div>
      </div>
      <div class="controls-row__right">
        <button class="icon-btn icon-btn--sm" @click="showSortDropdown = !showSortDropdown">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Active Filter Tags -->
    <ActiveFilterTags
      :tags="activeFilterTags"
      @remove="handleRemoveTag"
      @clear-all="clearAllFilters"
    />

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
      <button class="cart-bar__checkout" :disabled="selectedGifts.length === 0" @click="bulkBuy">
        <svg class="cart-bar__ton" width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z" fill="currentColor"/>
        </svg>
        <span>Cart ({{ selectedGifts.length }})</span>
      </button>
    </div>

    <!-- Sort Dropdown -->
    <SortDropdown
      :visible="showSortDropdown"
      :options="sortOptions"
      :current="sortBy"
      @update:visible="showSortDropdown = $event"
      @select="setSortBy"
    />

    <!-- Filter Modals -->
    <FilterListModal
      :visible="activeModal === 'collections'"
      title="Collections"
      :options="collectionOptions"
      :selected="filters.names"
      :show-thumbnails="true"
      @update:visible="activeModal = $event ? 'collections' : null"
      @apply="applyCollectionFilter"
    />

    <FilterListModal
      :visible="activeModal === 'model'"
      title="Model"
      :options="modelOptions"
      :selected="filters.models"
      :show-thumbnails="true"
      :show-rarity="true"
      @update:visible="activeModal = $event ? 'model' : null"
      @apply="applyModelFilter"
    />

    <FilterListModal
      :visible="activeModal === 'backdrop'"
      title="Background"
      :options="backdropOptions"
      :selected="filters.backdrops"
      :show-thumbnails="false"
      @update:visible="activeModal = $event ? 'backdrop' : null"
      @apply="applyBackdropFilter"
    />

    <FilterListModal
      :visible="activeModal === 'symbol'"
      title="Symbol"
      :options="symbolOptions"
      :selected="filters.symbols"
      :show-thumbnails="true"
      @update:visible="activeModal = $event ? 'symbol' : null"
      @apply="applySymbolFilter"
    />

    <PriceRangeModal
      :visible="activeModal === 'price'"
      :min-price="filters.minPrice"
      :max-price="filters.maxPrice"
      @update:visible="activeModal = $event ? 'price' : null"
      @apply="applyPriceFilter"
    />

    <GiftIdModal
      :visible="activeModal === 'giftId'"
      :gift-id="filters.giftId"
      @update:visible="activeModal = $event ? 'giftId' : null"
      @apply="applyGiftIdFilter"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GiftCard from '../components/GiftCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import FilterListModal from '../components/FilterListModal.vue'
import PriceRangeModal from '../components/PriceRangeModal.vue'
import GiftIdModal from '../components/GiftIdModal.vue'
import SortDropdown from '../components/SortDropdown.vue'
import ActiveFilterTags from '../components/ActiveFilterTags.vue'
import { useTelegram } from '../composables/useTelegram'
import { useMarketAggregator } from '../composables/useMarketAggregator'
import { getGifts, getFilters, searchGifts, getStats } from '../api/client'

const router = useRouter()
const { hapticImpact } = useTelegram()
const { preloadPrices, aggregatedData } = useMarketAggregator()

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
const sortBy = ref('price asc')
const showSortDropdown = ref(false)
const activeModal = ref<string | null>(null)
const bulkMode = ref(false)
const selectedGifts = ref<number[]>([])

// Pagination
const currentPage = ref(1)
const totalPages = ref(50)
const limit = 50

// Filters (Thermos-style — expanded)
interface Filters {
  names: string[]
  models: string[]
  backdrops: string[]
  patterns: string[]
  symbols: string[]
  rarities: string[]
  minPrice: number | null
  maxPrice: number | null
  giftId: number | null
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
  giftId: null,
})

// Filter options from backend API (not computed from loaded gifts)
const collectionOptions = ref<any[]>([])
const modelOptions = ref<any[]>([])
const backdropOptions = ref<any[]>([])
const symbolOptions = ref<any[]>([])

const mapFilterOptions = (opts: any[]) =>
  opts.map((o: any) => ({
    value: o.value,
    label: o.value,
    count: o.count,
    floorPrice: o.floor_price || undefined,
    imageUrl: o.image_url || undefined,
  })).sort((a: any, b: any) => (b.count || 0) - (a.count || 0))

// Filter button config (Thermos-style: 7 buttons)
const filterButtons = [
  { key: 'collections', label: 'Collections', filterGroup: 'names' },
  { key: 'model', label: 'Model', filterGroup: 'models' },
  { key: 'backdrop', label: 'Background', filterGroup: 'backdrops' },
  { key: 'symbol', label: 'Symbol', filterGroup: 'symbols' },
  { key: 'price', label: 'Price', filterGroup: 'price' },
  { key: 'giftId', label: 'Gift ID', filterGroup: 'giftId' },
]

const isFilterActive = (key: string) => {
  switch (key) {
    case 'collections': return filters.names.length > 0
    case 'model': return filters.models.length > 0
    case 'backdrop': return filters.backdrops.length > 0
    case 'symbol': return filters.symbols.length > 0
    case 'price': return filters.minPrice !== null || filters.maxPrice !== null
    case 'giftId': return filters.giftId !== null
    default: return false
  }
}

const getFilterLabel = (f: typeof filterButtons[number]) => {
  switch (f.key) {
    case 'collections':
      return filters.names.length > 0
        ? `Collections (${filters.names.length})`
        : 'Collections'
    case 'model':
      return filters.models.length > 0
        ? `Model (${filters.models.length})`
        : 'Model'
    case 'backdrop':
      return filters.backdrops.length > 0
        ? `Background (${filters.backdrops.length})`
        : 'Background'
    case 'symbol':
      return filters.symbols.length > 0
        ? `Symbol (${filters.symbols.length})`
        : 'Symbol'
    case 'price':
      if (filters.minPrice !== null || filters.maxPrice !== null) {
        const min = filters.minPrice ?? 0
        const max = filters.maxPrice ?? '...'
        return `${min} - ${max} TON`
      }
      return 'Price'
    case 'giftId':
      return filters.giftId !== null ? `#${filters.giftId}` : 'Gift ID'
    default: return f.label
  }
}

// Active filter tags (for removable tag bar)
const activeFilterTags = computed(() => {
  const tags: { key: string; label: string; imageUrl?: string }[] = []
  filters.names.forEach(name => {
    const opt = collectionOptions.value.find(o => o.value === name)
    tags.push({ key: 'names', label: name, imageUrl: opt?.imageUrl })
  })
  filters.models.forEach(model => {
    tags.push({ key: 'models', label: model })
  })
  filters.backdrops.forEach(backdrop => {
    tags.push({ key: 'backdrops', label: backdrop })
  })
  filters.symbols.forEach(symbol => {
    tags.push({ key: 'symbols', label: symbol })
  })
  if (filters.minPrice !== null || filters.maxPrice !== null) {
    tags.push({ key: 'price', label: `${filters.minPrice ?? 0} - ${filters.maxPrice ?? '...'} TON` })
  }
  if (filters.giftId !== null) {
    tags.push({ key: 'giftId', label: `#${filters.giftId}` })
  }
  return tags
})

const handleRemoveTag = (key: string, label: string) => {
  hapticImpact('light')
  switch (key) {
    case 'names':
      filters.names = filters.names.filter(n => n !== label)
      break
    case 'models':
      filters.models = filters.models.filter(m => m !== label)
      break
    case 'backdrops':
      filters.backdrops = filters.backdrops.filter(b => b !== label)
      break
    case 'symbols':
      filters.symbols = filters.symbols.filter(s => s !== label)
      break
    case 'price':
      filters.minPrice = null
      filters.maxPrice = null
      break
    case 'giftId':
      filters.giftId = null
      break
  }
  applyFilters()
}

const clearAllFilters = () => {
  hapticImpact('medium')
  filters.names = []
  filters.models = []
  filters.backdrops = []
  filters.patterns = []
  filters.symbols = []
  filters.rarities = []
  filters.minPrice = null
  filters.maxPrice = null
  filters.giftId = null
  applyFilters()
}

// Open filter modals
const openFilter = (key: string) => {
  hapticImpact('light')
  activeModal.value = key
}

// Apply filter handlers
const applyCollectionFilter = (selected: string[]) => {
  filters.names = selected
  applyFilters()
}
const applyModelFilter = (selected: string[]) => {
  filters.models = selected
  applyFilters()
}
const applyBackdropFilter = (selected: string[]) => {
  filters.backdrops = selected
  applyFilters()
}
const applySymbolFilter = (selected: string[]) => {
  filters.symbols = selected
  applyFilters()
}
const applyPriceFilter = (min: number | null, max: number | null) => {
  filters.minPrice = min
  filters.maxPrice = max
  applyFilters()
}
const applyGiftIdFilter = (id: number | null) => {
  filters.giftId = id
  applyFilters()
}

const applyFilters = () => {
  currentPage.value = 1
  fetchGifts()
}

// Sort options (Thermos-style: 7 options)
const sortOptions = [
  { value: 'price asc', label: 'Price: Low to High' },
  { value: 'price desc', label: 'Price: High to Low' },
  { value: 'id asc', label: 'Gift ID: Ascending' },
  { value: 'id desc', label: 'Gift ID: Descending' },
  { value: 'rarity asc', label: 'Model Rarity: Low to High' },
  { value: 'rarity desc', label: 'Model Rarity: High to Low' },
  { value: 'listed_at desc', label: 'Newest First' },
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
        sort_by: sortBy.value,
        limit,
        offset,
      }
      // All filters sent server-side (multi-value as comma-separated)
      if (filters.names.length > 0) params.gift_type = filters.names.join(',')
      if (filters.models.length > 0) params.model = filters.models.join(',')
      if (filters.backdrops.length > 0) params.backdrop = filters.backdrops.join(',')
      if (filters.patterns.length > 0) params.pattern = filters.patterns.join(',')
      if (filters.symbols.length > 0) params.symbol = filters.symbols.join(',')
      if (filters.minPrice !== null) params.price_min = filters.minPrice
      if (filters.maxPrice !== null) params.price_max = filters.maxPrice
      if (filters.giftId !== null) params.search = `#${filters.giftId}`

      data = await getGifts(params)
    }

    let items = data.items || data || []

    if (data.total) {
      totalPages.value = Math.ceil(data.total / limit)
    }

    // Show API data immediately
    gifts.value = items

    // Enrich with aggregated prices in background
    const giftIds = items.map((g: any) => g.id || g.gift_id).filter(Boolean)
    if (giftIds.length > 0) {
      preloadPrices(giftIds).then(() => {
        gifts.value = items.map((gift: any) => {
          const id = String(gift.id || gift.gift_id || '')
          const agg = aggregatedData.value.get(id)
          if (agg && agg.minPrice > 0) {
            return {
              ...gift,
              lowest_price_ton: agg.minPrice,
              lowest_price_market: agg.bestDeal?.source || gift.lowest_price_market
            }
          }
          return gift
        })
      })
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
    const filtersData = await getFilters({ is_on_sale: true })
    collectionOptions.value = mapFilterOptions(filtersData.gift_types || [])
    modelOptions.value = mapFilterOptions(filtersData.models || [])
    backdropOptions.value = mapFilterOptions(filtersData.backdrops || [])
    symbolOptions.value = mapFilterOptions(filtersData.symbols || [])
  } catch {
    // Filters will remain empty
  }
}

const fetchMarketStats = async () => {
  try {
    await getStats()
  } catch {
    // Use defaults
  }
}

const handleGiftClick = (gift: any) => {
  hapticImpact('light')
  router.push(`/gift/${gift.id}`)
}

const handleBuy = (_gift: any) => {
  hapticImpact('medium')
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
.icon-btn--sm {
  width: 36px;
  height: 36px;
  border-radius: 10px;
}

/* === Filters (Thermos-style) === */
.filters {
  display: flex;
  gap: 6px;
  padding: 0 16px 8px;
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

/* === Controls row (quantity + sort) === */
.controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 8px;
}
.controls-row__left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.controls-row__right {
  display: flex;
  align-items: center;
  gap: 8px;
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
.cart-bar__ton {
  flex-shrink: 0;
  opacity: 0.85;
}
</style>
