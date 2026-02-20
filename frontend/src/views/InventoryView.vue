<template>
  <div class="inventory-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 20" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="inv-header">
      <div class="header-title">
        <h1>Инвентарь</h1>
        <span class="items-count">
          {{ isConnected ? `${items.length} NFT` : 'Не подключено' }}
        </span>
      </div>
      <div class="header-right">
        <div v-if="isConnected" class="wallet-badge" @click="refreshInventory">
          <span class="wallet-icon">👛</span>
          <span class="wallet-address">{{ shortAddress }}</span>
        </div>
        <div class="header-balance">
          <svg class="balance-icon-svg" width="14" height="14" viewBox="0 0 56 56" fill="none">
            <circle cx="28" cy="28" r="28" fill="#0098EA"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
          </svg>
          <span class="balance-value">{{ balance.toFixed(2) }}</span>
        </div>
      </div>
    </header>

    <!-- Tabs -->
    <div class="inv-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
        <span class="tab-count">{{ getTabCount(tab.id) }}</span>
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="search-box">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Поиск по названию..."
        />
      </div>
      <button class="sort-btn" @click="toggleSort">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 5h10M11 9h7M11 13h4M3 17l4 4 4-4M7 3v18"/>
        </svg>
      </button>
    </div>

    <!-- Items Grid -->
    <div v-if="filteredItems.length > 0" class="items-grid">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        :class="['item-card', { selected: selectedItems.includes(item.id) }]"
        @click="toggleSelect(item.id)"
      >
        <div class="item-checkbox" :class="{ checked: selectedItems.includes(item.id) }">
          <svg v-if="selectedItems.includes(item.id)" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        </div>
        <div class="item-image" :style="{ background: item.bgColor }">
          <img :src="item.image" :alt="item.name" />
        </div>
        <div class="item-info">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-price">
            <svg class="price-icon-svg" width="10" height="10" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
            {{ item.price }}
          </span>
        </div>
        <div class="item-rarity" :class="item.rarity">{{ item.rarity }}</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="empty-state">
      <div class="loading-spinner"></div>
      <h3>Загрузка инвентаря...</h3>
      <p>Получаем NFT из блокчейна</p>
    </div>

    <!-- Not Connected State -->
    <div v-else-if="!isConnected" class="empty-state">
      <div class="empty-icon">🔗</div>
      <h3>Кошелёк не подключён</h3>
      <p>Подключите TON кошелёк чтобы увидеть свои гифты</p>
      <button class="btn-connect" @click="connectWallet">
        Подключить кошелёк
      </button>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <h3>Ошибка загрузки</h3>
      <p>{{ error }}</p>
      <button class="btn-shop" @click="refreshInventory">
        Попробовать снова
      </button>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">📦</div>
      <h3>Инвентарь пуст</h3>
      <p>Купите гифты в магазине или выиграйте в играх</p>
      <button class="btn-shop" @click="$router.push('/shop')">
        Перейти в магазин
      </button>
    </div>

    <!-- Floating Action Bar -->
    <div v-if="selectedItems.length > 0" class="action-bar">
      <div class="action-info">
        <span class="selected-count">{{ selectedItems.length }} выбрано</span>
        <span class="selected-value">
          <svg width="10" height="10" viewBox="0 0 56 56" fill="none" style="vertical-align:middle;margin-right:2px">
            <circle cx="28" cy="28" r="28" fill="#0098EA"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
          </svg>
          {{ selectedValue.toFixed(2) }}
        </span>
      </div>
      <div class="action-buttons">
        <button class="btn-sell" @click="sellSelected">
          <span>💰</span> Продать
        </button>
        <button class="btn-gift" @click="giftSelected">
          <span>🎁</span> Подарить
        </button>
        <button class="btn-pvp" @click="usePvP">
          <span>⚔️</span> В PvP
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTonConnect } from '../composables/useTonConnect'
import { inventoryGetMy, inventoryGetSummary, type InventoryItem as ApiInventoryItem } from '../api/client'

