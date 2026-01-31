<template>
  <div class="plinko-view min-h-screen bg-gradient-to-br from-blue-600 to-blue-700 pb-24">
    <!-- Header with Back Button -->
    <div class="px-4 pt-6 pb-4 flex items-center gap-4">
      <button
        @click="router.back()"
        class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all"
      >
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="text-2xl font-bold text-white">🎯 Gift Plinko</h1>
    </div>

    <!-- Coming Soon -->
    <div class="flex flex-col items-center justify-center px-4 pt-20">
      <div class="text-8xl mb-6">🎲</div>
      <h2 class="text-3xl font-bold text-white mb-4">Coming Soon</h2>
      <p class="text-gray-100 text-center mb-8">Drop the ball, win big rewards!</p>

      <div class="w-full max-w-md bg-white/5 rounded-2xl p-6 backdrop-blur-sm">
        <div class="flex items-center justify-between mb-4">
          <span class="text-gray-200">Max Multiplier:</span>
          <span class="text-yellow-400 font-bold text-2xl">x100</span>
        </div>
        <div class="grid grid-cols-6 gap-2 mt-6">
          <div v-for="i in 18" :key="i" class="w-8 h-8 rounded-full bg-white/20"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>
