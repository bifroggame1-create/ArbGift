<template>
  <div class="games-view min-h-screen bg-[#0a0e27] pb-24">
    <!-- Balance Header -->
    <div class="px-4 pt-4 pb-2">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div>
            <div class="text-xs text-gray-400">Your balance</div>
            <div class="text-xl font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
              </svg>
              {{ userBalance.toFixed(3) }}
            </div>
          </div>
        </div>
        <button class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
          </svg>
          Deposit
        </button>
      </div>
    </div>

    <!-- SOLO GAMES Section -->
    <div class="px-4 mb-4">
      <h2 class="text-2xl font-bold text-white mb-4">SOLO GAMES</h2>

      <!-- Games Grid 2x2 -->
      <div class="grid grid-cols-2 gap-3 mb-4">
        <!-- Trading Card -->
        <div
          class="relative bg-gradient-to-br from-blue-900 to-blue-950 rounded-2xl p-4 overflow-hidden cursor-pointer hover:scale-105 transition-transform"
          @click="navigateTo('/trading')"
        >
          <div class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-md font-bold">NEW</div>
          <div class="h-32 flex items-center justify-center mb-2">
            <!-- Candlestick chart SVG -->
            <svg class="w-full h-full" viewBox="0 0 200 100">
              <rect x="20" y="40" width="15" height="40" fill="#ef4444"/>
              <rect x="50" y="20" width="15" height="50" fill="#22c55e"/>
              <rect x="80" y="30" width="15" height="45" fill="#22c55e"/>
              <rect x="110" y="25" width="15" height="55" fill="#ef4444"/>
              <rect x="140" y="15" width="15" height="60" fill="#22c55e"/>
              <rect x="170" y="10" width="15" height="65" fill="#22c55e"/>
            </svg>
          </div>
          <div class="text-white font-bold text-center mb-1">Трейдинг</div>
          <div class="text-gray-400 text-xs text-center mb-2">Флипай график, получай TON</div>
          <div class="flex justify-around text-xs">
            <span class="text-green-400 font-semibold">+17.7 ✓</span>
            <span class="text-green-400 font-semibold">+50.5 ✓</span>
          </div>
        </div>

        <!-- Gift Plinko Card -->
        <div
          class="relative bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-4 overflow-hidden cursor-pointer hover:scale-105 transition-transform"
          @click="navigateTo('/plinko')"
        >
          <div class="h-32 flex items-center justify-center mb-2 relative">
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center text-2xl font-bold rotate-12">
              x100
            </div>
            <div class="grid grid-cols-6 gap-1 w-full">
              <div v-for="i in 18" :key="i" class="w-3 h-3 rounded-full bg-white/30"></div>
            </div>
            <div class="absolute bottom-2 right-2 flex gap-1">
              <div class="w-8 h-8 rounded-full bg-blue-900 flex items-center justify-center">🎮</div>
              <div class="w-8 h-8 rounded-full bg-blue-900 flex items-center justify-center">🎯</div>
            </div>
          </div>
          <div class="text-white font-bold text-center">Gift Plinko</div>
        </div>

        <!-- Ball Escape Card -->
        <div
          class="relative bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl p-4 overflow-hidden cursor-pointer hover:scale-105 transition-transform"
          @click="navigateTo('/ball-escape')"
        >
          <div class="h-32 flex items-center justify-center mb-2 relative">
            <div class="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-orange-400 flex items-center justify-center text-4xl border-4 border-purple-400">
              🐸
            </div>
            <div class="absolute top-2 right-2 w-8 h-16 bg-purple-400 rounded-full"></div>
          </div>
          <div class="text-white font-bold text-center mb-1">Ball Escape</div>
          <div class="text-purple-200 text-xs text-center">ASMR быстрая игра</div>
        </div>
      </div>
    </div>

    <!-- ROULETTE Section -->
    <div class="px-4 mb-4">
      <h2 class="text-2xl font-bold text-white mb-4">ROULETTE</h2>

      <!-- HOT ROCKET Banner -->
      <div
        class="relative bg-gradient-to-r from-yellow-500 via-orange-400 to-yellow-500 rounded-2xl p-5 mb-3 overflow-hidden cursor-pointer hover:scale-[1.02] transition-transform"
        @click="navigateTo('/rocket')"
      >
        <div class="absolute top-3 left-3 bg-red-500 text-white px-3 py-1 rounded-lg flex items-center gap-1 text-sm font-bold">
          <span class="animate-pulse">⚡</span> HOT!
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="text-5xl">🚀</div>
            <div>
              <div class="text-white text-2xl font-black uppercase tracking-wider">ROCKET</div>
            </div>
          </div>

          <div class="flex gap-2">
            <div class="bg-black/20 backdrop-blur-sm rounded-xl px-3 py-2 text-center">
              <div class="text-2xl mb-1">😊</div>
              <div class="text-xs text-white/80 font-semibold">CRYPTO</div>
              <div class="text-sm text-white font-bold">9.9%</div>
            </div>
            <div class="bg-black/20 backdrop-blur-sm rounded-xl px-3 py-2 text-center">
              <div class="text-2xl mb-1">🧔</div>
              <div class="text-xs text-white/80 font-semibold">DEGEN</div>
              <div class="text-sm text-white font-bold">8.8%</div>
            </div>
            <div class="bg-black/20 backdrop-blur-sm rounded-xl px-3 py-2 text-center">
              <div class="text-2xl mb-1">👩</div>
              <div class="text-xs text-white/80 font-semibold">MIKE_K</div>
              <div class="text-sm text-white font-bold">13.9%</div>
            </div>
            <div class="bg-black/20 backdrop-blur-sm rounded-xl px-3 py-2 text-center">
              <div class="text-2xl mb-1">😎</div>
              <div class="text-xs text-white/80 font-semibold">TONNER</div>
              <div class="text-sm text-white font-bold">14.1%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Blue ROCKET Banner -->
      <div
        class="relative bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-6 mb-3 overflow-hidden cursor-pointer hover:scale-[1.02] transition-transform"
        @click="navigateTo('/rocket')"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="text-4xl">🚀</div>
            <div class="text-white text-2xl font-black uppercase">ROCKET</div>
          </div>

          <div class="flex items-center gap-4">
            <div class="relative">
              <div class="w-32 h-32">
                <svg viewBox="0 0 100 100" class="w-full h-full">
                  <path d="M20,80 Q50,20 80,80" fill="none" stroke="#60a5fa" stroke-width="3"/>
                  <circle cx="50" cy="40" r="5" fill="#ef4444"/>
                </svg>
              </div>
              <div class="absolute top-2 left-8 bg-green-500 text-white px-2 py-1 rounded-md text-xs font-bold">
                x1.06
              </div>
              <div class="absolute top-8 right-8 bg-green-500 text-white px-2 py-1 rounded-md text-xs font-bold">
                x1.00
              </div>
              <div class="absolute bottom-4 right-4 text-white text-sm">
                x1.00
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contracts & Upgrade Cards Row -->
      <div class="grid grid-cols-2 gap-3">
        <!-- Contracts -->
        <div
          class="bg-gradient-to-br from-green-600 to-green-700 rounded-2xl p-4 cursor-pointer hover:scale-105 transition-transform flex items-center justify-between"
          @click="navigateTo('/contracts')"
        >
          <div class="flex items-center gap-3">
            <div class="text-3xl">💼</div>
            <div class="text-white font-bold text-lg">CONTRACTS</div>
          </div>
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </div>

        <!-- Upgrade -->
        <div
          class="bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl p-4 cursor-pointer hover:scale-105 transition-transform flex items-center justify-between"
          @click="navigateTo('/upgrade')"
        >
          <div class="flex items-center gap-3">
            <div class="text-3xl">⚡</div>
            <div class="text-white font-bold text-lg">UPGRADE</div>
          </div>
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'

const router = useRouter()
const { hapticImpact } = useTelegram()

const userBalance = ref(0.005)

const navigateTo = (path: string) => {
  hapticImpact('medium')
  router.push(path)
}

onMounted(async () => {
  // Load user balance
  // TODO: Replace with actual API call
})
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
