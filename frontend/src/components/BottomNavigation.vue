<template>
  <nav class="bottom-nav">
    <router-link to="/pvp" class="nav-item" :class="{ active: isActive('/pvp') }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M4 4l4 4m8 8l4 4M4 20l4-4m8-8l4-4"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
      <span>ПвП</span>
    </router-link>

    <router-link to="/solo" class="nav-item" :class="{ active: isActive('/solo') || isGameRoute() }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v6l4 2"/>
      </svg>
      <span>Соло</span>
    </router-link>

    <router-link to="/inventory" class="nav-item" :class="{ active: isActive('/inventory') }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <path d="M3 9h18M9 21V9"/>
      </svg>
      <span>Инвентарь</span>
    </router-link>

    <router-link to="/shop" class="nav-item" :class="{ active: isActive('/shop') || isActive('/market') }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>
        <line x1="3" y1="6" x2="21" y2="6"/>
        <path d="M16 10a4 4 0 01-8 0"/>
      </svg>
      <span>Магазин</span>
    </router-link>

    <router-link to="/profile" class="nav-item" :class="{ active: isActive('/profile') }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
      <span>Профиль</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const isGameRoute = () => {
  const gameRoutes = ['/plinko', '/lucky', '/rocket', '/trading', '/escape', '/aviator', '/roulette']
  return gameRoutes.some(gamePath => route.path.startsWith(gamePath))
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #000;
  border-top: 1px solid #1c1c1e;
  display: flex;
  padding: 8px 0 24px;
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  text-decoration: none;
  font-size: 10px;
  transition: color 0.2s;
}

.nav-item svg {
  width: 22px;
  height: 22px;
}

.nav-item.active {
  color: #fff;
}

.nav-item:active {
  transform: scale(0.95);
}
</style>
