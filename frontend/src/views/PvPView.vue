<template>
  <div class="pvp-view min-h-screen bg-[#0a0e27] pb-24 flex items-center justify-center">
    <div class="text-center px-4">
      <div class="text-8xl mb-6">⚔️</div>
      <h1 class="text-3xl font-bold text-white mb-4">PvP Mode</h1>
      <p class="text-gray-400 mb-8">Multiplayer battles coming soon!</p>
      <button
        @click="router.back()"
        class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold"
      >
        Go Back
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>
