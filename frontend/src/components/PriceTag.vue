<template>
  <div class="flex items-center space-x-1">
    <span class="text-blue-400 text-lg">💎</span>
    <span class="font-bold text-white">{{ formattedPrice }}</span>
    <span class="text-xs text-gray-400">TON</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  price: string | number
}>()

const formattedPrice = computed(() => {
  const num = typeof props.price === 'string' ? parseFloat(props.price) : props.price
  return num.toFixed(2)
})
</script>
