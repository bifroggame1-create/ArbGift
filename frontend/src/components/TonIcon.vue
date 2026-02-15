<template>
  <img src="/images/ton_symbol.svg" alt="TON" class="ton-icon" :style="{ width: size + 'px', height: size + 'px' }" />
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 14 })
</script>

<style scoped>
.ton-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
