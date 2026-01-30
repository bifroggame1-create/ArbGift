<template>
  <div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Stats -->
    <div v-if="stats" class="grid grid-cols-3 gap-3 mb-6">
      <div class="bg-gray-800 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-blue-400">{{ stats.total_gifts }}</div>
        <div class="text-xs text-gray-400">Total Gifts</div>
      </div>
      <div class="bg-gray-800 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-green-400">{{ stats.gifts_on_sale }}</div>
        <div class="text-xs text-gray-400">On Sale</div>
      </div>
      <div class="bg-gray-800 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-purple-400">{{ stats.total_listings }}</div>
        <div class="text-xs text-gray-400">Listings</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="mb-6 space-y-3">
      <!-- Collections -->
      <div v-if="collections.length > 0" class="flex space-x-2 overflow-x-auto pb-2 no-scrollbar">
        <button
          v-for="collection in collections"
          :key="collection.id"
          class="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors"
          :class="selectedCollection === collection.id ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'"
          @click="selectCollection(collection.id)"
        >
          {{ collection.name }}
        </button>
      </div>

      <!-- Sort & Filter toggles -->
      <div class="flex items-center justify-between">
        <button
          class="px-4 py-2 bg-gray-800 rounded-lg text-sm hover:bg-gray-700 transition-colors"
          @click="toggleOnSaleFilter"
        >
          {{ onSaleOnly ? '✓' : '○' }} On Sale Only
        </button>

        <select
          v-model="sortBy"
          class="px-4 py-2 bg-gray-800 rounded-lg text-sm border-none outline-none"
        >
          <option value="recent">Recent</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="name">Name</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="loading" :full-height="true" />

    <!-- Gifts Grid -->
    <div
      v-else-if="gifts.length > 0"
      class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
    >
      <GiftCard v-for="gift in gifts" :key="gift.id" :gift="gift" />
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16">
      <div class="text-6xl mb-4">🎁</div>
      <h3 class="text-xl font-semibold mb-2">No gifts found</h3>
      <p class="text-gray-400">Try adjusting your filters</p>
    </div>

    <!-- Load More -->
    <div v-if="hasMore && !loading" class="text-center mt-8">
      <button
        class="px-6 py-3 bg-blue-600 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        @click="loadMore"
      >
        Load More
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getGifts, getCollections, getStats } from '../api/client'
import type { Gift } from '../api/client'
import GiftCard from '../components/GiftCard.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { useTelegram } from '../composables/useTelegram'

const { hapticImpact } = useTelegram()

const gifts = ref<Gift[]>([])
const collections = ref<any[]>([])
const stats = ref<any>(null)
const loading = ref(true)
const selectedCollection = ref<number | null>(null)
const onSaleOnly = ref(false)
const sortBy = ref('recent')
const offset = ref(0)
const limit = 20
const hasMore = ref(true)

const loadGifts = async (append = false) => {
  try {
    loading.value = !append

    const params: any = {
      limit,
      offset: append ? offset.value : 0,
      sort: sortBy.value,
    }

    if (selectedCollection.value) {
      params.collection_id = selectedCollection.value
    }

    if (onSaleOnly.value) {
      params.is_on_sale = true
    }

    const data = await getGifts(params)

    if (append) {
      gifts.value.push(...data.gifts)
    } else {
      gifts.value = data.gifts
      offset.value = 0
    }

    offset.value += data.gifts.length
    hasMore.value = data.gifts.length === limit
  } catch (error) {
    console.error('Failed to load gifts:', error)
  } finally {
    loading.value = false
  }
}

const loadCollections = async () => {
  try {
    const data = await getCollections()
    collections.value = data.collections || []
  } catch (error) {
    console.error('Failed to load collections:', error)
  }
}

const loadStats = async () => {
  try {
    stats.value = await getStats()
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const selectCollection = (id: number) => {
  hapticImpact('light')
  if (selectedCollection.value === id) {
    selectedCollection.value = null
  } else {
    selectedCollection.value = id
  }
}

const toggleOnSaleFilter = () => {
  hapticImpact('light')
  onSaleOnly.value = !onSaleOnly.value
}

const loadMore = () => {
  hapticImpact('light')
  loadGifts(true)
}

// Watch filters
watch([selectedCollection, onSaleOnly, sortBy], () => {
  loadGifts(false)
})

onMounted(async () => {
  await Promise.all([
    loadGifts(),
    loadCollections(),
    loadStats(),
  ])
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
