<template>
  <div class="max-w-7xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Favorites</h1>

    <!-- Coming Soon -->
    <div class="text-center py-16">
      <div class="text-6xl mb-4">❤️</div>
      <h3 class="text-xl font-semibold mb-2">Coming Soon</h3>
      <p class="text-gray-400 mb-6">
        Save your favorite gifts and get notified when prices drop
      </p>
      <router-link
        to="/"
        class="inline-block px-6 py-3 bg-blue-600 rounded-lg font-medium hover:bg-blue-700 transition-colors"
      >
        Browse Gifts
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// Placeholder for favorites functionality
// Will implement localStorage/backend persistence later
</script>
