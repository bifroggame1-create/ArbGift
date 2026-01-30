<template>
  <router-link
    :to="`/gift/${gift.id}`"
    class="block bg-gray-800 rounded-xl overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all transform hover:scale-[1.02]"
    @click="hapticImpact('light')"
  >
    <!-- Image -->
    <div class="relative aspect-square bg-gradient-to-br from-gray-700 to-gray-900">
      <img
        v-if="gift.image_url"
        :src="gift.image_url"
        :alt="gift.name"
        class="w-full h-full object-cover"
        loading="lazy"
      />
      <div v-else class="flex items-center justify-center h-full text-6xl">
        🎁
      </div>

      <!-- Rarity badge -->
      <div
        v-if="gift.rarity"
        class="absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-semibold backdrop-blur-sm"
        :class="rarityClass(gift.rarity)"
      >
        {{ gift.rarity }}
      </div>
    </div>

    <!-- Content -->
    <div class="p-3">
      <h3 class="font-semibold text-sm mb-1 truncate">{{ gift.name }}</h3>

      <div class="flex items-center justify-between">
        <PriceTag v-if="gift.min_price_ton" :price="gift.min_price_ton" />
        <span v-else class="text-gray-500 text-sm">Not on sale</span>

        <span v-if="gift.listings_count > 0" class="text-xs text-gray-400">
          {{ gift.listings_count }} listing{{ gift.listings_count > 1 ? 's' : '' }}
        </span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { Gift } from '../api/client'
import { useTelegram } from '../composables/useTelegram'
import PriceTag from './PriceTag.vue'

defineProps<{
  gift: Gift
}>()

const { hapticImpact } = useTelegram()

const rarityClass = (rarity: string) => {
  const classes: Record<string, string> = {
    common: 'bg-gray-600/80 text-gray-200',
    uncommon: 'bg-green-600/80 text-green-100',
    rare: 'bg-blue-600/80 text-blue-100',
    epic: 'bg-purple-600/80 text-purple-100',
    legendary: 'bg-yellow-600/80 text-yellow-100',
  }
  return classes[rarity.toLowerCase()] || classes.common
}
</script>
