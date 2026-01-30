<template>
  <div class="max-w-4xl mx-auto px-4 py-6">
    <LoadingSpinner v-if="loading" :full-height="true" />

    <div v-else-if="gift">
      <!-- Image -->
      <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl overflow-hidden mb-6">
        <div class="aspect-square max-w-md mx-auto p-8">
          <img
            v-if="gift.image_url"
            :src="gift.image_url"
            :alt="gift.name"
            class="w-full h-full object-contain"
          />
          <div v-else class="flex items-center justify-center h-full text-9xl">
            🎁
          </div>
        </div>
      </div>

      <!-- Info -->
      <div class="bg-gray-800 rounded-2xl p-6 mb-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h1 class="text-2xl font-bold mb-2">{{ gift.name }}</h1>
            <p v-if="gift.collection_name" class="text-gray-400 text-sm">
              {{ gift.collection_name }}
            </p>
          </div>

          <div
            v-if="gift.rarity"
            class="px-3 py-1 rounded-full text-sm font-semibold"
            :class="rarityClass(gift.rarity)"
          >
            {{ gift.rarity }}
          </div>
        </div>

        <p v-if="gift.description" class="text-gray-300 mb-4">
          {{ gift.description }}
        </p>

        <!-- Metadata -->
        <div v-if="gift.backdrop || gift.model" class="flex flex-wrap gap-2 mb-4">
          <span v-if="gift.backdrop" class="px-3 py-1 bg-gray-700 rounded-full text-sm">
            🎨 {{ gift.backdrop }}
          </span>
          <span v-if="gift.model" class="px-3 py-1 bg-gray-700 rounded-full text-sm">
            🎁 {{ gift.model }}
          </span>
        </div>

        <!-- Price -->
        <div v-if="gift.min_price_ton" class="border-t border-gray-700 pt-4">
          <div class="text-gray-400 text-sm mb-1">Best Price</div>
          <PriceTag :price="gift.min_price_ton" class="text-2xl" />
        </div>
      </div>

      <!-- Listings -->
      <div class="bg-gray-800 rounded-2xl p-6">
        <h2 class="text-xl font-bold mb-4">
          Available Listings ({{ listings.length }})
        </h2>

        <LoadingSpinner v-if="loadingListings" size="sm" />

        <div v-else-if="listings.length > 0" class="space-y-3">
          <a
            v-for="listing in listings"
            :key="listing.id"
            :href="listing.listing_url"
            target="_blank"
            class="block bg-gray-900 rounded-xl p-4 hover:ring-2 hover:ring-blue-500 transition-all"
            @click="hapticImpact('medium')"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-semibold text-lg mb-1">
                  {{ listing.market_name }}
                </div>
                <div class="text-gray-400 text-xs truncate">
                  {{ shortAddress(listing.seller_address) }}
                </div>
              </div>

              <div class="text-right">
                <PriceTag :price="listing.price_ton" />
                <div class="text-xs text-blue-400 mt-1">View →</div>
              </div>
            </div>
          </a>
        </div>

        <div v-else class="text-center py-8 text-gray-400">
          No active listings
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="text-center py-16">
      <div class="text-6xl mb-4">😕</div>
      <h3 class="text-xl font-semibold mb-2">Gift not found</h3>
      <router-link to="/" class="text-blue-400 hover:text-blue-300">
        ← Back to all gifts
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getGift, getGiftListings } from '../api/client'
import type { Gift, Listing } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import PriceTag from '../components/PriceTag.vue'
import { useTelegram } from '../composables/useTelegram'

const route = useRoute()
const { hapticImpact } = useTelegram()

const gift = ref<Gift | null>(null)
const listings = ref<Listing[]>([])
const loading = ref(true)
const loadingListings = ref(true)

const loadGift = async () => {
  try {
    const id = Number(route.params.id)
    gift.value = await getGift(id)
  } catch (error) {
    console.error('Failed to load gift:', error)
  } finally {
    loading.value = false
  }
}

const loadListings = async () => {
  try {
    const id = Number(route.params.id)
    const data = await getGiftListings(id)
    listings.value = data.listings || []
  } catch (error) {
    console.error('Failed to load listings:', error)
  } finally {
    loadingListings.value = false
  }
}

const shortAddress = (address: string) => {
  if (!address) return ''
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

const rarityClass = (rarity: string) => {
  const classes: Record<string, string> = {
    common: 'bg-gray-600 text-gray-100',
    uncommon: 'bg-green-600 text-green-100',
    rare: 'bg-blue-600 text-blue-100',
    epic: 'bg-purple-600 text-purple-100',
    legendary: 'bg-yellow-600 text-yellow-100',
  }
  return classes[rarity.toLowerCase()] || classes.common
}

onMounted(async () => {
  await Promise.all([
    loadGift(),
    loadListings(),
  ])
})
</script>
