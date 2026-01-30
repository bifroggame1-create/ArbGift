<template>
  <div class="top-up-view min-h-screen bg-gradient-to-b from-gray-900 to-gray-950 pb-24">
    <!-- Header -->
    <div class="px-4 pt-6 pb-4">
      <h1 class="text-3xl font-bold text-white mb-2">🎮 Gaming Hub</h1>
      <p class="text-gray-400 text-sm">Choose your game and test your luck</p>
    </div>

    <!-- User Balance (if authenticated) -->
    <div v-if="userBalance" class="mx-4 mb-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-2xl p-4 border border-blue-500/20">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-gray-400 text-xs mb-1">Your Balance</div>
          <div class="text-2xl font-bold text-white">{{ userBalance.toFixed(2) }} TON</div>
        </div>
        <div class="text-4xl">💎</div>
      </div>
    </div>

    <!-- Game Cards Grid -->
    <div class="px-4 space-y-4">
      <!-- Contracts Game -->
      <GameCard
        title="Contracts"
        subtitle="Risk-based gift gambling"
        icon="🔥"
        gradient="from-red-600 to-orange-600"
        :stats="contractsStats"
        @click="navigateTo('/contracts')"
      >
        <template #description>
          Select 2-10 gifts, choose your risk level (Safe, Normal, or Risky), and multiply your rewards up to 100x!
        </template>
        <template #features>
          <FeatureBadge color="green">x2 Safe</FeatureBadge>
          <FeatureBadge color="blue">x8 Normal</FeatureBadge>
          <FeatureBadge color="red">x100 Risky</FeatureBadge>
        </template>
      </GameCard>

      <!-- Upgrade Game -->
      <GameCard
        title="Upgrade"
        subtitle="Transform your gifts"
        icon="⚡"
        gradient="from-purple-600 to-pink-600"
        :stats="upgradeStats"
        @click="navigateTo('/upgrade')"
      >
        <template #description>
          Spin the wheel to upgrade one gift into another. Higher value targets mean lower success probability.
        </template>
        <template #features>
          <FeatureBadge color="purple">Provably Fair</FeatureBadge>
          <FeatureBadge color="pink">Dynamic Odds</FeatureBadge>
        </template>
      </GameCard>

      <!-- Aviator Game -->
      <GameCard
        title="Aviator"
        subtitle="Crash betting game"
        icon="✈️"
        gradient="from-blue-600 to-cyan-600"
        :stats="aviatorStats"
        @click="navigateTo('/aviator')"
      >
        <template #description>
          Bet on a growing multiplier and cash out before it crashes. The longer you wait, the higher the reward!
        </template>
        <template #features>
          <FeatureBadge color="blue">Live Multiplayer</FeatureBadge>
          <FeatureBadge color="cyan">Real-time</FeatureBadge>
        </template>
      </GameCard>

      <!-- Roulette Game -->
      <GameCard
        title="Roulette"
        subtitle="Classic & Gift roulette"
        icon="🎰"
        gradient="from-green-600 to-emerald-600"
        :stats="rouletteStats"
        @click="navigateTo('/roulette')"
      >
        <template #description>
          Spin to win NFT gifts or TON prizes from a managed prize pool. Classic casino experience!
        </template>
        <template #features>
          <FeatureBadge color="green">Classic Mode</FeatureBadge>
          <FeatureBadge color="emerald">Gift Mode</FeatureBadge>
        </template>
      </GameCard>

      <!-- Stars Service -->
      <GameCard
        title="Telegram Stars"
        subtitle="Buy Stars with TON"
        icon="⭐"
        gradient="from-yellow-600 to-amber-600"
        :stats="starsStats"
        @click="navigateTo('/stars')"
      >
        <template #description>
          Exchange your TON for Telegram Stars. Use Stars for premium features and app subscriptions.
        </template>
        <template #features>
          <FeatureBadge color="yellow">Instant Exchange</FeatureBadge>
          <FeatureBadge color="amber">Low Fees</FeatureBadge>
        </template>
      </GameCard>
    </div>

    <!-- Footer Info -->
    <div class="mt-8 px-4 pb-4">
      <div class="bg-gray-800/50 rounded-xl p-4 text-center">
        <div class="text-xs text-gray-400 mb-2">🛡️ All games use provably fair algorithms</div>
        <div class="text-xs text-gray-500">Powered by TON blockchain</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'
import GameCard from '../components/GameCard.vue'
import FeatureBadge from '../components/FeatureBadge.vue'

const router = useRouter()
const { hapticImpact } = useTelegram()

// User balance (mock - replace with actual API call)
const userBalance = ref<number | null>(null)

// Game stats (mock - replace with actual API calls)
const contractsStats = ref({
  players: '1.2k',
  volume: '45.3 TON',
})

const upgradeStats = ref({
  players: '890',
  volume: '32.1 TON',
})

const aviatorStats = ref({
  players: '2.5k',
  volume: '78.9 TON',
})

const rouletteStats = ref({
  players: '1.8k',
  volume: '56.4 TON',
})

const starsStats = ref({
  exchanges: '3.4k',
  volume: '102.5 TON',
})

const navigateTo = (path: string) => {
  hapticImpact('medium')
  router.push(path)
}

onMounted(async () => {
  // Load user balance and game stats
  // TODO: Replace with actual API calls
  // userBalance.value = await getUserBalance()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