const router = useRouter()
const { init, connect, isConnected, shortAddress } = useTonConnect()

// State
const balance = ref(0)
const activeTab = ref('all')
const searchQuery = ref('')
const sortAsc = ref(false)
const selectedItems = ref<string[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const tabs = [
  { id: 'all', label: 'Все', icon: '📦' },
  { id: 'gift', label: 'Гифты', icon: '🎁' },
]

const items = ref<ApiInventoryItem[]>([])
const summary = ref<{ total_value_ton: number }>({ total_value_ton: 0 })

// Determine rarity from price
const getRarityFromPrice = (price: number): 'common' | 'rare' | 'epic' | 'legendary' => {
  if (price >= 10) return 'legendary'
  if (price >= 3) return 'epic'
  if (price >= 0.5) return 'rare'
  return 'common'
}

const viewItems = computed(() =>
  items.value.map((item) => {
    const price = Number(item.current_floor_price_ton || 0)
    return {
      id: String(item.id),
      name: item.gift.name,
      image: item.gift.image_url || '/gifts/default.webp',
      price,
      rarity: getRarityFromPrice(price),
      bgColor: '#1a1a2e',
      type: 'gift' as const,
      inventoryId: item.id,
    }
  })
)

// Fetch inventory from API
const fetchInventory = async () => {
  loading.value = true
  error.value = null

  try {
    items.value = await inventoryGetMy(false)
    const s = await inventoryGetSummary()
    summary.value = s
    balance.value = s.total_value_ton || 0
  } catch (e: any) {
    error.value = e.message || 'Не удалось загрузить инвентарь'
    console.error('Inventory fetch error:', e)
  } finally {
    loading.value = false
  }
}

// Watch for wallet connection
watch(isConnected, (connected) => {
  if (connected) {
    fetchInventory()
  } else {
    items.value = []
    balance.value = 0
  }
})

// Initialize TON Connect
onMounted(async () => {
  await init()
  if (isConnected.value) {
    fetchInventory()
  }
})

const getTabCount = (tabId: string) => {
  if (tabId === 'all') return viewItems.value.length
  return viewItems.value.filter(i => i.type === tabId).length
}

const filteredItems = computed(() => {
  let result = viewItems.value

  // Filter by tab
  if (activeTab.value !== 'all') {
    result = result.filter(i => i.type === activeTab.value)
  }

  // Filter by search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(i => i.name.toLowerCase().includes(query))
  }

  // Sort
  result = [...result].sort((a, b) => {
    return sortAsc.value ? a.price - b.price : b.price - a.price
  })

  return result
})

const selectedValue = computed(() => {
  return viewItems.value
    .filter(i => selectedItems.value.includes(i.id))
    .reduce((sum, i) => sum + i.price, 0)
})

const getStarStyle = (_i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

const toggleSort = () => {
  sortAsc.value = !sortAsc.value
}

const toggleSelect = (id: string) => {
  const index = selectedItems.value.indexOf(id)
  if (index === -1) {
    selectedItems.value.push(id)
  } else {
    selectedItems.value.splice(index, 1)
  }
}

const sellSelected = () => {
  // TODO: Implement relayer-based selling via marketplace APIs
  alert('Функция продажи через релеер в разработке')
}

const giftSelected = () => {
  alert('Функция подарка в разработке')
}

const usePvP = () => {
  // Navigate to PvP with selected items
  const selectedAddresses = selectedItems.value.join(',')
  router.push(`/pvp?gifts=${selectedAddresses}`)
}

const connectWallet = async () => {
  try {
    await connect()
  } catch (e) {
    console.error('Failed to connect wallet:', e)
  }
}

const refreshInventory = () => {
  fetchInventory()
}
</script>

<style scoped>
.inventory-view {
  background: #000;
  color: #fff;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 90px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
}

/* Stars */
.stars-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  background: #fff;
  border-radius: 50%;
  opacity: 0.3;
  animation: twinkle 3s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.3); }
}

