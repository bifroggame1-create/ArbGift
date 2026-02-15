<template>
  <button
    class="risk-button"
    :class="[risk.level, { active: selected, disabled: disabled }]"
    :disabled="disabled"
    @click="handleClick"
  >
    <!-- Icon -->
    <div class="risk-icon">{{ risk.icon }}</div>

    <!-- Info -->
    <div class="risk-info">
      <div class="risk-name">{{ risk.name }}</div>
      <div class="risk-multiplier">x{{ risk.multiplier }}</div>
      <div class="risk-chance">{{ (risk.probability * 100).toFixed(1) }}% chance</div>
      <div class="risk-min">Min: {{ risk.minValue }} <img src="/images/ton_symbol.svg" width="10" height="10" style="display:inline-block;vertical-align:middle" /></div>
    </div>

    <!-- Checkmark when selected -->
    <div v-if="selected" class="risk-checkmark">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
      </svg>
    </div>

    <!-- Flame animation for Risky mode when active -->
    <div v-if="risk.level === 'risky' && selected" class="flame-effect">
      <span class="flame">🔥</span>
      <span class="flame">🔥</span>
      <span class="flame">🔥</span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { useTelegram } from '../composables/useTelegram'

interface Risk {
  level: string
  name: string
  icon: string
  multiplier: number
  probability: number
  minValue: number
  color: string
}

interface Props {
  risk: Risk
  selected: boolean
  disabled: boolean
}

defineProps<Props>()
const emit = defineEmits(['click'])

const { hapticImpact } = useTelegram()

const handleClick = () => {
  hapticImpact('medium')
  emit('click')
}
</script>

<style scoped>
.risk-button {
  position: relative;
  padding: 20px;
  border-radius: 16px;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

/* Safe Mode */
.risk-button.safe {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.risk-button.safe:hover:not(.disabled) {
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.risk-button.safe.active {
  border-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
}

/* Normal Mode */
.risk-button.normal {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.risk-button.normal:hover:not(.disabled) {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

.risk-button.normal.active {
  border-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
}

/* Risky Mode */
.risk-button.risky {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.risk-button.risky:hover:not(.disabled) {
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.3);
}

.risk-button.risky.active {
  border-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.4);
  animation: flame-pulse 2s ease-in-out infinite;
}

@keyframes flame-pulse {
  0%, 100% {
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.5), 0 0 40px rgba(239, 68, 68, 0.3);
  }
  50% {
    box-shadow: 0 0 40px rgba(239, 68, 68, 0.8), 0 0 60px rgba(239, 68, 68, 0.5);
  }
}

.risk-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.3);
}

.risk-button.active {
  transform: scale(1.02);
}

.risk-button:active:not(.disabled) {
  transform: scale(0.98);
}

.risk-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.risk-info {
  flex: 1;
  text-align: left;
}

.risk-name {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.risk-multiplier {
  font-size: 28px;
  font-weight: 800;
  color: #fbbf24;
  line-height: 1;
  margin-bottom: 4px;
}

.risk-chance {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.risk-min {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2px;
}

.risk-checkmark {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  color: #10b981;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  animation: scale-in 0.2s ease;
}

@keyframes scale-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.flame-effect {
  position: absolute;
  top: -10px;
  right: -10px;
  display: flex;
  gap: 8px;
  pointer-events: none;
}

.flame {
  font-size: 24px;
  animation: flame-flicker 1s ease-in-out infinite;
}

.flame:nth-child(2) {
  animation-delay: 0.2s;
}

.flame:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes flame-flicker {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  25% {
    transform: scale(1.1) rotate(5deg);
    opacity: 0.9;
  }
  50% {
    transform: scale(0.9) rotate(-5deg);
    opacity: 1;
  }
  75% {
    transform: scale(1.05) rotate(3deg);
    opacity: 0.95;
  }
}
</style>
