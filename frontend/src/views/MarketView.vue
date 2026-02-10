<template>
  <!--
    myballs.io Market Page Design
    Background: #0C0C0C (inherited from --mb-bg)
    Font: Chroma ST (font-display)
  -->
  <div class="market-view">
    <!-- Online indicator -->
    <div class="online-indicator">
      <span class="online-dot"></span>
      <span class="online-text">22 online</span>
    </div>

    <!-- Header: Title + Balance -->
    <div class="market-header">
      <div class="market-header__spacer"></div>
      <h1 class="market-title">Market</h1>
      <div class="market-header__right">
        <BalancePill :balance="0" @add="() => {}" />
      </div>
    </div>

    <!-- Tab bar -->
    <nav class="market-tabs">
      <div class="market-tabs__scroll">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="market-tabs__item"
          :class="{ active: activeTab === tab.id }"
          @click="setTab(tab.id)"
        >
          {{ tab.label }}
        </button>
      </div>
    </nav>

    <!-- Filter bar -->
    <div class="filter-bar">
      <!-- Sort icon button -->
      <button class="filter-bar__sort-btn" @click="showSortMenu = !showSortMenu">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18M6 12h12M9 18h6"/>
        </svg>
      </button>

      <!-- Type dropdown -->
      <button
        class="filter-bar__dropdown"
        :class="{ 'has-value': filters.names.length > 0 }"
        @click="openDropdown = openDropdown === 'type' ? null : 'type'"
      >
        <span>{{ filters.names.length > 0 ? filters.names[0] + (filters.names.length > 1 ? ` +${filters.names.length - 1}` : '') : 'Type' }}</span>
        <svg v-if="filters.names.length === 0" class="filter-bar__chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="m6 9 6 6 6-6"/>
        </svg>
        <svg v-else class="filter-bar__clear" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" @click.stop="filters.names = []; applyFilters()">
          <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
        </svg>
      </button>

      <!-- Skin / Model dropdown -->
      <button
        class="filter-bar__dropdown"
        :class="{ 'has-value': filters.models.length > 0 }"
        @click="openDropdown = openDropdown === 'model' ? null : 'model'"
      >
        <span>{{ filters.models.length > 0 ? filters.models[0] + (filters.models.length > 1 ? ` +${filters.models.length - 1}` : '') : 'Skin' }}</span>
        <svg v-if="filters.models.length === 0" class="filter-bar__chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="m6 9 6 6 6-6"/>
        </svg>
        <svg v-else class="filter-bar__clear" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" @click.stop="filters.models = []; applyFilters()">
          <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
        </svg>
      </button>

      <!-- Backdrop dropdown -->
      <button
        class="filter-bar__dropdown"
        :class="{ 'has-value': filters.backdrops.length > 0 }"
        @click="openDropdown = openDropdown === 'backdrop' ? null : 'backdrop'"
      >
        <span>{{ filters.backdrops.length > 0 ? filters.backdrops[0] + (filters.backdrops.length > 1 ? ` +${filters.backdrops.length - 1}` : '') : 'Backdrop' }}</span>
        <svg v-if="filters.backdrops.length === 0" class="filter-bar__chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="m6 9 6 6 6-6"/>
        </svg>
        <svg v-else class="filter-bar__clear" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" @click.stop="filters.backdrops = []; applyFilters()">
          <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
        </svg>
      </button>
    </div>

    <!-- Active Filter Chips -->
    <div v-if="activeFilterTags.length > 0" class="active-filters">
      <button
        v-for="tag in activeFilterTags"
        :key="tag.key"
        class="active-filter-chip"
        @click="removeFilterTag(tag)"
      >
        <span>{{ tag.label }}</span>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
        </svg>
      </button>
      <button class="clear-all-btn" @click="resetFilters(); applyFilters()">Clear</button>
    </div>

    <!-- Sort Dropdown Overlay -->
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

    <!-- Gift Grid -->
    <div class="gift-grid-wrapper">
      <!-- Skeleton loading state -->
      <div v-if="loading" class="gift-grid">
        <SkeletonCard v-for="i in 12" :key="'skeleton-' + i" />
      </div>

      <!-- Loaded grid -->
      <div v-else class="gift-grid">
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
        <button
          class="pagination__btn"
          :disabled="currentPage <= 1"
          @click="prevPage"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>

        <span class="pagination__info">
          <span class="pagination__current">{{ currentPage }}</span>
          <span class="pagination__sep">/</span>
          <span class="pagination__total">{{ totalPages }}</span>
        </span>

        <button
          class="pagination__btn"
          :disabled="currentPage >= totalPages"
          @click="nextPage"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && gifts.length === 0" class="empty-state">
        <div class="empty-state__icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 8v13H3V8"/>
            <path d="M1 3h22v5H1z"/>
            <path d="M10 12h4"/>
          </svg>
        </div>
        <p class="empty-state__text">No gifts available</p>
        <p class="empty-state__hint">Try adjusting your filters</p>
      </div>
    </div>

    <!-- Bulk Buy FAB -->
    <Transition name="fab-pop">
      <button
        v-if="selectedGifts.length > 0"
        class="bulk-fab"
        @click="bulkBuy"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
          <path d="M3 6h18"/>
          <path d="M16 10a4 4 0 0 1-8 0"/>
        </svg>
        <span>{{ selectedGifts.length }}</span>
      </button>
    </Transition>

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
                  >
                    {{ opt }}
                  </button>
                </div>
              </div>
              <div class="filter-sheet__footer">
                <button class="filter-sheet__done" @click="openDropdown = null; applyFilters()">
                  Done
                </button>
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
import BalancePill from '../components/BalancePill.vue'
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
const openDropdown = ref<'type' | 'model' | 'backdrop' | null>(null)
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

