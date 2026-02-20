<template>
  <div class="p2p-market">
    <!-- Header -->
    <header class="market-header">
      <h1 class="market-title">🤝 P2P Market</h1>
      <p class="market-subtitle">Trade Gift NFTs with other users</p>
    </header>

    <!-- Tabs -->
    <div class="tabs">
      <button
        :class="['tab', { active: activeTab === 'browse' }]"
        @click="activeTab = 'browse'"
      >
        Browse Listings
      </button>
      <button
        :class="['tab', { active: activeTab === 'my-listings' }]"
        @click="activeTab = 'my-listings'"
      >
        My Listings
      </button>
      <button
        :class="['tab', { active: activeTab === 'sell' }]"
        @click="activeTab = 'sell'"
      >
        Sell Gift
      </button>
    </div>

    <!-- Browse Listings Tab -->
    <div v-if="activeTab === 'browse'" class="tab-content">
      <!-- Filters -->
      <div class="filters">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search gifts..."
          class="search-input"
        />
        <select v-model="sortBy" class="sort-select">
          <option value="created_at">Latest</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="discount">Best Discount</option>
        </select>
      </div>

      <!-- Listings Grid -->
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="filteredListings.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No listings found</h3>
        <p>Be the first to list a gift!</p>
      </div>
      <div v-else class="listings-grid">
        <div
          v-for="listing in filteredListings"
          :key="listing.id"
          class="listing-card"
        >
          <div class="listing-image">
            <img :src="listing.gift.image_url || '/gifts/default.webp'" :alt="listing.gift.name" />
            <div v-if="listing.discount_percent && listing.discount_percent > 0" class="discount-badge">
              -{{ listing.discount_percent.toFixed(0) }}%
            </div>
          </div>
          <div class="listing-info">
            <h3 class="listing-name">{{ listing.gift.name }}</h3>
            <div class="listing-meta">
              <span v-if="listing.gift.rarity" class="rarity-badge" :class="`rarity-${listing.gift.rarity}`">
                {{ listing.gift.rarity }}
              </span>
              <span class="seller">by @{{ listing.seller_username || 'Anonymous' }}</span>
            </div>
            <div class="listing-prices">
              <div class="current-price">
                <img src="/icons/ton.svg" alt="TON" width="16" height="16" />
                <span class="price-value">{{ listing.price_ton }}</span>
              </div>
              <div v-if="listing.floor_price_ton > 0" class="floor-price">
                Floor: {{ listing.floor_price_ton }}
              </div>
            </div>
            <button @click="purchaseListing(listing)" class="buy-btn">
              Buy Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- My Listings Tab -->
    <div v-if="activeTab === 'my-listings'" class="tab-content">
      <div v-if="myListingsLoading" class="loading">Loading...</div>
      <div v-else-if="myListings.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <h3>No active listings</h3>
        <p>Create your first listing to start selling!</p>
        <button @click="activeTab = 'sell'" class="create-listing-btn">
          Create Listing
        </button>
      </div>
      <div v-else class="listings-grid">
        <div
          v-for="listing in myListings"
          :key="listing.id"
          class="listing-card my-listing"
        >
          <div class="listing-image">
            <img :src="listing.gift.image_url || '/gifts/default.webp'" :alt="listing.gift.name" />
            <div class="status-badge" :class="`status-${listing.status}`">
              {{ listing.status }}
            </div>
          </div>
          <div class="listing-info">
            <h3 class="listing-name">{{ listing.gift.name }}</h3>
            <div class="listing-meta">
              <span v-if="listing.gift.rarity" class="rarity-badge" :class="`rarity-${listing.gift.rarity}`">
                {{ listing.gift.rarity }}
              </span>
              <span class="views">{{ listing.views_count }} views</span>
            </div>
            <div class="listing-prices">
              <div class="current-price">
                <img src="/icons/ton.svg" alt="TON" width="16" height="16" />
                <span class="price-value">{{ listing.price_ton }}</span>
              </div>
            </div>
            <button
              v-if="listing.status === 'active'"
              @click="cancelListing(listing.id)"
              class="cancel-btn"
            >
              Cancel Listing
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Sell Gift Tab -->
    <div v-if="activeTab === 'sell'" class="tab-content">
      <div class="sell-section">
        <h2>Sell Your Gift</h2>
        <p class="sell-description">List a gift from your inventory for sale</p>

        <div v-if="!selectedInventoryItem" class="select-gift-section">
          <h3>1. Select Gift</h3>
          <button @click="openInventorySelector" class="select-gift-btn">
            Choose from Inventory
          </button>
        </div>

        <div v-if="selectedInventoryItem" class="selected-gift-preview">
          <div class="preview-header">
            <h3>Selected Gift</h3>
            <button @click="selectedInventoryItem = null" class="change-btn">Change</button>
          </div>
          <div class="preview-card">
            <img :src="selectedInventoryItem.gift.image_url || '/gifts/default.webp'" :alt="selectedInventoryItem.gift.name" />
            <div class="preview-details">
              <h4>{{ selectedInventoryItem.gift.name }}</h4>
              <div class="preview-meta">
                <span v-if="selectedInventoryItem.gift.rarity" class="rarity-badge" :class="`rarity-${selectedInventoryItem.gift.rarity}`">
                  {{ selectedInventoryItem.gift.rarity }}
                </span>
                <span class="floor-price">
                  Floor: {{ selectedInventoryItem.current_floor_price_ton }} TON
                </span>
              </div>
            </div>
          </div>

          <div class="price-input-section">
            <h3>2. Set Price</h3>
            <div class="price-input-wrapper">
              <img src="/icons/ton.svg" alt="TON" width="20" height="20" />
              <input
                v-model.number="sellPrice"
                type="number"
                step="0.1"
                min="0.1"
                placeholder="Enter price in TON"
                class="price-input"
              />
            </div>
            <div v-if="sellPrice > 0" class="price-suggestions">
              <button @click="sellPrice = selectedInventoryItem.current_floor_price_ton" class="suggestion">
                Floor ({{ selectedInventoryItem.current_floor_price_ton }})
              </button>
              <button @click="sellPrice = selectedInventoryItem.current_floor_price_ton * 0.9" class="suggestion">
                -10% ({{ (selectedInventoryItem.current_floor_price_ton * 0.9).toFixed(2) }})
              </button>
              <button @click="sellPrice = selectedInventoryItem.current_floor_price_ton * 0.8" class="suggestion">
                -20% ({{ (selectedInventoryItem.current_floor_price_ton * 0.8).toFixed(2) }})
              </button>
            </div>
          </div>

          <button
            @click="createListing"
            :disabled="!sellPrice || sellPrice <= 0"
            class="create-listing-btn"
          >
            Create Listing
          </button>
        </div>
      </div>
    </div>

    <!-- Inventory Selector Modal -->
    <GiftBetModal
      :open="showInventoryModal"
      :items="inventoryItems"
      :loading="inventoryLoading"
      @close="showInventoryModal = false"
      @confirm="onInventoryItemSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  p2pGetListings,
  p2pGetMyListings,
  p2pCreateListing,
  p2pCancelListing,
  p2pPurchaseListing,
  inventoryGetMy,
  type P2PTradeListing,
  type InventoryItem,
} from '../api/client'
import GiftBetModal from '../components/GiftBetModal.vue'
import { useTelegram } from '../composables/useTelegram'

