<template>
  <div class="win-feed" v-if="history.length > 0">
    <TransitionGroup name="feed-item" tag="div" class="feed-list">
      <div
        v-for="(item, i) in visibleHistory"
        :key="i"
        :class="['feed-badge', badgeClass(item.multiplier)]"
      >
        {{ item.multiplier.toFixed(1) }}x
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PlinkoHistoryItem } from '@/composables/usePlinko'

const props = defineProps<{
  history: PlinkoHistoryItem[]
}>()

const visibleHistory = computed(() => props.history.slice(0, 15))

function badgeClass(mult: number): string {
  if (mult >= 10) return 'extreme'
  if (mult >= 3) return 'high'
  if (mult >= 1) return 'win'
  return 'loss'
}
</script>

<style scoped>
.win-feed {
  position: absolute;
  right: 4px;
  top: 40px;
  bottom: 40px;
  width: 52px;
  overflow: hidden;
  pointer-events: none;
  z-index: 5;
}

.feed-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
}

.feed-badge {
  padding: 3px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  font-family: 'CoFo Sans Mono', monospace;
  white-space: nowrap;
}

.feed-badge.extreme {
  background: rgba(226, 53, 53, 0.3);
  color: #E23535;
}
.feed-badge.high {
  background: rgba(255, 197, 2, 0.25);
  color: #FFC502;
}
.feed-badge.win {
  background: rgba(0, 255, 98, 0.15);
  color: #00FF62;
}
.feed-badge.loss {
  background: rgba(128, 128, 128, 0.15);
  color: #808080;
}

/* Transition */
.feed-item-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.feed-item-leave-active { transition: all 0.2s ease; }
.feed-item-enter-from { opacity: 0; transform: translateX(20px) scale(0.8); }
.feed-item-leave-to { opacity: 0; transform: scale(0.7); }
.feed-item-move { transition: transform 0.3s ease; }
</style>
