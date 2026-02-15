<template>
  <TonIcon v-if="currency === 'ton'" :size="size" />
  <StarIcon v-else :size="size" />
</template>

<script setup lang="ts">
import TonIcon from './TonIcon.vue'
import StarIcon from './StarIcon.vue'
import type { Currency } from '../composables/useCurrency'

withDefaults(defineProps<{
  currency?: Currency
  size?: number
}>(), {
  currency: 'ton',
  size: 14,
})
</script>
