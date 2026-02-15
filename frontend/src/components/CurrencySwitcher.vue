<template>
  <div class="currency-switcher">
    <!-- Currency Toggle -->
    <button class="switcher-btn" @click="toggle">
      <CurrencyIcon :currency="nextCurrency" :size="14" />
      <span class="switcher-label">{{ nextCurrency === 'stars' ? 'Stars' : 'TON' }}</span>
    </button>

    <!-- Balance Display -->
    <div class="switcher-balance">
      <CurrencyIcon :currency="selectedCurrency" :size="16" />
      <span class="balance-amount">{{ formattedBalance }}</span>
      <button class="balance-plus" @click="$emit('topUp')">+</button>
    </div>

    <!-- Gift Bet (right side) -->
    <button class="gift-bet-btn" @click="$emit('giftBet')">
      <span class="gift-emoji">🎁</span>
      <span class="gift-label">Gift</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CurrencyIcon from './CurrencyIcon.vue'
import { useCurrency, type Currency } from '../composables/useCurrency'

const { selectedCurrency, currentBalance, toggleCurrency, formatAmount } = useCurrency()

defineEmits<{
  topUp: []
  giftBet: []
}>()

const nextCurrency = computed<Currency>(() => {
  return selectedCurrency.value === 'ton' ? 'stars' : 'ton'
})

const formattedBalance = computed(() => formatAmount(currentBalance.value))

const toggle = () => {
  toggleCurrency()
}
</script>

<style scoped>
.currency-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #1a1a1a;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.switcher-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 8px 12px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.switcher-btn:active {
  transform: scale(0.96);
  background: rgba(255, 255, 255, 0.12);
}

.switcher-label {
  font-size: 12px;
}

.switcher-balance {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 8px 12px;
}

.balance-amount {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.balance-plus {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: #fff;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.balance-plus:active {
  background: rgba(255, 255, 255, 0.1);
}

.gift-bet-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 8px 12px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.gift-bet-btn:active {
  transform: scale(0.96);
  background: rgba(255, 255, 255, 0.12);
}

.gift-emoji {
  font-size: 14px;
}

.gift-label {
  font-size: 12px;
}
</style>
