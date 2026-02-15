<template>
  <div class="flex items-center space-x-1">
    <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 56 56" fill="none">
      <circle cx="28" cy="28" r="28" fill="#0098EA"/>
      <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
    </svg>
    <span class="font-bold text-white">{{ formattedPrice }}</span>
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
