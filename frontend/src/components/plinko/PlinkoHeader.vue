<template>
  <header class="plinko-header">
    <div class="header-left">
      <button class="back-btn" @click="$router.push('/solo')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="title">PLINKO</h1>
    </div>

    <div class="header-right">
      <div class="plinko-balance-pill">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="12" fill="#FFB800"/>
          <path d="M12 5l2.5 5 5.5.8-4 3.8 1 5.4-5-2.6-5 2.6 1-5.4-4-3.8 5.5-.8z" fill="white"/>
        </svg>
        <span class="balance-amount">{{ formatBalance(balance) }}</span>
        <button class="plus-btn" @click="$emit('topUp')">+</button>
      </div>
      <div class="avatar" v-if="photoUrl">
        <img :src="photoUrl" alt="" />
      </div>
    </div>
  </header>

  <div class="demo-toggle-row">
    <label class="demo-toggle" @click="$emit('toggleDemo')">
      <span class="toggle-track" :class="{ active: isDemo }">
        <span class="toggle-thumb" />
      </span>
      <span class="toggle-label">DEMO</span>
    </label>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTelegram } from '@/composables/useTelegram'

defineProps<{
  balance: number
  isDemo: boolean
}>()

defineEmits<{
  topUp: []
  toggleDemo: []
}>()

const { user } = useTelegram()
const photoUrl = computed(() => user.value?.photo_url || '')

function formatBalance(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toFixed(0)
}
</script>

<style scoped>
.plinko-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px 8px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--plinko-white);
  padding: 4px;
  cursor: pointer;
  opacity: 0.7;
}

.title {
  font-family: 'Chroma ST', 'SF Pro Display', sans-serif;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 1px;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.balance-amount {
  font-family: 'CoFo Sans Mono', 'SF Mono', monospace;
  font-size: 14px;
  font-weight: 600;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--plinko-purple);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.demo-toggle-row {
  padding: 0 16px 8px;
}

.demo-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.toggle-track {
  width: 36px;
  height: 20px;
  border-radius: 10px;
  background: var(--plinko-purple);
  position: relative;
  transition: background 0.2s;
}

.toggle-track.active {
  background: var(--plinko-blue);
}

.toggle-thumb {
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--plinko-white);
  top: 2px;
  left: 2px;
  transition: transform 0.2s var(--plinko-ease, ease);
}

.toggle-track.active .toggle-thumb {
  transform: translateX(16px);
}

.toggle-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--plinko-text-secondary);
}
</style>
