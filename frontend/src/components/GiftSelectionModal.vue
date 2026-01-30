<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <!-- Header -->
      <div class="modal-header">
        <h2 class="modal-title">Select {{ mode === 'input' ? 'Input' : 'Target' }} Gift</h2>
        <button @click="emit('close')" class="close-button">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Search -->
      <div class="search-box">
        <svg class="search-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search gifts..."
          class="search-input"
        />
      </div>

      <!-- Filters -->
      <div class="filters">
        <button
          v-for="filter in filters"
          :key="filter.value"
          :class="{ active: selectedFilter === filter.value }"
          class="filter-button"
          @click="selectedFilter = filter.value"
        >
          {{ filter.label }}
        </button>
      </div>

      <!-- Gift Grid -->
      <div class="gift-grid-modal">
        <div v-if="loading" class="loading-grid">
          <div v-for="i in 6" :key="i" class="loading-card"></div>
        </div>

        <div v-else-if="filteredGifts.length > 0" class="grid">
          <TelegramGiftCard
            v-for="gift in filteredGifts"
            :key="gift.id"
            :gift="gift"
            @click="selectGift(gift)"
          />
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-text">No gifts found</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import TelegramGiftCard from './TelegramGiftCard.vue'
import { getGifts } from '../api/client'
import type { Gift } from '../api/client'

interface Props {
  mode: 'input' | 'target'
  excludeId?: number
}

const props = defineProps<Props>()
const emit = defineEmits(['select', 'close'])

const gifts = ref<Gift[]>([])
const loading = ref(true)
const searchQuery = ref('')
const selectedFilter = ref('all')

const filters = [
  { label: 'All', value: 'all' },
  { label: 'Common', value: 'common' },
  { label: 'Rare', value: 'rare' },
  { label: 'Epic', value: 'epic' },
  { label: 'Legendary', value: 'legendary' },
]

const filteredGifts = computed(() => {
  let result = gifts.value

  // Exclude specific ID if provided
  if (props.excludeId) {
    result = result.filter(g => g.id !== props.excludeId)
  }

  // Filter by rarity
  if (selectedFilter.value !== 'all') {
    result = result.filter(g =>
      (g.rarity || 'common').toLowerCase() === selectedFilter.value.toLowerCase()
    )
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(g =>
      g.name.toLowerCase().includes(query)
    )
  }

  return result
})

const selectGift = (gift: Gift) => {
  emit('select', gift)
}

const loadGifts = async () => {
  try {
    loading.value = true
    const response = await getGifts({ limit: 50 })
    gifts.value = response.gifts || []
  } catch (error) {
    console.error('Failed to load gifts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadGifts()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fade-in 0.2s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
  border-radius: 24px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slide-up 0.3s ease;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.close-button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.search-box {
  position: relative;
  margin: 16px 24px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.4);
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 44px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.search-input:focus {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(168, 85, 247, 0.5);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.filters {
  display: flex;
  gap: 8px;
  padding: 0 24px 16px;
  overflow-x: auto;
}

.filter-button {
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.filter-button.active {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
}

.gift-grid-modal {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px 24px;
}

.loading-grid,
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.loading-card {
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
}
</style>