const { hapticImpact } = useTelegram()

// Tabs
const activeTab = ref<'browse' | 'my-listings' | 'sell'>('browse')

// Browse listings
const listings = ref<P2PTradeListing[]>([])
const loading = ref(false)
const searchQuery = ref('')
const sortBy = ref('created_at')

const filteredListings = computed(() => {
  let result = listings.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(l => l.gift.name.toLowerCase().includes(query))
  }
  return result
})

// My listings
const myListings = ref<P2PTradeListing[]>([])
const myListingsLoading = ref(false)

// Sell gift
const showInventoryModal = ref(false)
const inventoryItems = ref<InventoryItem[]>([])
const inventoryLoading = ref(false)
const selectedInventoryItem = ref<InventoryItem | null>(null)
const sellPrice = ref(0)

// Load listings
async function loadListings() {
  try {
    loading.value = true
    const response = await p2pGetListings({ sort_by: sortBy.value, limit: 50 })
    listings.value = response.listings
  } catch (error) {
    console.error('Failed to load listings:', error)
    listings.value = []
  } finally {
    loading.value = false
  }
}

// Load my listings
async function loadMyListings() {
  try {
    myListingsLoading.value = true
    const response = await p2pGetMyListings()
    myListings.value = response.listings
  } catch (error) {
    console.error('Failed to load my listings:', error)
    myListings.value = []
  } finally {
    myListingsLoading.value = false
  }
}

// Purchase listing
async function purchaseListing(listing: P2PTradeListing) {
  if (!confirm(`Buy ${listing.gift.name} for ${listing.price_ton} TON?`)) return

  try {
    hapticImpact('medium')
    const response = await p2pPurchaseListing(listing.id)
    alert(response.message)
    await loadListings()
  } catch (error: any) {
    console.error('Failed to purchase:', error)
    alert(error.response?.data?.detail || 'Failed to purchase listing')
  }
}

