<template>
  <div class="market-view min-h-screen bg-[#0f1419] pb-24">
    <!-- Header -->
    <div class="bg-gradient-to-b from-[#1a2332] to-[#0f1419] px-4 pt-6 pb-4 sticky top-0 z-10">
      <div class="flex items-center justify-between mb-4">
        <button @click="router.back()" class="text-white">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
        <h1 class="text-xl font-bold text-white">Магазин</h1>
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1">
            <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/>
            </svg>
            <span class="text-white font-semibold">{{ userBalance.toFixed(2) }}</span>
          </div>
          <button class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-lg">
            +
          </button>
        </div>
      </div>

      <div class="text-sm text-gray-400 mb-4">
        • {{ onlineCount }} онлайн
      </div>
    </div>

    <!-- Tabs -->
    <div class="sticky top-[88px] bg-[#0f1419] z-10 px-4 mb-4">
      <div class="flex gap-4 border-b border-gray-800">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-3 font-medium transition-all relative',
            activeTab === tab.id
              ? 'text-white'
              : 'text-gray-500'
          ]"
        >
          {{ tab.label }}
          <div
            v-if="activeTab === tab.id"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500"
          ></div>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="px-4 mb-4 flex gap-2">
      <button
        class="flex items-center gap-2 bg-[#1a2332] text-white px-4 py-2 rounded-lg text-sm"
        @click="toggleSort"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/>
        </svg>
      </button>

      <button
        v-for="filter in filters"
        :key="filter.id"
        @click="toggleFilter(filter.id)"
        class="flex items-center gap-2 bg-[#1a2332] text-white px-4 py-2 rounded-lg text-sm"
      >
        {{ filter.label }}
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
    </div>

    <!-- Gifts Grid -->
    <div class="px-4">
      <div class="grid grid-cols-2 gap-3">
        <div
          v-for="gift in displayedGifts"
          :key="gift.id"
          class="gift-card rounded-2xl overflow-hidden cursor-pointer hover:scale-105 transition-transform"
          :style="{ background: gift.background }"
          @click="openGift(gift)"
        >
          <!-- 3D Gift Icon -->
          <div class="aspect-square flex items-center justify-center p-4">
            <div class="text-6xl">{{ gift.icon }}</div>
          </div>

          <!-- Gift Info -->
          <div class="p-3 bg-black/20 backdrop-blur-sm">
            <div class="text-white font-semibold text-sm mb-1">{{ gift.name }}</div>
            <div class="text-white/60 text-xs mb-2">#{{ gift.serial }}</div>

            <!-- Price Button -->
            <button class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-semibold flex items-center justify-center gap-1">
              <span>{{ gift.price }}</span>
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="mt-6 text-center">
        <button
          @click="loadMore"
          class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold"
        >
          Load More
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'

const router = useRouter()
const { hapticImpact } = useTelegram()

const userBalance = ref(0.16)
const onlineCount = ref(39)
const activeTab = ref('gifts')
const hasMore = ref(true)

const tabs = [
  { id: 'gifts', label: 'Гифты' },
  { id: 'lootboxes', label: 'Лутпаки' },
  { id: 'upgrades', label: 'Апгрейды' },
  { id: 'items', label: 'Ништяки' },
]

const filters = [
  { id: 'type', label: 'Тип' },
  { id: 'skin', label: 'Скин' },
  { id: 'background', label: 'Фон' },
]

// Mock gift data matching screenshot
const gifts = ref([
  {
    id: 3440,
    name: 'Perfume Bottle',
    serial: '3440',
    price: 211,
    icon: '🧴',
    background: 'linear-gradient(135deg, #d97e7c 0%, #c16361 100%)',
  },
  {
    id: 1617,
    name: 'Mini Oscar',
    serial: '1617',
    price: 194,
    icon: '🏆',
    background: 'linear-gradient(135deg, #a66d5c 0%, #8b5a4a 100%)',
  },
  {
    id: 2782,
    name: 'Nail Bracelet',
    serial: '2782',
    price: 154,
    icon: '💍',
    background: 'linear-gradient(135deg, #c4b454 0%, #a89842 100%)',
  },
  {
    id: 4021,
    name: 'Loot Bag',
    serial: '4021',
    price: 153,
    icon: '👜',
    background: 'linear-gradient(135deg, #66b366 0%, #4a9b4a 100%)',
  },
  {
    id: 10681,
    name: 'Loot Bag',
    serial: '10681',
    price: 153,
    icon: '👜',
    background: 'linear-gradient(135deg, #66b366 0%, #4a9b4a 100%)',
  },
  {
    id: 14353,
    name: 'Scared Cat',
    serial: '14353',
    price: 152,
    icon: '🐱',
    background: 'linear-gradient(135deg, #c17b9e 0%, #a5678a 100%)',
  },
])

const displayedGifts = computed(() => gifts.value)

const toggleSort = () => {
  hapticImpact('light')
  // TODO: Implement sort logic
}

const toggleFilter = (filterId: string) => {
  hapticImpact('light')
  // TODO: Implement filter logic
  console.log('Toggle filter:', filterId)
}

const openGift = (gift: any) => {
  hapticImpact('medium')
  router.push(`/gift/${gift.id}`)
}

const loadMore = () => {
  hapticImpact('light')
  // TODO: Load more gifts
}
</script>

<style scoped>
.gift-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style>
