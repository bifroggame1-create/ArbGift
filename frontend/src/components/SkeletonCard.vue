<template>
  <div class="skeleton-card">
    <!-- Fake image area (square) -->
    <div class="skeleton-card__image skeleton" />

    <!-- Fake info section -->
    <div class="skeleton-card__body">
      <!-- Fake title bar -->
      <div class="skeleton-card__title skeleton" />
      <!-- Fake serial line -->
      <div class="skeleton-card__serial skeleton" />
      <!-- Fake price pill -->
      <div class="skeleton-card__price skeleton" />
    </div>
  </div>
</template>

<script setup lang="ts">
// No props needed -- pure visual placeholder
</script>

<style scoped>
.skeleton-card {
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

/* Square image placeholder */
.skeleton-card__image {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 0;
}

/* Info section below image */
.skeleton-card__body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
}

/* Title bar */
.skeleton-card__title {
  height: 14px;
  width: 70%;
  border-radius: 6px;
}

/* Serial number line */
.skeleton-card__serial {
  height: 10px;
  width: 35%;
  border-radius: 4px;
}

/* Price pill */
.skeleton-card__price {
  height: 32px;
  width: 100%;
  border-radius: 8px;
  margin-top: 4px;
}
</style>
