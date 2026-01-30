<template>
  <div class="flex items-center justify-center" :class="containerClass">
    <div
      class="animate-spin rounded-full border-4 border-gray-700 border-t-blue-500"
      :class="sizeClass"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: 'sm' | 'md' | 'lg'
    fullHeight?: boolean
  }>(),
  {
    size: 'md',
    fullHeight: false,
  }
)

const sizeClass = computed(() => {
  return {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  }[props.size]
})

const containerClass = computed(() => {
  return props.fullHeight ? 'min-h-[60vh]' : 'py-8'
})
</script>
