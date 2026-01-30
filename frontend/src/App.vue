<template>
  <div id="app" class="min-h-screen bg-gray-950 text-white">
    <Navigation />

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
import { onMounted } from 'vue'
import { useTelegram } from './composables/useTelegram'
import Navigation from './components/Navigation.vue'
import BottomNavigation from './components/BottomNavigation.vue'

const { initWebApp, setHeaderColor, ready } = useTelegram()

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
