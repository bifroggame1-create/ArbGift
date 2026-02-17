<template>
  <div id="app" :class="['app-body', { 'mobile-body': isMobilePlatform }]">
    <div :class="['app-wrap', { 'mobile-wrap': isMobilePlatform }]">
      <div :class="['app-content', { 'mobile-content': isMobilePlatform }]" :style="{ paddingBottom: navPadding }">
        <router-view v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </div>
    </div>

    <BottomNavigation />
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useTelegram } from './composables/useTelegram'
import BottomNavigation from './components/BottomNavigation.vue'
import ToastContainer from './components/ToastContainer.vue'

const route = useRoute()
const { initWebApp, setHeaderColor, ready } = useTelegram()

// Detect mobile platforms that need special scrolling structure
const isMobilePlatform = computed(() => {
  const tg = window.Telegram?.WebApp
  if (!tg) return false

  const platform = tg.platform || ''
  // Desktop platforms don't need the mobile wrapper structure
  const desktopPlatforms = ['macos', 'tdesktop', 'weba', 'web', 'webk']
  return !desktopPlatforms.includes(platform)
})

// Hide bottom nav on full-screen game pages
const hideNav = computed(() => {
  const fullScreenPaths = ['/plinko', '/trading', '/escape', '/gonka', '/pvp/ice', '/pvp/race']
  return fullScreenPaths.some(p => route.path.startsWith(p))
})

// Account for bottom nav (56px) + safe area inset
const navPadding = computed(() => hideNav.value ? '0px' : '80px')

onMounted(() => {
  initWebApp()
  setHeaderColor('#0C0C0C')

  const tg = window.Telegram?.WebApp
  if (tg) {
    try { tg.setBackgroundColor('#0C0C0C') } catch {}
    try { tg.expand() } catch {}
  }

  // Prevent overscroll/bounce effect on iOS
  document.body.style.overscrollBehavior = 'none'
  document.documentElement.style.overscrollBehavior = 'none'

  ready()
})
</script>

<style>
/* Base app container */
.app-body {
  max-width: 440px;
  margin: 0 auto;
  background-color: var(--mb-bg, #0C0C0C);
  color: #fff;
}

/* Mobile platform: prevent swipe-down closure */
.mobile-body {
  overflow: hidden;
  height: 100vh;
  height: 100dvh;
}

/* Mobile platform: scrollable wrapper */
.mobile-wrap {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Mobile platform: content slightly taller than viewport */
.mobile-content {
  min-height: calc(100% + 1px);
}

/* Desktop platform: natural flow */
.app-content {
  position: relative;
  padding-top: env(safe-area-inset-top, 20px);
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
