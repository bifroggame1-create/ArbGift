<template>
  <div class="ball-escape-view min-h-screen bg-gradient-to-br from-purple-600 to-purple-700 pb-24">
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
      <h1 class="text-2xl font-bold text-white">🐸 Ball Escape</h1>
    </div>

    <!-- Coming Soon -->
    <div class="flex flex-col items-center justify-center px-4 pt-20">
      <div class="w-32 h-32 rounded-full bg-gradient-to-br from-yellow-400 to-orange-400 flex items-center justify-center text-7xl border-8 border-purple-400 mb-6 animate-bounce">
        🐸
      </div>
      <h2 class="text-3xl font-bold text-white mb-4">Coming Soon</h2>
      <p class="text-purple-100 text-center mb-8">ASMR быстрая игра</p>

      <div class="w-full max-w-md bg-white/5 rounded-2xl p-6 backdrop-blur-sm">
        <div class="text-center">
          <div class="text-gray-200 mb-2">Features</div>
          <div class="space-y-2">
            <div class="bg-purple-500/30 rounded-lg p-3">
              <span class="text-white">⚡ Fast gameplay</span>
            </div>
            <div class="bg-purple-500/30 rounded-lg p-3">
              <span class="text-white">🎵 ASMR sounds</span>
            </div>
            <div class="bg-purple-500/30 rounded-lg p-3">
              <span class="text-white">💰 Quick rewards</span>
            </div>
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
