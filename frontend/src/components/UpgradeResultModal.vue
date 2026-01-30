<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content" :class="result.won ? 'win' : 'loss'">
      <!-- Confetti for wins -->
      <div v-if="result.won" class="confetti-container">
        <div v-for="i in 50" :key="i" class="confetti" :style="confettiStyle(i)"></div>
      </div>

      <!-- Result Icon -->
      <div class="result-icon">
        <span v-if="result.won" class="icon-win">🎊</span>
        <span v-else class="icon-loss">💔</span>
      </div>

      <!-- Result Title -->
      <h2 class="result-title">
        {{ result.won ? 'Upgrade Successful!' : 'Upgrade Failed' }}
      </h2>

      <!-- Gifts Display -->
      <div class="gifts-display">
        <!-- Input Gift -->
        <div class="gift-slot">
          <div class="slot-label">Lost</div>
          <TelegramGiftCard :gift="result.input_gift" />
        </div>

        <!-- Arrow -->
        <div class="arrow" :class="{ failed: !result.won }">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>

        <!-- Target Gift -->
        <div class="gift-slot" :class="{ 'grayed-out': !result.won }">
          <div class="slot-label">{{ result.won ? 'Won!' : 'Target' }}</div>
          <TelegramGiftCard :gift="result.target_gift" />
          <div v-if="!result.won" class="overlay-x">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Result Details -->
      <div class="result-details">
        <div class="detail-row">
          <span class="detail-label">Probability</span>
          <span class="detail-value">{{ (result.probability * 100).toFixed(1) }}%</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Result Angle</span>
          <span class="detail-value">{{ result.result_angle.toFixed(1) }}°</span>
        </div>

        <div class="detail-row highlight" :class="result.won ? 'win' : 'loss'">
          <span class="detail-label">Outcome</span>
          <span class="detail-value">{{ result.won ? 'SUCCESS' : 'FAILED' }}</span>
        </div>
      </div>

      <!-- Provably Fair -->
      <div class="provably-fair">
        <div class="fair-header">
          <span class="fair-icon">🔐</span>
          <span class="fair-title">Provably Fair</span>
        </div>
        <button class="verify-button">
          Verify Result
        </button>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button
          class="action-button primary"
          @click="emit('close')"
        >
          {{ result.won ? 'Claim Reward 🎁' : 'Try Again ⚡' }}
        </button>

        <button
          class="action-button secondary"
          @click="emit('close')"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import TelegramGiftCard from './TelegramGiftCard.vue'

interface UpgradeResult {
  won: boolean
  input_gift: any
  target_gift: any
  probability: number
  result_angle: number
}

interface Props {
  result: UpgradeResult
}

defineProps<Props>()
const emit = defineEmits(['close'])

const confettiStyle = (index: number) => {
  const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#a855f7']
  return {
    left: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 3}s`,
    backgroundColor: colors[index % colors.length],
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
  border-radius: 24px;
  padding: 32px 24px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  animation: slide-up 0.3s ease;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content.win {
  border: 2px solid #10b981;
}

.modal-content.loss {
  border: 2px solid #ef4444;
}

.confetti-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  border-radius: 24px;
}

.confetti {
  position: absolute;
  width: 10px;
  height: 10px;
  top: -10px;
  animation: confetti-fall 3s linear infinite;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

.result-icon {
  text-align: center;
  margin-bottom: 20px;
}

.icon-win,
.icon-loss {
  font-size: 80px;
  display: inline-block;
  animation: icon-pop 0.5s ease;
}

@keyframes icon-pop {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.result-title {
  text-align: center;
  font-size: 28px;
  font-weight: 800;
  color: white;
  margin-bottom: 24px;
}

.gifts-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 24px;
}

.gift-slot {
  flex: 1;
  position: relative;
}

.gift-slot.grayed-out {
  opacity: 0.4;
}

.slot-label {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.arrow {
  flex-shrink: 0;
  color: #10b981;
  margin-top: 24px;
}

.arrow.failed {
  color: #ef4444;
}

.overlay-x {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ef4444;
  opacity: 0.8;
}

.result-details {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 24px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row.highlight {
  margin-top: 8px;
  padding: 16px;
  border-radius: 12px;
  border-bottom: none;
}

.detail-row.highlight.win {
  background: rgba(16, 185, 129, 0.2);
}

.detail-row.highlight.loss {
  background: rgba(239, 68, 68, 0.2);
}

.detail-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.detail-value {
  font-size: 16px;
  font-weight: 700;
  color: white;
}

.provably-fair {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.fair-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.fair-icon {
  font-size: 20px;
}

.fair-title {
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.verify-button {
  width: 100%;
  padding: 8px;
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.4);
  border-radius: 8px;
  color: #a855f7;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.verify-button:hover {
  background: rgba(168, 85, 247, 0.3);
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-button {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.action-button.primary {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
}

.action-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(168, 85, 247, 0.3);
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>
