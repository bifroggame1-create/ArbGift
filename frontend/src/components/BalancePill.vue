<template>
  <div class="balance-pill">
    <!-- TON diamond icon -->
    <svg
      class="balance-pill__icon"
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
    >
      <path
        d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z"
        fill="currentColor"
      />
    </svg>

    <!-- Balance number -->
    <span class="balance-pill__amount">{{ displayBalance }}</span>

    <!-- Plus button -->
    <button class="balance-pill__add" @click.stop="$emit('add')">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path
          d="M7 1v12M1 7h12"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  balance: number
}>()

defineEmits<{
  add: []
}>()

const displayBalance = computed(() => {
  const b = props.balance
  if (b >= 1000) {
    return b.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
  }
  // Remove trailing zeros but keep up to 2 decimals
  return Number(b.toFixed(2)).toString()
})
</script>

<style scoped>
.balance-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 4px 0 10px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  user-select: none;
  flex-shrink: 0;
}

.balance-pill__icon {
  flex-shrink: 0;
  color: var(--mb-primary, #34CDEF);
}

.balance-pill__amount {
  font-family: var(--mb-font-mono, 'CoFo Sans Mono', 'SF Mono', monospace);
  font-size: 14px;
  font-weight: 500;
  line-height: 1;
  color: #fff;
  white-space: nowrap;
}

.balance-pill__add {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  border: none;
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
  padding: 0;
  transition: background 0.16s ease;
  -webkit-tap-highlight-color: transparent;
}

.balance-pill__add:active {
  background: rgba(255, 255, 255, 0.2);
}
</style>
