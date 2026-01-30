<template>
  <div class="stat-card bg-gray-800/50 rounded-xl p-4 border border-gray-700">
    <div class="flex items-center justify-between mb-2">
      <div class="text-2xl">{{ icon }}</div>
      <div
        class="text-xs font-semibold px-2 py-1 rounded-full"
        :class="colorClasses"
      >
        {{ color }}
      </div>
    </div>
    <div class="text-2xl font-bold text-white mb-1">{{ value }}</div>
    <div class="text-xs text-gray-400">{{ title }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: string | number
  icon: string
  color: 'blue' | 'green' | 'purple' | 'yellow' | 'red'
}

const props = defineProps<Props>()

const colorClasses = computed(() => {
  const classes = {
    blue: 'bg-blue-500/20 text-blue-300',
    green: 'bg-green-500/20 text-green-300',
    purple: 'bg-purple-500/20 text-purple-300',
    yellow: 'bg-yellow-500/20 text-yellow-300',
    red: 'bg-red-500/20 text-red-300',
  }
  return classes[props.color] || classes.blue
})
</script>
