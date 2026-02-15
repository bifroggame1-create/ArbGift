<template>
  <svg
    class="star-icon"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="12" cy="12" r="12" fill="#FFB800"/>
    <path
      d="M12 5.5L13.8 9.6L18.2 10L14.9 13L15.8 17.5L12 15.3L8.2 17.5L9.1 13L5.8 10L10.2 9.6L12 5.5Z"
      fill="white"
    />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 14 })
</script>

<style scoped>
.star-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