const rarityOptions = [
  { value: 'common', label: 'Common', color: '#6b7280' },
  { value: 'uncommon', label: 'Uncommon', color: '#22c55e' },
  { value: 'rare', label: 'Rare', color: '#3b82f6' },
  { value: 'epic', label: 'Epic', color: '#a855f7' },
  { value: 'legendary', label: 'Legendary', color: '#f59e0b' },
  { value: 'mythic', label: 'Mythic', color: '#ef4444' },
]


interface FilterTag {
  key: string
  group: string
  value: string
  label: string
}

const activeFilterTags = computed<FilterTag[]>(() => {
  const tags: FilterTag[] = []
  filters.names.forEach(v => tags.push({ key: `name-${v}`, group: 'names', value: v, label: v }))
  filters.models.forEach(v => tags.push({ key: `model-${v}`, group: 'models', value: v, label: `Skin: ${v}` }))
  filters.backdrops.forEach(v => tags.push({ key: `backdrop-${v}`, group: 'backdrops', value: v, label: `Backdrop: ${v}` }))
  filters.patterns.forEach(v => tags.push({ key: `pattern-${v}`, group: 'patterns', value: v, label: `Pattern: ${v}` }))
  filters.symbols.forEach(v => tags.push({ key: `symbol-${v}`, group: 'symbols', value: v, label: `Symbol: ${v}` }))
  filters.rarities.forEach(v => {
    const opt = rarityOptions.find(r => r.value === v)
    tags.push({ key: `rarity-${v}`, group: 'rarities', value: v, label: opt?.label || v })
  })
  if (filters.minPrice !== null) tags.push({ key: 'minPrice', group: 'minPrice', value: String(filters.minPrice), label: `from ${filters.minPrice} TON` })
  if (filters.maxPrice !== null) tags.push({ key: 'maxPrice', group: 'maxPrice', value: String(filters.maxPrice), label: `to ${filters.maxPrice} TON` })
  return tags
})

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

const removeFilterTag = (tag: FilterTag) => {
  if (tag.group === 'minPrice') {
    filters.minPrice = null
  } else if (tag.group === 'maxPrice') {
    filters.maxPrice = null
  } else {
    const arr = filters[tag.group as keyof typeof filters] as string[]
    const idx = arr.indexOf(tag.value)
    if (idx > -1) arr.splice(idx, 1)
  }
  applyFilters()
}

const resetFilters = () => {
  filters.names = []
  filters.models = []
  filters.backdrops = []
  filters.patterns = []
  filters.symbols = []
  filters.rarities = []
  filters.minPrice = null
  filters.maxPrice = null
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
/* ============================================
   myballs.io Market Page
   --mb-bg: #0C0C0C
   --mb-primary: #34CDEF
   --mb-card: rgba(255, 255, 255, 0.05)
   --mb-text-secondary: rgba(255, 255, 255, 0.5)
   --mb-radius-lg: 16px
   --mb-radius-md: 12px
   --mb-content-padding: 15px
   ============================================ */

.market-view {
  min-height: 100vh;
  background: var(--mb-bg, #0C0C0C);
  color: #fff;
  padding-bottom: 100px;
}

/* --- Online indicator --- */
.online-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 0 4px;
}

.online-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.online-text {
  font-size: 12px;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  font-weight: 400;
}

/* --- Header --- */
.market-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px var(--mb-content-padding, 15px) 12px;
}

.market-header__spacer {
  width: 80px; /* Balance against right side for centering */
}

.market-title {
  font-family: 'Chroma ST', var(--mb-font-display, system-ui), sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  text-align: center;
  flex: 1;
}

.market-header__right {
  display: flex;
  justify-content: flex-end;
  min-width: 80px;
}

/* --- Tab bar --- */
.market-tabs {
  padding: 0 var(--mb-content-padding, 15px);
}

.market-tabs__scroll {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding-bottom: 1px;
}

.market-tabs__scroll::-webkit-scrollbar {
  display: none;
}

.market-tabs__item {
  position: relative;
  background: none;
  border: none;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  font-size: 15px;
  font-weight: 600;
  padding: 10px 0 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.market-tabs__item.active {
  color: #fff;
}

.market-tabs__item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #fff;
  border-radius: 1px 1px 0 0;
}

/* --- Filter bar --- */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px var(--mb-content-padding, 15px);
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.filter-bar::-webkit-scrollbar {
  display: none;
}

