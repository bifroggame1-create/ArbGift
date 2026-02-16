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
        <CurrencyIcon :currency="selectedCurrency" :size="16" />
        <span class="balance-amount">{{ formatBalance(balance) }}</span>
        <button class="plus-btn" @click="$emit('topUp')">+</button>
      </div>
      <div class="avatar" v-if="photoUrl">
        <img :src="photoUrl" alt="" />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTelegram } from '@/composables/useTelegram'
import CurrencyIcon from '@/components/CurrencyIcon.vue'
import { useCurrency } from '@/composables/useCurrency'

const { selectedCurrency } = useCurrency()

defineProps<{
  balance: number
}>()

defineEmits<{
  topUp: []
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

</style>
