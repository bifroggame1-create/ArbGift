<template>
  <span
    class="feature-badge inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold transition-all"
    :class="badgeClasses"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  color?: 'green' | 'blue' | 'red' | 'purple' | 'pink' | 'yellow' | 'amber' | 'cyan' | 'emerald'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'blue'
})

const badgeClasses = computed(() => {
  const colorClasses = {
    green: 'bg-green-500/20 text-green-300 border border-green-500/30',
    blue: 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
    red: 'bg-red-500/20 text-red-300 border border-red-500/30',
    purple: 'bg-purple-500/20 text-purple-300 border border-purple-500/30',
    pink: 'bg-pink-500/20 text-pink-300 border border-pink-500/30',
    yellow: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30',
    amber: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
    cyan: 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30',
    emerald: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
  }

  return colorClasses[props.color] || colorClasses.blue
})
</script>

<style scoped>
.feature-badge {
  backdrop-filter: blur(8px);
}
</style>