.filter-bar__sort-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--mb-card, rgba(255, 255, 255, 0.05));
  border: none;
  border-radius: var(--mb-radius-md, 12px);
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s, color 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.filter-bar__sort-btn:active {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.filter-bar__dropdown {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--mb-card, rgba(255, 255, 255, 0.05));
  border: none;
  border-radius: var(--mb-radius-md, 12px);
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.2s, color 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.filter-bar__dropdown.has-value {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.filter-bar__dropdown:active {
  background: rgba(255, 255, 255, 0.1);
}

.filter-bar__chevron {
  flex-shrink: 0;
  opacity: 0.5;
}

/* --- Active filter chips --- */
.active-filters {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 var(--mb-content-padding, 15px) 8px;
  flex-wrap: wrap;
}

.active-filter-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  background: rgba(52, 205, 239, 0.12);
  border: 1px solid rgba(52, 205, 239, 0.25);
  border-radius: 8px;
  color: var(--mb-primary, #34CDEF);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.active-filter-chip:active {
  background: rgba(52, 205, 239, 0.2);
}

.active-filter-chip svg {
  opacity: 0.6;
}

.clear-all-btn {
  padding: 5px 10px;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.clear-all-btn:active {
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

/* --- Sort overlay --- */
.sort-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.sort-menu {
  background: #1A1A1A;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--mb-radius-lg, 16px);
  min-width: 240px;
  overflow: hidden;
}

.sort-menu__header {
  padding: 14px 16px 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
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
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.sort-menu__option:active {
  background: rgba(255, 255, 255, 0.06);
}

.sort-menu__option.active {
  color: var(--mb-primary, #34CDEF);
}

.sort-menu__option.active svg {
  stroke: var(--mb-primary, #34CDEF);
}

/* Sort transition */
.sort-fade-enter-active,
.sort-fade-leave-active {
  transition: opacity 0.2s ease;
}
.sort-fade-enter-from,
.sort-fade-leave-to {
  opacity: 0;
}

/* --- Gift grid --- */
.gift-grid-wrapper {
  padding: 0 12px 20px;
}

.gift-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

/* --- Pagination --- */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding: 12px 0;
}

.pagination__btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--mb-card, rgba(255, 255, 255, 0.05));
  border: none;
  border-radius: var(--mb-radius-md, 12px);
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.pagination__btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pagination__btn:not(:disabled):active {
  background: rgba(255, 255, 255, 0.1);
}

.pagination__info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.pagination__current {
  color: #fff;
  font-weight: 600;
}

.pagination__sep {
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
}

.pagination__total {
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
}

/* --- Empty state --- */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-state__icon {
  color: rgba(255, 255, 255, 0.15);
  margin-bottom: 16px;
}

.empty-state__text {
  font-size: 17px;
  color: #fff;
  font-weight: 600;
  margin: 0 0 6px;
}

.empty-state__hint {
  font-size: 14px;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  margin: 0;
}

/* --- Bulk FAB --- */
.bulk-fab {
  position: fixed;
  bottom: 90px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  background: var(--mb-primary, #34CDEF);
  border: none;
  border-radius: var(--mb-radius-lg, 16px);
  color: #000;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 24px rgba(52, 205, 239, 0.35);
  z-index: 50;
  -webkit-tap-highlight-color: transparent;
}

.bulk-fab:active {
  transform: scale(0.95);
}

.fab-pop-enter-active {
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.fab-pop-leave-active {
  transition: all 0.15s ease-in;
}
.fab-pop-enter-from,
.fab-pop-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

/* --- Filter bottom sheet --- */
.filter-sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
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
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.5);
}

.filter-sheet__handle {
  width: 36px;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
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
  background: var(--mb-card, rgba(255, 255, 255, 0.05));
  border: none;
  border-radius: 10px;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
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
  background: var(--mb-card, rgba(255, 255, 255, 0.05));
  border: 1px solid transparent;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.filter-chip:active {
  background: rgba(255, 255, 255, 0.1);
}

.filter-chip.active {
  background: rgba(52, 205, 239, 0.12);
  border-color: rgba(52, 205, 239, 0.4);
  color: var(--mb-primary, #34CDEF);
}

.filter-sheet__footer {
  padding: 12px 20px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.filter-sheet__done {
  width: 100%;
  padding: 14px;
  background: var(--mb-primary, #34CDEF);
  border: none;
  border-radius: var(--mb-radius-md, 12px);
  color: #000;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.filter-sheet__done:active {
  opacity: 0.85;
}

.filter-bar__clear {
  flex-shrink: 0;
  opacity: 0.7;
}

/* Filter transitions */
.filter-overlay-enter-active,
.filter-overlay-leave-active {
  transition: opacity 0.25s ease;
}

.filter-overlay-enter-from,
.filter-overlay-leave-to {
  opacity: 0;
}

.sheet-slide-enter-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.sheet-slide-leave-active {
  transition: transform 0.2s ease-in;
}

.sheet-slide-enter-from,
.sheet-slide-leave-to {
  transform: translateY(100%);
}
</style>
