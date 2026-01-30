<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-sm border-t border-gray-800 pb-safe z-50">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex items-end justify-around py-2 relative">
        <!-- Left items -->
        <router-link
          v-for="item in leftItems"
          :key="item.name"
          :to="item.path"
          class="flex flex-col items-center py-2 px-4 rounded-lg transition-all"
          :class="isActive(item.path) ? 'text-blue-400' : 'text-gray-400 hover:text-white'"
          @click="hapticImpact('light')"
        >
          <component :is="item.icon" class="w-6 h-6 mb-1" />
          <span class="text-xs font-medium">{{ item.label }}</span>
        </router-link>

        <!-- Center Games Button -->
        <router-link
          to="/topup"
          class="relative -mt-8"
          @click="hapticImpact('medium')"
        >
          <div
            class="w-16 h-16 rounded-full flex items-center justify-center shadow-xl transition-all transform hover:scale-110 active:scale-95"
            :class="isActive('/topup') || isGameRoute() ? 'bg-gradient-to-br from-purple-600 to-pink-600' : 'bg-gradient-to-br from-blue-600 to-cyan-600'"
          >
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
            </svg>
          </div>
          <span
            class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 text-xs font-medium whitespace-nowrap"
            :class="isActive('/topup') || isGameRoute() ? 'text-purple-400' : 'text-gray-400'"
          >
            Games
          </span>
        </router-link>

        <!-- Right items -->
        <router-link
          v-for="item in rightItems"
          :key="item.name"
          :to="item.path"
          class="flex flex-col items-center py-2 px-4 rounded-lg transition-all"
          :class="isActive(item.path) ? 'text-blue-400' : 'text-gray-400 hover:text-white'"
          @click="hapticImpact('light')"
        >
          <component :is="item.icon" class="w-6 h-6 mb-1" />
          <span class="text-xs font-medium">{{ item.label }}</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'

const route = useRoute()
const { hapticImpact } = useTelegram()

const isActive = (path: string) => {
  return route.path === path
}

// SVG icons as components
const HomeIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
])

const SearchIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' })
])

const HeartIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' })
])

const UserIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' })
])

const leftItems = [
  { name: 'home', path: '/', label: 'Gifts', icon: HomeIcon },
  { name: 'search', path: '/search', label: 'Search', icon: SearchIcon },
]

const rightItems = [
  { name: 'favorites', path: '/favorites', label: 'Favorites', icon: HeartIcon },
  { name: 'profile', path: '/profile', label: 'Profile', icon: UserIcon },
]

const isGameRoute = () => {
  const gameRoutes = ['/topup', '/contracts', '/upgrade', '/aviator', '/roulette', '/stars']
  return gameRoutes.some(route => route.path.startsWith(route))
}
</script>
