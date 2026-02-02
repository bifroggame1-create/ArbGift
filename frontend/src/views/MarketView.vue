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
      <button class="toolbar-btn filter-btn" :class="{ 'has-filters': activeFilterCount > 0 }" @click="showFilters = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>
        </svg>
        <span>Фильтры</span>
        <span v-if="activeFilterCount > 0" class="filter-badge">{{ activeFilterCount }}</span>
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

    <!-- Active Filter Chips -->
    <div v-if="activeFilterTags.length > 0" class="active-filters">
      <button
        v-for="tag in activeFilterTags"
        :key="tag.key"
        class="active-filter-chip"
        @click="removeFilterTag(tag)"
      >
        <span class="af-label">{{ tag.label }}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
        </svg>
      </button>
      <button class="clear-all-btn" @click="resetFilters(); applyFilters()">Очистить всё</button>
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

    <!-- Filter Sidebar (Thermos-style) -->
    <Teleport to="body">
      <Transition name="filter-overlay">
        <div v-if="showFilters" class="filter-overlay" @click.self="showFilters = false">
          <Transition name="filter-slide">
            <div v-if="showFilters" class="filter-sidebar">
              <div class="filter-header">
                <h3 class="filter-title">Фильтры</h3>
                <button class="filter-close" @click="showFilters = false">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
                  </svg>
                </button>
              </div>

              <div class="filter-body">
                <!-- Gift Name / Collection -->
                <div class="filter-section">
                  <div class="filter-section-title">Подарок</div>
                  <div class="filter-chips">
                    <button
                      v-for="name in availableNames"
                      :key="name"
                      class="filter-chip"
                      :class="{ active: filters.names.includes(name) }"
                      @click="toggleFilter('names', name)"
                    >
                      {{ name }}
                    </button>
                  </div>
                </div>

                <!-- Model -->
                <div class="filter-section" v-if="availableModels.length">
                  <div class="filter-section-title">Модель</div>
                  <div class="filter-chips">
                    <button
                      v-for="m in availableModels"
                      :key="m"
                      class="filter-chip"
                      :class="{ active: filters.models.includes(m) }"
                      @click="toggleFilter('models', m)"
                    >
                      {{ m }}
                    </button>
                  </div>
                </div>

                <!-- Backdrop -->
                <div class="filter-section" v-if="availableBackdrops.length">
                  <div class="filter-section-title">Фон</div>
                  <div class="filter-chips">
                    <button
                      v-for="b in availableBackdrops"
                      :key="b"
                      class="filter-chip"
                      :class="{ active: filters.backdrops.includes(b) }"
                      @click="toggleFilter('backdrops', b)"
                    >
                      {{ b }}
                    </button>
                  </div>
                </div>

                <!-- Pattern -->
                <div class="filter-section" v-if="availablePatterns.length">
                  <div class="filter-section-title">Паттерн</div>
                  <div class="filter-chips">
                    <button
                      v-for="p in availablePatterns"
                      :key="p"
                      class="filter-chip"
                      :class="{ active: filters.patterns.includes(p) }"
                      @click="toggleFilter('patterns', p)"
                    >
                      {{ p }}
                    </button>
                  </div>
                </div>

                <!-- Symbol -->
                <div class="filter-section" v-if="availableSymbols.length">
                  <div class="filter-section-title">Символ</div>
                  <div class="filter-chips">
                    <button
                      v-for="s in availableSymbols"
                      :key="s"
                      class="filter-chip"
                      :class="{ active: filters.symbols.includes(s) }"
                      @click="toggleFilter('symbols', s)"
                    >
                      {{ s }}
                    </button>
                  </div>
                </div>

                <!-- Rarity -->
                <div class="filter-section">
                  <div class="filter-section-title">Редкость</div>
                  <div class="filter-chips">
                    <button
                      v-for="r in rarityOptions"
                      :key="r.value"
                      class="filter-chip rarity-chip"
                      :class="{ active: filters.rarities.includes(r.value) }"
                      :style="filters.rarities.includes(r.value) ? { background: r.color, borderColor: r.color } : {}"
                      @click="toggleFilter('rarities', r.value)"
                    >
                      {{ r.label }}
                    </button>
                  </div>
                </div>

                <!-- Price Range -->
                <div class="filter-section">
                  <div class="filter-section-title">Цена (TON)</div>
                  <div class="price-range">
                    <div class="price-input-wrap">
                      <input
                        v-model.number="filters.minPrice"
                        type="number"
                        placeholder="Мин"
                        class="price-input"
                        min="0"
                        step="0.1"
                      />
                    </div>
                    <span class="price-dash">—</span>
                    <div class="price-input-wrap">
                      <input
                        v-model.number="filters.maxPrice"
                        type="number"
                        placeholder="Макс"
                        class="price-input"
                        min="0"
                        step="0.1"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="filter-footer">
                <button class="filter-reset" @click="resetFilters">Сбросить</button>
                <button class="filter-apply" @click="applyFilters">
                  Показать
                  <span v-if="activeFilterCount > 0" class="filter-apply-count">{{ activeFilterCount }}</span>
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GiftCard from '../components/GiftCard.vue'
import { useTelegram } from '../composables/useTelegram'
import { useMarketAggregator } from '../composables/useMarketAggregator'
import { getGifts, searchGifts, getStats } from '../api/client'