/* Header */
.inv-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  position: relative;
  z-index: 10;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px;
}

.items-count {
  font-size: 12px;
  color: #6b7280;
}

.header-balance {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1c1c1e;
  padding: 8px 12px;
  border-radius: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wallet-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #0088cc20 0%, #0098ea20 100%);
  border: 1px solid #0088cc40;
  padding: 6px 10px;
  border-radius: 10px;
  cursor: pointer;
}

.wallet-icon { font-size: 12px; }
.wallet-address {
  font-size: 11px;
  font-weight: 500;
  color: #0098ea;
}

.balance-icon-svg { flex-shrink: 0; margin-right: 6px; }
.balance-value { font-size: 14px; font-weight: 600; }

/* Tabs */
.inv-tabs {
  display: flex;
  gap: 8px;
  padding: 0 16px 16px;
  overflow-x: auto;
  position: relative;
  z-index: 10;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #1c1c1e;
  border: none;
  border-radius: 12px;
  color: #6b7280;
  font-size: 13px;
  white-space: nowrap;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #3b82f6;
  color: #fff;
}

.tab-icon { font-size: 14px; }
.tab-label { font-weight: 500; }

.tab-count {
  background: rgba(255,255,255,0.15);
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 11px;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  gap: 10px;
  padding: 0 16px 16px;
  position: relative;
  z-index: 10;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: #1c1c1e;
  padding: 10px 14px;
  border-radius: 12px;
}

.search-box svg {
  color: #6b7280;
  flex-shrink: 0;
}

.search-box input {
  flex: 1;
  background: none;
  border: none;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.search-box input::placeholder {
  color: #6b7280;
}

.sort-btn {
  width: 44px;
  height: 44px;
  background: #1c1c1e;
  border: none;
  border-radius: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Items Grid */
.items-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.item-card {
  background: #1c1c1e;
  border-radius: 16px;
  padding: 12px;
  position: relative;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.item-card.selected {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.item-checkbox {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  border: 2px solid #4b5563;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.item-checkbox.checked {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

.item-image {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 12px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.item-image img {
  width: 70%;
  height: 70%;
  object-fit: contain;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-price {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #4ade80;
  font-weight: 600;
}

.price-icon-svg { flex-shrink: 0; margin-right: 4px; }

.item-rarity {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

.item-rarity.common { background: #6b7280; color: #fff; }
.item-rarity.rare { background: #3b82f6; color: #fff; }
.item-rarity.epic { background: #8b5cf6; color: #fff; }
.item-rarity.legendary { background: #f59e0b; color: #000; }

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  position: relative;
  z-index: 10;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  margin: 0 0 8px;
}

.empty-state p {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 24px;
}

.btn-shop {
  background: #3b82f6;
  color: #fff;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.btn-connect {
  background: linear-gradient(135deg, #0088cc 0%, #0098ea 100%);
  color: #fff;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 auto;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #1c1c1e;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Action Bar */
.action-bar {
  position: fixed;
  bottom: 80px;
  left: 16px;
  right: 16px;
  background: #1c1c1e;
  border-radius: 16px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 50;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.5);
}

.action-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.selected-count {
  font-size: 12px;
  color: #6b7280;
}

.selected-value {
  font-size: 14px;
  font-weight: 700;
  color: #4ade80;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sell, .btn-gift, .btn-pvp {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.btn-sell { background: #22c55e; }
.btn-gift { background: #3b82f6; }
.btn-pvp { background: #f59e0b; color: #000; }

/* Bottom Nav */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #000;
  border-top: 1px solid #1c1c1e;
  display: flex;
  padding: 8px 0 24px;
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  text-decoration: none;
  font-size: 10px;
}

.nav-item.active { color: #fff; }
.nav-item svg { width: 22px; height: 22px; }
</style>
