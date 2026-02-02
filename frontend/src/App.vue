<template>
  <div id="app" class="min-h-screen bg-gray-950 text-white">
    <!-- Hide top nav on game/detail pages that have their own headers -->
    <Navigation v-if="showTopNav" />

    <main class="pb-20">
      <router-view v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>

    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useTelegram } from './composables/useTelegram'
import Navigation from './components/Navigation.vue'
import BottomNavigation from './components/BottomNavigation.vue'

const route = useRoute()
const { initWebApp, setHeaderColor, ready } = useTelegram()

// Hide top nav on pages with their own headers
const showTopNav = computed(() => {
  const hiddenPaths = [
    '/plinko', '/lucky', '/rocket', '/trading', '/escape',
    '/aviator', '/roulette', '/pvp', '/topup', '/contracts',
    '/upgrade', '/stars', '/gift/'
  ]
  return !hiddenPaths.some(p => route.path.startsWith(p))
})

onMounted(() => {
  // Initialize Telegram Web App
  initWebApp()
  setHeaderColor('#030712') // bg-gray-950
  ready()
})
</script>

<style>
/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #1f2937;
}

::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>
