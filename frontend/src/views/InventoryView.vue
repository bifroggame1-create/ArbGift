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
        <span class="items-count">{{ items.length }} предметов</span>
      </div>
      <div class="header-balance">
        <span class="balance-icon">💎</span>
        <span class="balance-value">{{ balance.toFixed(2) }}</span>
        <button class="balance-add" @click="$router.push('/topup')">+</button>
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
            <span class="price-icon">💎</span>
            {{ item.price }} TON
          </span>
        </div>
        <div class="item-rarity" :class="item.rarity">{{ item.rarity }}</div>
      </div>
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
        <span class="selected-value">{{ selectedValue.toFixed(2) }} TON</span>
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

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/pvp" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4l4 4m8 8l4 4M4 20l4-4m8-8l4-4M12 12l-8 8m16 0l-8-8m0 0l8-8M4 4l8 8"/>
        </svg>
        <span>ПвП</span>
      </router-link>
      <router-link to="/solo" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        <span>Соло</span>
      </router-link>
      <router-link to="/inventory" class="nav-item active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M3 9h18M9 21V9"/>
        </svg>
        <span>Инвентарь</span>
      </router-link>
      <router-link to="/shop" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>Магазин</span>
      </router-link>
      <router-link to="/profile" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>Профиль</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface InventoryItem {
  id: number
  name: string
  image: string
  price: number
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  bgColor: string
  type: 'gift' | 'lootbox' | 'upgrade'
}

// State
const balance = ref(4.16)
const activeTab = ref('all')
const searchQuery = ref('')
const sortAsc = ref(false)
const selectedItems = ref<number[]>([])

const tabs = [
  { id: 'all', label: 'Все', icon: '📦' },
  { id: 'gift', label: 'Гифты', icon: '🎁' },
  { id: 'lootbox', label: 'Лутбоксы', icon: '📦' },
  { id: 'upgrade', label: 'Апгрейды', icon: '⬆️' },
]

const items = ref<InventoryItem[]>([
  { id: 1, name: 'Eternal Rose', image: '/gifts/rose.webp', price: 0.27, rarity: 'rare', bgColor: '#1a1a2e', type: 'gift' },
  { id: 2, name: 'Diamond Ring', image: '/gifts/ring.webp', price: 1.02, rarity: 'epic', bgColor: '#0f3460', type: 'gift' },
  { id: 3, name: 'Lucky Charm', image: '/gifts/charm.webp', price: 0.45, rarity: 'rare', bgColor: '#16213e', type: 'gift' },
  { id: 4, name: 'Golden Key', image: '/gifts/key.webp', price: 0.06, rarity: 'common', bgColor: '#1a1a2e', type: 'gift' },
  { id: 5, name: 'Mystery Box', image: '/gifts/box.webp', price: 0.5, rarity: 'rare', bgColor: '#1a1a2e', type: 'lootbox' },
  { id: 6, name: 'Cupid Arrow', image: '/gifts/cupid.webp', price: 0.24, rarity: 'common', bgColor: '#1a1a2e', type: 'gift' },
])

const getTabCount = (tabId: string) => {
  if (tabId === 'all') return items.value.length
  return items.value.filter(i => i.type === tabId).length
}

const filteredItems = computed(() => {
  let result = items.value

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
  return items.value
    .filter(i => selectedItems.value.includes(i.id))
    .reduce((sum, i) => sum + i.price, 0)
})

const getStarStyle = (i: number) => ({
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

const toggleSelect = (id: number) => {
  const index = selectedItems.value.indexOf(id)
  if (index === -1) {
    selectedItems.value.push(id)
  } else {
    selectedItems.value.splice(index, 1)
  }
}

const sellSelected = () => {
  balance.value += selectedValue.value
  items.value = items.value.filter(i => !selectedItems.value.includes(i.id))
  selectedItems.value = []
}

const giftSelected = () => {
  alert('Функция подарка в разработке')
}

const usePvP = () => {
  // Navigate to PvP with selected items
}
</script>

<style scoped>
.inventory-view {
  min-height: 100vh;
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

.balance-icon { font-size: 14px; }
.balance-value { font-size: 14px; font-weight: 600; }

.balance-add {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 14px;
}

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

.price-icon { font-size: 10px; }

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