const router = useRouter()
const { hapticImpact } = useTelegram()
const { preloadPrices, enrichGiftsWithPrices } = useMarketAggregator()

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
const availablePatterns = computed(() => [...new Set(allLoadedGifts.value.map(g => g.pattern).filter(Boolean))].sort())
const availableSymbols = computed(() => [...new Set(allLoadedGifts.value.map(g => g.symbol).filter(Boolean))].sort())

const rarityOptions = [
  { value: 'common', label: 'Common', color: '#6b7280' },
  { value: 'uncommon', label: 'Uncommon', color: '#22c55e' },
  { value: 'rare', label: 'Rare', color: '#3b82f6' },
  { value: 'epic', label: 'Epic', color: '#a855f7' },
  { value: 'legendary', label: 'Legendary', color: '#f59e0b' },
  { value: 'mythic', label: 'Mythic', color: '#ef4444' },
]

const activeFilterCount = computed(() => {
  let count = 0
  count += filters.names.length
  count += filters.models.length
  count += filters.backdrops.length
  count += filters.patterns.length
  count += filters.symbols.length
  count += filters.rarities.length
  if (filters.minPrice !== null) count++
  if (filters.maxPrice !== null) count++
  return count
})

interface FilterTag {
  key: string
  group: string
  value: string
  label: string
}

const activeFilterTags = computed<FilterTag[]>(() => {
  const tags: FilterTag[] = []
  filters.names.forEach(v => tags.push({ key: `name-${v}`, group: 'names', value: v, label: v }))
  filters.models.forEach(v => tags.push({ key: `model-${v}`, group: 'models', value: v, label: `Модель: ${v}` }))
  filters.backdrops.forEach(v => tags.push({ key: `backdrop-${v}`, group: 'backdrops', value: v, label: `Фон: ${v}` }))
  filters.patterns.forEach(v => tags.push({ key: `pattern-${v}`, group: 'patterns', value: v, label: `Паттерн: ${v}` }))
  filters.symbols.forEach(v => tags.push({ key: `symbol-${v}`, group: 'symbols', value: v, label: `Символ: ${v}` }))
  filters.rarities.forEach(v => {
    const opt = rarityOptions.find(r => r.value === v)
    tags.push({ key: `rarity-${v}`, group: 'rarities', value: v, label: opt?.label || v })
  })
  if (filters.minPrice !== null) tags.push({ key: 'minPrice', group: 'minPrice', value: String(filters.minPrice), label: `от ${filters.minPrice} TON` })
  if (filters.maxPrice !== null) tags.push({ key: 'maxPrice', group: 'maxPrice', value: String(filters.maxPrice), label: `до ${filters.maxPrice} TON` })
  return tags
})

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
  showFilters.value = false
  currentPage.value = 1
  fetchGifts()
}

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

/* Filter Badge on toolbar button */
.filter-btn.has-filters {
  border: 1px solid #1689ff;
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #1689ff;
  border-radius: 9px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

/* Active Filter Chips Bar */
.active-filters {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px 8px;
  flex-wrap: wrap;
}

.active-filter-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(22, 137, 255, 0.15);
  border: 1px solid rgba(22, 137, 255, 0.3);
  border-radius: 8px;
  color: #1689ff;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.active-filter-chip:hover {
  background: rgba(22, 137, 255, 0.25);
}

.active-filter-chip svg {
  opacity: 0.7;
}

.clear-all-btn {
  padding: 6px 10px;
  background: none;
  border: 1px solid #3a3a3a;
  border-radius: 8px;
  color: #6d6d71;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-all-btn:hover {
  color: #fff;
  border-color: #6d6d71;
}

/* Filter Overlay & Sidebar */
.filter-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 200;
  display: flex;
  justify-content: flex-end;
}

.filter-sidebar {
  width: 340px;
  max-width: 90vw;
  height: 100%;
  background: #1a1a1a;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.4);
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #282727;
}

.filter-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.filter-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #282727;
  border: none;
  border-radius: 10px;
  color: #6d6d71;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-close:hover {
  background: #3a3a3a;
  color: #fff;
}

.filter-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #6d6d71;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-chip {
  padding: 7px 12px;
  background: #282727;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #b0b0b0;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  background: #333;
  color: #fff;
}

.filter-chip.active {
  background: rgba(22, 137, 255, 0.15);
  border-color: #1689ff;
  color: #1689ff;
}

.rarity-chip.active {
  color: #fff;
}

/* Price Range */
.price-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.price-input-wrap {
  flex: 1;
}

.price-input {
  width: 100%;
  padding: 10px 12px;
  background: #282727;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  -moz-appearance: textfield;
}

.price-input::-webkit-inner-spin-button,
.price-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
}

.price-input:focus {
  border-color: #1689ff;
}

.price-input::placeholder {
  color: #6d6d71;
}

.price-dash {
  color: #6d6d71;
  font-size: 16px;
}

/* Filter Footer */
.filter-footer {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #282727;
}

.filter-reset {
  flex: 1;
  padding: 12px;
  background: #282727;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.filter-reset:hover {
  background: #3a3a3a;
}

.filter-apply {
  flex: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #1689ff;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.filter-apply:hover {
  background: #1478e0;
}

.filter-apply-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
}

/* Filter Transitions */
.filter-overlay-enter-active,
.filter-overlay-leave-active {
  transition: opacity 0.25s ease;
}

.filter-overlay-enter-from,
.filter-overlay-leave-to {
  opacity: 0;
}

.filter-slide-enter-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.filter-slide-leave-active {
  transition: transform 0.2s ease-in;
}

.filter-slide-enter-from,
.filter-slide-leave-to {
  transform: translateX(100%);
}
</style>
