<template>
  <header class="sticky top-0 z-50 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800">
    <div class="max-w-7xl mx-auto px-4 py-3">
      <div class="flex items-center justify-between">
        <router-link to="/" class="flex items-center space-x-2">
          <span class="text-2xl">🎁</span>
          <span class="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            TON Gifts
          </span>
        </router-link>

        <router-link
          to="/search"
          class="p-2 rounded-lg hover:bg-gray-800 transition-colors"
          @click="hapticImpact('light')"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useTelegram } from '../composables/useTelegram'

const { hapticImpact } = useTelegram()
</script>
