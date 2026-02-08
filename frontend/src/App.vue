<template>
  <div id="app" class="app-container">
    <main class="app-content" :style="{ paddingBottom: navPadding }">
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
import BottomNavigation from './components/BottomNavigation.vue'

const route = useRoute()
const { initWebApp, setHeaderColor, ready } = useTelegram()

// Hide bottom nav on full-screen game pages
const hideNav = computed(() => {
  const fullScreenPaths = ['/plinko', '/trading', '/escape', '/gonka', '/pvp/ice', '/pvp/race']
  return fullScreenPaths.some(p => route.path.startsWith(p))
})

const navPadding = computed(() => hideNav.value ? '0px' : '76px')

onMounted(() => {
  initWebApp()
  setHeaderColor('#0C0C0C')

  // Also set background color
  const tg = window.Telegram?.WebApp
  if (tg) {
    try { tg.setBackgroundColor('#0C0C0C') } catch {}
  }

  ready()
})
</script>

<style>
.app-container {
  max-width: 440px;
  margin: 0 auto;
  min-height: 100vh;
  min-height: 100dvh;
  background-color: var(--mb-bg, #0C0C0C);
  color: #fff;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
}

.app-content {
  min-height: 100vh;
  min-height: 100dvh;
}
</style>
