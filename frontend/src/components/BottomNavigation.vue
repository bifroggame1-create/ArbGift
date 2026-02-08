<template>
  <nav class="bottom-nav">
    <div class="bottom-nav-fade" />
    <div class="bottom-nav-items">
      <router-link
        v-for="tab in tabs"
        :key="tab.path"
        :to="tab.path"
        class="nav-item base-active-btn"
        :class="{ active: isActive(tab.matchPaths) }"
      >
        <component :is="tab.icon" />
        <span class="nav-label">{{ tab.label }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { markRaw } from 'vue'
import IconMarket from './icons/IconMarket.vue'
import IconPvP from './icons/IconPvP.vue'
import IconSolo from './icons/IconSolo.vue'
import IconEarn from './icons/IconEarn.vue'
import IconProfile from './icons/IconProfile.vue'

const route = useRoute()

const tabs = [
  {
    path: '/market',
    label: 'Market',
    icon: markRaw(IconMarket),
    matchPaths: ['/market', '/gift'],
  },
  {
    path: '/pvp',
    label: 'PvP',
    icon: markRaw(IconPvP),
    matchPaths: ['/pvp'],
  },
  {
    path: '/solo',
    label: 'Solo',
    icon: markRaw(IconSolo),
    matchPaths: ['/solo', '/trading', '/plinko', '/gonka', '/escape', '/ball-escape'],
  },
  {
    path: '/earn',
    label: 'Earn',
    icon: markRaw(IconEarn),
    matchPaths: ['/earn', '/farming', '/staking'],
  },
  {
    path: '/profile',
    label: 'Profile',
    icon: markRaw(IconProfile),
    matchPaths: ['/profile', '/inventory'],
  },
]

const isActive = (matchPaths: string[]) => {
  return matchPaths.some(p => route.path === p || route.path.startsWith(p + '/') || route.path.startsWith(p))
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 440px;
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

.bottom-nav-fade {
  position: absolute;
  inset: 0;
  top: -20px;
  background: var(--mb-gradient-nav);
  pointer-events: none;
}

.bottom-nav-items {
  position: relative;
  display: flex;
  height: 56px;
  align-items: center;
  background: var(--mb-bg, #0C0C0C);
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--mb-text-inactive, #808080);
  text-decoration: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.nav-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-label {
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
}

.nav-item.active {
  color: #FFFFFF;
}
</style>