// Cancel listing
async function cancelListing(listingId: number) {
  if (!confirm('Cancel this listing?')) return

  try {
    hapticImpact('medium')
    await p2pCancelListing(listingId)
    await loadMyListings()
  } catch (error: any) {
    console.error('Failed to cancel listing:', error)
    alert(error.response?.data?.detail || 'Failed to cancel listing')
  }
}

// Open inventory selector
async function openInventorySelector() {
  try {
    inventoryLoading.value = true
    inventoryItems.value = await inventoryGetMy(true)
    showInventoryModal.value = true
  } catch (error) {
    console.error('Failed to load inventory:', error)
    inventoryItems.value = []
  } finally {
    inventoryLoading.value = false
  }
}

// On inventory item selected
function onInventoryItemSelected(item: InventoryItem) {
  selectedInventoryItem.value = item
  sellPrice.value = item.current_floor_price_ton
  showInventoryModal.value = false
}

// Create listing
async function createListing() {
  if (!selectedInventoryItem.value || !sellPrice.value) return

  try {
    hapticImpact('medium')
    await p2pCreateListing({
      inventory_id: selectedInventoryItem.value.id,
      price_ton: sellPrice.value,
    })
    alert('Listing created successfully!')
    selectedInventoryItem.value = null
    sellPrice.value = 0
    activeTab.value = 'my-listings'
    await loadMyListings()
  } catch (error: any) {
    console.error('Failed to create listing:', error)
    alert(error.response?.data?.detail || 'Failed to create listing')
  }
}

// Watch sort change
import { watch } from 'vue'
watch(sortBy, () => {
  loadListings()
})

// Watch tab change
watch(activeTab, (newTab) => {
  if (newTab === 'browse') {
    loadListings()
  } else if (newTab === 'my-listings') {
    loadMyListings()
  }
})

onMounted(() => {
  loadListings()
})
</script>

<style scoped>
.p2p-market {
  min-height: 100vh;
  background: #0C0C0C;
  color: #fff;
  padding: 16px;
  padding-bottom: 100px;
}

/* Header */
.market-header {
  text-align: center;
  margin-bottom: 24px;
}

.market-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
}

.market-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  overflow-x: auto;
}

.tab {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab.active {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  border-color: transparent;
  color: #fff;
}

/* Filters */
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input,
.sort-select {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
}

.search-input {
  flex: 1;
}

.sort-select {
  min-width: 150px;
}

/* Listings Grid */
.listings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.listing-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.2s;
}

.listing-card:hover {
  border-color: rgba(168, 85, 247, 0.5);
  transform: translateY(-2px);
}

.listing-image {
  position: relative;
  aspect-ratio: 1;
  background: #1a1a1a;
}

.listing-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.discount-badge,
.status-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
}

.discount-badge {
  background: #10b981;
  color: #fff;
}

.status-badge {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  text-transform: uppercase;
  font-size: 10px;
}

.status-badge.status-sold {
  background: #ef4444;
}

.listing-info {
  padding: 12px;
}

.listing-name {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.listing-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

.rarity-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.rarity-common { background: #6b7280; }
.rarity-uncommon { background: #10b981; }
.rarity-rare { background: #3b82f6; }
.rarity-epic { background: #8b5cf6; }
.rarity-legendary { background: #f59e0b; }

.seller,
.views {
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
}

.listing-prices {
  margin-bottom: 12px;
}

.current-price {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 700;
}

.floor-price {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.buy-btn,
.cancel-btn,
.create-listing-btn {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.buy-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  color: #fff;
}

.cancel-btn {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid #ef4444;
  color: #ef4444;
}

.create-listing-btn {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  border: none;
  color: #fff;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 20px;
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
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 24px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.6);
}

/* Sell Section */
.sell-section {
  max-width: 500px;
  margin: 0 auto;
}

.sell-section h2 {
  font-size: 24px;
  margin: 0 0 8px;
}

.sell-description {
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 32px;
}

.select-gift-section,
.price-input-section {
  margin-bottom: 24px;
}

.select-gift-section h3,
.price-input-section h3 {
  font-size: 18px;
  margin: 0 0 12px;
}

.select-gift-btn {
  width: 100%;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.selected-gift-preview {
  margin-top: 24px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.change-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.preview-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 24px;
}

.preview-card img {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  object-fit: cover;
}

.preview-details {
  flex: 1;
}

.preview-details h4 {
  font-size: 16px;
  margin: 0 0 8px;
}

.preview-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px;
}

.price-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 12px;
}

.price-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  outline: none;
}

.price-suggestions {
  display: flex;
  gap: 8px;
}

.suggestion {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}
</style>
