<template>
  <button
    class="setting-button w-full bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 flex items-center justify-between transition-all hover:bg-gray-800/50 active:scale-[0.98]"
    @click="$emit('click')"
  >
    <div class="flex items-center space-x-3">
      <div class="text-2xl">{{ icon }}</div>
      <span class="text-sm font-medium text-white">{{ label }}</span>
    </div>
    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
    </svg>
  </button>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  label: string
}

defineProps<Props>()
defineEmits(['click'])
</script>
