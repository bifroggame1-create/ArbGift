<template>
  <div class="earn-view min-h-screen bg-[#0a0e27] pb-24">
    <!-- Header -->
    <div class="px-4 pt-6 pb-4">
      <h1 class="text-3xl font-bold text-white mb-2">💰 Earn</h1>
      <p class="text-gray-400 text-sm">Stake gifts and earn TON rewards</p>
    </div>

    <!-- Total Earned -->
    <div class="mx-4 mb-6">
      <div class="bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-2xl p-6 border border-green-500/20">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-gray-400 text-xs mb-1">Total Earned</div>
            <div class="text-3xl font-bold text-white">{{ totalEarned.toFixed(4) }} TON</div>
            <div class="text-green-400 text-sm mt-1">+{{ dailyRate.toFixed(2) }}% daily</div>
          </div>
          <svg class="w-16 h-16" viewBox="0 0 56 56" fill="none">
            <circle cx="28" cy="28" r="28" fill="#0098EA"/>
            <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Staking Options -->
    <div class="px-4 mb-6">
      <h2 class="text-xl font-bold text-white mb-4">Staking Pools</h2>

      <div class="space-y-3">
        <!-- Pool 1: High APY -->
        <div class="bg-gradient-to-br from-purple-900/40 to-purple-950/40 rounded-2xl p-5 border border-purple-500/30">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-white font-bold text-lg">High Yield Pool</div>
              <div class="text-purple-300 text-sm">Lock for 30 days</div>
            </div>
            <div class="bg-purple-600 text-white px-4 py-2 rounded-xl font-bold">
              15% APY
            </div>
          </div>

          <div class="flex items-center justify-between text-sm mb-3">
            <span class="text-gray-400">Min. Stake</span>
            <span class="text-white font-semibold">10 TON</span>
          </div>

          <div class="flex items-center justify-between text-sm mb-4">
            <span class="text-gray-400">Your Stake</span>
            <span class="text-white font-semibold">0 TON</span>
          </div>

          <button class="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-xl font-semibold">
            Stake Now
          </button>
        </div>

        <!-- Pool 2: Flexible -->
        <div class="bg-gradient-to-br from-blue-900/40 to-blue-950/40 rounded-2xl p-5 border border-blue-500/30">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-white font-bold text-lg">Flexible Pool</div>
              <div class="text-blue-300 text-sm">Unstake anytime</div>
            </div>
            <div class="bg-blue-600 text-white px-4 py-2 rounded-xl font-bold">
              8% APY
            </div>
          </div>

          <div class="flex items-center justify-between text-sm mb-3">
            <span class="text-gray-400">Min. Stake</span>
            <span class="text-white font-semibold">1 TON</span>
          </div>

          <div class="flex items-center justify-between text-sm mb-4">
            <span class="text-gray-400">Your Stake</span>
            <span class="text-white font-semibold">0 TON</span>
          </div>

          <button class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-semibold">
            Stake Now
          </button>
        </div>

        <!-- Pool 3: Gift Staking -->
        <div class="bg-gradient-to-br from-yellow-900/40 to-amber-950/40 rounded-2xl p-5 border border-yellow-500/30">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-white font-bold text-lg">Gift Staking</div>
              <div class="text-yellow-300 text-sm">Stake gifts, earn TON</div>
            </div>
            <div class="bg-yellow-600 text-white px-4 py-2 rounded-xl font-bold">
              12% APY
            </div>
          </div>

          <div class="flex items-center justify-between text-sm mb-3">
            <span class="text-gray-400">Min. Stake</span>
            <span class="text-white font-semibold">1 Gift</span>
          </div>

          <div class="flex items-center justify-between text-sm mb-4">
            <span class="text-gray-400">Your Stake</span>
            <span class="text-white font-semibold">0 Gifts</span>
          </div>

          <button class="w-full bg-yellow-600 hover:bg-yellow-700 text-white py-3 rounded-xl font-semibold">
            Stake Gifts
          </button>
        </div>
      </div>
    </div>

    <!-- Referral Program -->
    <div class="px-4 mb-6">
      <h2 class="text-xl font-bold text-white mb-4">Referral Program</h2>

      <div class="bg-gradient-to-br from-pink-900/40 to-purple-950/40 rounded-2xl p-5 border border-pink-500/30">
        <div class="flex items-center gap-4 mb-4">
          <div class="text-5xl">🎁</div>
          <div>
            <div class="text-white font-bold text-lg">Invite Friends</div>
            <div class="text-pink-300 text-sm">Earn 10% of their income</div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 mb-4">
          <div class="bg-black/20 rounded-xl p-3 text-center">
            <div class="text-2xl font-bold text-white">{{ referrals.count }}</div>
            <div class="text-xs text-gray-400">Referrals</div>
          </div>
          <div class="bg-black/20 rounded-xl p-3 text-center">
            <div class="text-2xl font-bold text-white">{{ referrals.earned.toFixed(2) }}</div>
            <div class="text-xs text-gray-400">TON Earned</div>
          </div>
        </div>

        <button class="w-full bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700 text-white py-3 rounded-xl font-semibold">
          Share Referral Link
        </button>
      </div>
    </div>

    <!-- Daily Tasks -->
    <div class="px-4">
      <h2 class="text-xl font-bold text-white mb-4">Daily Tasks</h2>

      <div class="space-y-2">
        <div
          v-for="task in dailyTasks"
          :key="task.id"
          class="bg-gray-800/50 rounded-xl p-4 flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <div class="text-2xl">{{ task.icon }}</div>
            <div>
              <div class="text-white font-semibold">{{ task.title }}</div>
              <div class="text-gray-400 text-xs">{{ task.reward }}</div>
            </div>
          </div>
          <button
            v-if="!task.completed"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold"
          >
            Claim
          </button>
          <div v-else class="text-green-400 text-xl">✓</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import { stakingGetStats, stakingGetUserStakes } from '../api/client'

const { user, initWebApp } = useTelegram()

const totalEarned = ref(0)
const dailyRate = ref(0)

const referrals = ref({
  count: 0,
  earned: 0,
})

const dailyTasks = ref([
  { id: 1, icon: '🎮', title: 'Play 3 games', reward: '0.01 TON', completed: false },
  { id: 2, icon: '💎', title: 'Stake 10 TON', reward: '0.05 TON', completed: false },
  { id: 3, icon: '👥', title: 'Invite 1 friend', reward: '0.1 TON', completed: false },
  { id: 4, icon: '🎁', title: 'Buy 1 gift', reward: '0.02 TON', completed: false },
])

onMounted(async () => {
  initWebApp()
  if (!user.value?.id) return

  try {
    const [statsData, stakes] = await Promise.all([
      stakingGetStats(user.value.id),
      stakingGetUserStakes(user.value.id, 'active'),
    ])

    totalEarned.value = parseFloat(statsData.total_rewards_earned_ton || '0')

    // Calculate daily rate from active stakes
    if (stakes.length > 0) {
      const totalDailyReward = stakes.reduce((sum: number, s: any) => {
        const reward = parseFloat(s.estimated_reward_ton || '0')
        const days = s.period_days || 30
        return sum + reward / days
      }, 0)
      dailyRate.value = parseFloat(totalDailyReward.toFixed(4))
    }

    // Check if stake task is completed
    if (stakes.length > 0) {
      const stakeTask = dailyTasks.value.find(t => t.id === 2)
      if (stakeTask) stakeTask.completed = true
    }
  } catch (e) {
    // Staking data not available
  }
})
</script>
