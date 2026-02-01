<template>
  <div class="shop-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 20" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="shop-header">
      <div class="header-title">
        <h1>Магазин</h1>
        <span class="shop-subtitle">Гифты и лутбоксы</span>
      </div>
      <div class="header-balance">
        <span class="balance-icon">💎</span>
        <span class="balance-value">{{ balance.toFixed(2) }}</span>
        <button class="balance-add" @click="$router.push('/topup')">+</button>
      </div>
    </header>

    <!-- Tabs -->
    <div class="shop-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <!-- Featured Banner -->
    <div v-if="activeTab === 'gifts'" class="featured-banner">
      <div class="banner-content">
        <span class="banner-badge">🔥 HOT</span>
        <h3>Новая коллекция</h3>
        <p>Эксклюзивные гифты Valentine's</p>
      </div>
      <div class="banner-gift">🎁</div>
    </div>

    <!-- Gifts Grid -->
    <div v-if="activeTab === 'gifts'" class="gifts-section">
      <div class="section-header">
        <h2>💎 TON Гифты</h2>
        <button class="filter-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>
          </svg>
        </button>
      </div>

      <div class="gifts-grid">
        <div
          v-for="gift in tonGifts"
          :key="gift.id"
          class="gift-card"
          @click="selectGift(gift)"
        >
          <div class="gift-image" :style="{ background: gift.bgGradient }">
            <img :src="gift.image" :alt="gift.name" />
            <div v-if="gift.discount" class="discount-badge">-{{ gift.discount }}%</div>
          </div>
          <div class="gift-info">
            <span class="gift-name">{{ gift.name }}</span>
            <div class="gift-price-row">
              <span class="gift-price">
                <span class="price-icon">💎</span>
                {{ gift.price }} TON
              </span>
              <span v-if="gift.originalPrice" class="original-price">{{ gift.originalPrice }}</span>
            </div>
          </div>
          <div class="gift-rarity" :class="gift.rarity">{{ gift.rarity }}</div>
        </div>
      </div>
    </div>

    <!-- Lootpacks Section -->
    <div v-if="activeTab === 'lootpacks'" class="lootpacks-section">
      <div class="section-header">
        <h2>📦 Лутпаки</h2>
      </div>

      <div class="lootpacks-grid">
        <div
          v-for="pack in lootpacks"
          :key="pack.id"
          class="lootpack-card"
          :style="{ background: pack.gradient }"
          @click="selectLootpack(pack)"
        >
          <div class="pack-glow"></div>
          <div class="pack-icon">{{ pack.icon }}</div>
          <div class="pack-info">
            <span class="pack-name">{{ pack.name }}</span>
            <span class="pack-contains">{{ pack.contains }} гифтов</span>
          </div>
          <div class="pack-price">
            <span class="price-value">{{ pack.price }}</span>
            <span class="price-currency">TON</span>
          </div>
          <div class="pack-chance">
            <span>Шанс x{{ pack.maxMultiplier }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Upgrades Section -->
    <div v-if="activeTab === 'upgrades'" class="upgrades-section">
      <div class="section-header">
        <h2>⬆️ Апгрейды</h2>
      </div>

      <div class="upgrade-info-card">
        <div class="upgrade-icon">🎰</div>
        <div class="upgrade-text">
          <h3>Апгрейд гифтов</h3>
          <p>Объедините 2 гифта и получите шанс на более ценный!</p>
        </div>
        <button class="btn-upgrade" @click="$router.push('/upgrade')">
          Попробовать
        </button>
      </div>

      <div class="upgrades-list">
        <div class="upgrade-item">
          <div class="upgrade-from">
            <span class="from-icon">🎁</span>
            <span>2x Common</span>
          </div>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          <div class="upgrade-to">
            <span class="to-icon">💎</span>
            <span>1x Rare</span>
          </div>
          <span class="upgrade-chance">45%</span>
        </div>
        <div class="upgrade-item">
          <div class="upgrade-from">
            <span class="from-icon">💎</span>
            <span>2x Rare</span>
          </div>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          <div class="upgrade-to">
            <span class="to-icon">👑</span>
            <span>1x Epic</span>
          </div>
          <span class="upgrade-chance">30%</span>
        </div>
      </div>
    </div>

    <!-- Extras Section -->
    <div v-if="activeTab === 'extras'" class="extras-section">
      <div class="section-header">
        <h2>✨ Ништяки</h2>
      </div>

      <div class="extras-grid">
        <div class="extra-card" v-for="extra in extras" :key="extra.id">
          <div class="extra-icon">{{ extra.icon }}</div>
          <div class="extra-info">
            <span class="extra-name">{{ extra.name }}</span>
            <span class="extra-desc">{{ extra.description }}</span>
          </div>
          <button class="btn-buy-extra">
            {{ extra.price }} TON
          </button>
        </div>
      </div>
    </div>

    <!-- Purchase Modal -->
    <Teleport to="body">
      <div v-if="showPurchaseModal" class="modal-overlay" @click.self="showPurchaseModal = false">
        <div class="purchase-modal">
          <div class="modal-handle"></div>
          <div class="modal-header">
            <h3>Купить {{ selectedItem?.name }}</h3>
            <button class="modal-close" @click="showPurchaseModal = false">×</button>
          </div>

          <div class="modal-gift-preview">
            <div class="preview-image" :style="{ background: selectedItem?.bgGradient }">
              <img :src="selectedItem?.image" :alt="selectedItem?.name" />
            </div>
            <div class="preview-info">
              <span class="preview-name">{{ selectedItem?.name }}</span>
              <span class="preview-rarity" :class="selectedItem?.rarity">{{ selectedItem?.rarity }}</span>
            </div>
          </div>

          <div class="modal-price">
            <span class="price-label">Цена:</span>
            <span class="price-value">
              <span class="price-icon">💎</span>
              {{ selectedItem?.price }} TON
            </span>
          </div>

          <button
            class="btn-confirm-purchase"
            :disabled="balance < (selectedItem?.price || 0)"
            @click="confirmPurchase"
          >
            <span v-if="balance >= (selectedItem?.price || 0)">Купить за {{ selectedItem?.price }} TON</span>
            <span v-else>Недостаточно средств</span>
          </button>

          <button class="btn-cancel" @click="showPurchaseModal = false">
            Отмена
          </button>
        </div>
      </div>
    </Teleport>

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
      <router-link to="/inventory" class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M3 9h18M9 21V9"/>
        </svg>
        <span>Инвентарь</span>
      </router-link>
      <router-link to="/shop" class="nav-item active">
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
import { ref } from 'vue'

interface Gift {
  id: number
  name: string
  image: string
  price: number
  originalPrice?: number
  discount?: number
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  bgGradient: string
}

interface Lootpack {
  id: number
  name: string
  icon: string
  contains: number
  price: number
  maxMultiplier: number
  gradient: string
}

interface Extra {
  id: number
  name: string
  icon: string
  description: string
  price: number
}

// State
const balance = ref(4.16)
const activeTab = ref('gifts')
const showPurchaseModal = ref(false)
const selectedItem = ref<Gift | null>(null)

const tabs = [
  { id: 'gifts', label: 'Гифты', icon: '🎁' },
  { id: 'lootpacks', label: 'Лутпаки', icon: '📦' },
  { id: 'upgrades', label: 'Апгрейды', icon: '⬆️' },
  { id: 'extras', label: 'Ништяки', icon: '✨' },
]

const tonGifts = ref<Gift[]>([
  { id: 1, name: 'Eternal Rose', image: '/gifts/rose.webp', price: 0.27, rarity: 'rare', bgGradient: 'linear-gradient(135deg, #1a1a2e, #16213e)' },
  { id: 2, name: 'Diamond Ring', image: '/gifts/ring.webp', price: 1.02, originalPrice: 1.5, discount: 32, rarity: 'epic', bgGradient: 'linear-gradient(135deg, #0f3460, #16213e)' },
  { id: 3, name: 'Golden Key', image: '/gifts/key.webp', price: 0.06, rarity: 'common', bgGradient: 'linear-gradient(135deg, #1a1a2e, #0f0f1a)' },
  { id: 4, name: 'Lucky Charm', image: '/gifts/charm.webp', price: 0.45, rarity: 'rare', bgGradient: 'linear-gradient(135deg, #16213e, #1a1a2e)' },
  { id: 5, name: 'Voodoo Doll', image: '/gifts/doll.webp', price: 0.45, rarity: 'epic', bgGradient: 'linear-gradient(135deg, #1e1e3f, #2d1b4e)' },
  { id: 6, name: 'Love Potion', image: '/gifts/potion.webp', price: 0.18, rarity: 'common', bgGradient: 'linear-gradient(135deg, #2d1b4e, #1a1a2e)' },
])

const lootpacks = ref<Lootpack[]>([
  { id: 1, name: 'Стартовый', icon: '📦', contains: 3, price: 0.5, maxMultiplier: 5, gradient: 'linear-gradient(135deg, #1e3a8a, #3b82f6)' },
  { id: 2, name: 'Про', icon: '💎', contains: 5, price: 2, maxMultiplier: 10, gradient: 'linear-gradient(135deg, #7c3aed, #a855f7)' },
  { id: 3, name: 'Элитный', icon: '👑', contains: 10, price: 5, maxMultiplier: 50, gradient: 'linear-gradient(135deg, #d97706, #f59e0b)' },
])

const extras = ref<Extra[]>([
  { id: 1, name: 'VIP Статус', icon: '⭐', description: '7 дней VIP привилегий', price: 1 },
  { id: 2, name: 'Бонус удачи', icon: '🍀', description: '+10% к шансу выигрыша', price: 0.5 },
  { id: 3, name: 'Кэшбэк', icon: '💰', description: '5% возврат с проигрышей', price: 2 },
])

const getStarStyle = (i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

const selectGift = (gift: Gift) => {
  selectedItem.value = gift
  showPurchaseModal.value = true
}

const selectLootpack = (pack: Lootpack) => {
  // Handle lootpack selection
}

const confirmPurchase = () => {
  if (!selectedItem.value || balance.value < selectedItem.value.price) return

  balance.value -= selectedItem.value.price
  showPurchaseModal.value = false
  // Add to inventory logic
}
</script>

<style scoped>
.shop-view {
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
.shop-header {
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

.shop-subtitle {
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
.shop-tabs {
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

/* Featured Banner */
.featured-banner {
  margin: 0 16px 20px;
  background: linear-gradient(135deg, #7c3aed, #ec4899);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 10;
  overflow: hidden;
}

.banner-content {
  position: relative;
  z-index: 2;
}

.banner-badge {
  background: rgba(255,255,255,0.2);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 8px;
  display: inline-block;
}

.banner-content h3 {
  font-size: 18px;
  margin: 0 0 4px;
}

.banner-content p {
  font-size: 12px;
  opacity: 0.8;
  margin: 0;
}

.banner-gift {
  font-size: 48px;
  opacity: 0.9;
}

/* Section Header */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 12px;
  position: relative;
  z-index: 10;
}

.section-header h2 {
  font-size: 16px;
  margin: 0;
}

.filter-btn {
  width: 36px;
  height: 36px;
  background: #1c1c1e;
  border: none;
  border-radius: 10px;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Gifts Grid */
.gifts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.gift-card {
  background: #1c1c1e;
  border-radius: 16px;
  padding: 12px;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s;
}

.gift-card:active {
  transform: scale(0.98);
}

.gift-image {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 12px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.gift-image img {
  width: 70%;
  height: 70%;
  object-fit: contain;
}

.discount-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ef4444;
  color: #fff;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}

.gift-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.gift-name {
  font-size: 13px;
  font-weight: 600;
}

.gift-price-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.gift-price {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #4ade80;
  font-weight: 600;
}

.price-icon { font-size: 10px; }

.original-price {
  font-size: 11px;
  color: #6b7280;
  text-decoration: line-through;
}

.gift-rarity {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

.gift-rarity.common { background: #6b7280; }
.gift-rarity.rare { background: #3b82f6; }
.gift-rarity.epic { background: #8b5cf6; }
.gift-rarity.legendary { background: #f59e0b; color: #000; }

/* Lootpacks */
.lootpacks-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.lootpack-card {
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.pack-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 150px;
  height: 150px;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
  filter: blur(40px);
}

.pack-icon {
  font-size: 40px;
  position: relative;
  z-index: 2;
}

.pack-info {
  flex: 1;
  position: relative;
  z-index: 2;
}

.pack-name {
  display: block;
  font-size: 16px;
  font-weight: 700;
}

.pack-contains {
  font-size: 12px;
  opacity: 0.7;
}

.pack-price {
  text-align: right;
  position: relative;
  z-index: 2;
}

.price-value {
  display: block;
  font-size: 20px;
  font-weight: 800;
}

.price-currency {
  font-size: 12px;
  opacity: 0.7;
}

.pack-chance {
  position: absolute;
  bottom: 8px;
  right: 16px;
  font-size: 10px;
  opacity: 0.6;
}

/* Upgrades */
.upgrade-info-card {
  margin: 0 16px 20px;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 10;
}

.upgrade-icon {
  font-size: 40px;
}

.upgrade-text {
  flex: 1;
}

.upgrade-text h3 {
  font-size: 16px;
  margin: 0 0 4px;
}

.upgrade-text p {
  font-size: 12px;
  opacity: 0.8;
  margin: 0;
}

.btn-upgrade {
  background: #fff;
  color: #1e3a8a;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
}

.upgrades-list {
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 10;
}

.upgrade-item {
  background: #1c1c1e;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.upgrade-from, .upgrade-to {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.from-icon, .to-icon {
  font-size: 18px;
}

.upgrade-chance {
  margin-left: auto;
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

/* Extras */
.extras-grid {
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 10;
}

.extra-card {
  background: #1c1c1e;
  border-radius: 14px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.extra-icon {
  font-size: 32px;
}

.extra-info {
  flex: 1;
}

.extra-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
}

.extra-desc {
  font-size: 12px;
  color: #6b7280;
}

.btn-buy-extra {
  background: #3b82f6;
  color: #fff;
  border: none;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.purchase-modal {
  width: 100%;
  max-width: 500px;
  background: #1c1c1e;
  border-radius: 24px 24px 0 0;
  padding: 16px;
}

.modal-handle {
  width: 40px;
  height: 4px;
  background: #3a3a3c;
  border-radius: 2px;
  margin: 0 auto 16px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 18px;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3a3a3c;
  border: none;
  color: #fff;
  font-size: 20px;
}

.modal-gift-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image img {
  width: 60%;
  height: 60%;
  object-fit: contain;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-name {
  font-size: 16px;
  font-weight: 600;
}

.preview-rarity {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  width: fit-content;
}

.preview-rarity.common { background: #6b7280; }
.preview-rarity.rare { background: #3b82f6; }
.preview-rarity.epic { background: #8b5cf6; }

.modal-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #27272a;
  border-radius: 12px;
  margin-bottom: 16px;
}

.price-label {
  font-size: 14px;
  color: #6b7280;
}

.modal-price .price-value {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 18px;
  font-weight: 700;
  color: #4ade80;
}

.btn-confirm-purchase {
  width: 100%;
  padding: 16px;
  background: #22c55e;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 10px;
}

.btn-confirm-purchase:disabled {
  background: #3a3a3c;
  color: #6b7280;
}

.btn-cancel {
  width: 100%;
  padding: 14px;
  background: transparent;
  border: 1px solid #3a3a3c;
  border-radius: 14px;
  font-size: 14px;
  color: #6b7280;
}

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
