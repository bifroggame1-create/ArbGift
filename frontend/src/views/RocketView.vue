<template>
  <div class="rocket-view min-h-screen bg-gradient-to-br from-orange-500 via-yellow-500 to-orange-500 pb-24">
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
      <div class="flex items-center gap-3">
        <div class="text-3xl">🚀</div>
        <h1 class="text-2xl font-bold text-white uppercase tracking-wider">Rocket</h1>
      </div>
      <div class="ml-auto bg-red-500 text-white px-3 py-1 rounded-lg flex items-center gap-1 text-sm font-bold">
        <span class="animate-pulse">⚡</span> HOT!
      </div>
    </div>

    <!-- Coming Soon -->
    <div class="flex flex-col items-center justify-center px-4 pt-12">
      <div class="text-9xl mb-6 animate-bounce">🚀</div>
      <h2 class="text-4xl font-bold text-white mb-4">Coming Soon</h2>
      <p class="text-white text-center mb-8">Multiplayer rocket game with live bets</p>

      <!-- Live Players Preview -->
      <div class="w-full max-w-md bg-black/20 backdrop-blur-sm rounded-2xl p-6 mb-4">
        <div class="text-white text-lg font-bold mb-4 text-center">Top Players</div>
        <div class="grid grid-cols-4 gap-2">
          <div class="bg-black/20 backdrop-blur-sm rounded-xl p-3 text-center">
            <div class="text-2xl mb-1">😊</div>
            <div class="text-xs text-white/80 font-semibold">CRYPTO</div>
            <div class="text-sm text-green-400 font-bold">9.9%</div>
          </div>
          <div class="bg-black/20 backdrop-blur-sm rounded-xl p-3 text-center">
            <div class="text-2xl mb-1">🧔</div>
            <div class="text-xs text-white/80 font-semibold">DEGEN</div>
            <div class="text-sm text-green-400 font-bold">8.8%</div>
          </div>
          <div class="bg-black/20 backdrop-blur-sm rounded-xl p-3 text-center">
            <div class="text-2xl mb-1">👩</div>
            <div class="text-xs text-white/80 font-semibold">MIKE_K</div>
            <div class="text-sm text-green-400 font-bold">13.9%</div>
          </div>
          <div class="bg-black/20 backdrop-blur-sm rounded-xl p-3 text-center">
            <div class="text-2xl mb-1">😎</div>
            <div class="text-xs text-white/80 font-semibold">TONNER</div>
            <div class="text-sm text-green-400 font-bold">14.1%</div>
          </div>
        </div>
      </div>

      <!-- Graph Preview -->
      <div class="w-full max-w-md bg-black/20 backdrop-blur-sm rounded-2xl p-6">
        <div class="relative h-40">
          <svg viewBox="0 0 200 100" class="w-full h-full">
            <path d="M20,80 Q50,20 80,80" fill="none" stroke="#60a5fa" stroke-width="3"/>
            <circle cx="50" cy="40" r="6" fill="#ef4444"/>
          </svg>
          <div class="absolute top-4 left-8 bg-green-500 text-white px-3 py-1 rounded-md text-sm font-bold">
            x1.06
          </div>
          <div class="absolute top-12 right-8 bg-green-500 text-white px-3 py-1 rounded-md text-sm font-bold">
            x1.00
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
