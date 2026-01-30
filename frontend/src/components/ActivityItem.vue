<template>
  <div class="activity-item bg-gray-800/30 rounded-lg p-3 border border-gray-700/50">
    <div class="flex items-start justify-between">
      <div class="flex items-start space-x-3">
        <div class="text-2xl mt-0.5">{{ activity.icon }}</div>
        <div>
          <div class="text-sm font-medium text-white">{{ activity.title }}</div>
          <div class="text-xs text-gray-400 mt-0.5">{{ activity.description }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ formatTime(activity.timestamp) }}</div>
        </div>
      </div>
      <div
        v-if="activity.amount"
        class="text-sm font-semibold"
        :class="activity.amount > 0 ? 'text-green-400' : 'text-red-400'"
      >
        {{ activity.amount > 0 ? '+' : '' }}{{ activity.amount }} TON
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Activity {
  id: string
  icon: string
  title: string
  description: string
  timestamp: number
  amount?: number
}

interface Props {
  activity: Activity
}

defineProps<Props>()

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))

  if (hours < 1) {
    const minutes = Math.floor(diff / (1000 * 60))
    return `${minutes}m ago`
  } else if (hours < 24) {
    return `${hours}h ago`
  } else {
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }
}
</script>
