<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content" :class="result.won ? 'win' : 'loss'">
      <!-- Confetti Effect for Wins -->
      <div v-if="result.won" class="confetti-container">
        <div v-for="i in 50" :key="i" class="confetti" :style="confettiStyle(i)"></div>
      </div>

      <!-- Result Icon -->
      <div class="result-icon">
        <span v-if="result.won" class="icon-win">🎉</span>
        <span v-else class="icon-loss">😢</span>
      </div>

      <!-- Result Title -->
      <h2 class="result-title">
        {{ result.won ? 'Congratulations!' : 'Better Luck Next Time' }}
      </h2>

      <!-- Result Details -->
      <div class="result-details">
        <div class="detail-row">
          <span class="detail-label">Risk Level</span>
          <span class="detail-value risk-badge" :class="result.risk_level">
            {{ result.risk_level }}
          </span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Multiplier</span>
          <span class="detail-value">x{{ result.multiplier }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Input Value</span>
          <span class="detail-value"><img src="/images/ton_symbol.svg" width="12" height="12" style="display:inline-block;vertical-align:middle;margin-right:2px" />{{ result.input_value.toFixed(2) }}</span>
        </div>

        <div class="detail-row highlight" :class="result.won ? 'win' : 'loss'">
          <span class="detail-label">{{ result.won ? 'You Won' : 'You Lost' }}</span>
          <span class="detail-value payout">
            {{ result.won ? '+' : '-' }}{{ result.input_value.toFixed(2) }} <img src="/images/ton_symbol.svg" width="12" height="12" style="display:inline-block;vertical-align:middle;margin-left:2px" />
          </span>
        </div>

        <div v-if="result.won" class="detail-row highlight win">
          <span class="detail-label">Total Payout</span>
          <span class="detail-value payout">
            {{ result.payout_value.toFixed(2) }} <img src="/images/ton_symbol.svg" width="14" height="14" style="display:inline-block;vertical-align:middle;margin-left:2px" />
          </span>
        </div>
      </div>

      <!-- Reward Gift (if won) -->
      <div v-if="result.won && result.reward_gift" class="reward-section">
        <h3 class="reward-title">Your Reward</h3>
        <TelegramGiftCard :gift="result.reward_gift" />
      </div>

      <!-- Provably Fair Info -->
      <div class="provably-fair">
        <div class="fair-header">
          <span class="fair-icon">🔐</span>
          <span class="fair-title">Provably Fair</span>
        </div>
        <div class="fair-details">
          <div class="fair-row">
            <span class="fair-label">Server Seed</span>
            <span class="fair-value mono">{{ result.server_seed || 'Loading...' }}</span>
          </div>
          <button class="verify-button" @click="verifyResult">
            Verify Result
          </button>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button
          v-if="result.won"
          class="action-button primary"
          @click="playAgain"
        >
          Play Again 🎮
        </button>
        <button
          v-else
          class="action-button primary"
          @click="tryAgain"
        >
          Try Again 🔥
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
import { useTelegram } from '../composables/useTelegram'
import TelegramGiftCard from './TelegramGiftCard.vue'

interface ContractResult {
  won: boolean
  multiplier: number
  input_value: number
  payout_value: number
  risk_level: string
  reward_gift?: any
  server_seed?: string
}

interface Props {
  result: ContractResult
}

defineProps<Props>()
const emit = defineEmits(['close', 'playAgain'])

const { hapticImpact } = useTelegram()

const confettiStyle = (index: number) => {
  const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#a855f7']
  return {
    left: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 3}s`,
    backgroundColor: colors[index % colors.length],
  }
}

const verifyResult = () => {
  hapticImpact('light')
  // TODO: Open verification modal or navigate to verification page
  console.log('Verify result')
}

const playAgain = () => {
  hapticImpact('medium')
  emit('close')
}

const tryAgain = () => {
  hapticImpact('medium')
  emit('close')
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
  max-width: 480px;
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
  font-weight: 600;
  color: white;
}

.detail-value.payout {
  font-size: 20px;
  font-weight: 800;
}

.risk-badge {
  text-transform: capitalize;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
}

.risk-badge.safe {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.risk-badge.normal {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.risk-badge.risky {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.reward-section {
  margin-bottom: 24px;
}

.reward-title {
  font-size: 18px;
  font-weight: 700;
  color: white;
  margin-bottom: 16px;
  text-align: center;
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

.fair-details {
  font-size: 12px;
}

.fair-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.fair-label {
  color: rgba(255, 255, 255, 0.6);
}

.fair-value {
  color: #3b82f6;
  font-family: monospace;
  font-size: 10px;
  max-width: 60%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.verify-button {
  width: 100%;
  padding: 8px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 8px;
  color: #3b82f6;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.verify-button:hover {
  background: rgba(59, 130, 246, 0.3);
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
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.action-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
}

.action-button.primary:active {
  transform: translateY(0);
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>
