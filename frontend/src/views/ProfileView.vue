<template>
  <div class="profile-view min-h-screen bg-gray-950 pb-24">
    <!-- Header -->
    <div class="bg-gradient-to-b from-blue-900/30 to-gray-950 px-4 pt-6 pb-8">
      <div class="flex items-center space-x-4 mb-6">
        <div class="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-3xl">
          {{ userInitial }}
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white mb-1">{{ username }}</h1>
          <p class="text-sm text-gray-400">Telegram ID: {{ userId }}</p>
        </div>
      </div>

      <!-- Balance Card -->
      <div class="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-gray-400 text-xs mb-1">Total Balance</div>
            <div class="text-2xl font-bold text-white">{{ totalBalance.toFixed(2) }} TON</div>
          </div>
          <div class="text-4xl">💎</div>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="px-4 mt-6">
      <h2 class="text-lg font-semibold text-white mb-4">Statistics</h2>
      <div class="grid grid-cols-2 gap-3">
        <StatCard
          title="Total Gifts"
          :value="stats.totalGifts"
          icon="🎁"
          color="blue"
        />
        <StatCard
          title="On Sale"
          :value="stats.giftsOnSale"
          icon="💰"
          color="green"
        />
        <StatCard
          title="Games Played"
          :value="stats.gamesPlayed"
          icon="🎮"
          color="purple"
        />
        <StatCard
          title="Total Winnings"
          :value="`${stats.totalWinnings} TON`"
          icon="🏆"
          color="yellow"
        />
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="px-4 mt-8">
      <h2 class="text-lg font-semibold text-white mb-4">Recent Activity</h2>
      <div v-if="recentActivity.length > 0" class="space-y-3">
        <ActivityItem
          v-for="activity in recentActivity"
          :key="activity.id"
          :activity="activity"
        />
      </div>
      <div v-else class="text-center py-8 text-gray-400">
        No recent activity
      </div>
    </div>

    <!-- Settings -->
    <div class="px-4 mt-8">
      <h2 class="text-lg font-semibold text-white mb-4">Settings</h2>
      <div class="space-y-2">
        <SettingButton
          icon="🔔"
          label="Notifications"
          @click="openNotifications"
        />
        <SettingButton
          icon="🔐"
          label="Privacy"
          @click="openPrivacy"
        />
        <SettingButton
          icon="ℹ️"
          label="About"
          @click="openAbout"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import StatCard from '../components/StatCard.vue'
import ActivityItem from '../components/ActivityItem.vue'
import SettingButton from '../components/SettingButton.vue'

const { hapticImpact, user } = useTelegram()

// User info
const username = ref(user?.username || 'Anonymous')
const userId = ref(user?.id || '0')
const userInitial = ref((user?.username || 'A')[0].toUpperCase())
const totalBalance = ref(0)

// Stats
const stats = ref({
  totalGifts: 0,
  giftsOnSale: 0,
  gamesPlayed: 0,
  totalWinnings: 0,
})

// Recent activity
const recentActivity = ref<any[]>([])

const openNotifications = () => {
  hapticImpact('light')
  // TODO: Navigate to notifications settings
}

const openPrivacy = () => {
  hapticImpact('light')
  // TODO: Navigate to privacy settings
}

const openAbout = () => {
  hapticImpact('light')
  // TODO: Navigate to about page
}

onMounted(async () => {
  // Load user profile data
  // TODO: Replace with actual API calls
})
</script>
