<template>
  <div class="plinko-controls">
    <!-- Bet amount + Ball count row -->
    <div class="controls-row">
      <div class="control-group">
        <label class="control-label">СУММА СТАВКИ</label>
        <div class="input-with-icon">
          <svg class="star-icon" width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="#FFB800"/>
            <path d="M12 5l2.5 5 5.5.8-4 3.8 1 5.4-5-2.6-5 2.6 1-5.4-4-3.8 5.5-.8z" fill="white"/>
          </svg>
          <input
            type="number"
            class="bet-input"
            :value="bet"
            @input="onBetInput"
            :disabled="isPlaying"
            min="10"
          />
        </div>
      </div>

      <div class="control-group">
        <label class="control-label">ПОДАРКИ</label>
        <div class="counter">
          <button class="counter-btn" @click="changeBallCount(-1)" :disabled="isPlaying || ballCount <= 1">−</button>
          <span class="counter-value">{{ ballCount }}</span>
          <button class="counter-btn" @click="changeBallCount(1)" :disabled="isPlaying || ballCount >= 10">+</button>
        </div>
      </div>
    </div>

    <!-- Risk level -->
    <div class="risk-section">
      <label class="control-label">УРОВЕНЬ РИСКА</label>
      <div class="risk-bar-wrapper" @click="onRiskClick">
        <div class="plinko-risk-bar">
          <div
            class="risk-indicator"
            :style="{ left: riskPosition + '%' }"
          />
        </div>
        <div class="risk-labels">
          <span :class="{ active: risk === 'low' }">Low</span>
          <span :class="{ active: risk === 'medium' }">Med</span>
          <span :class="{ active: risk === 'high' }">High</span>
        </div>
      </div>
    </div>

    <!-- Row count selector -->
    <div class="rows-section">
      <label class="control-label">РЯДЫ</label>
      <div class="row-options">
        <button
          v-for="r in [8, 12, 16]"
          :key="r"
          :class="['row-btn', { active: rows === r }]"
          @click="$emit('update:rows', r)"
          :disabled="isPlaying"
        >
          {{ r }}
        </button>
      </div>
    </div>

    <!-- Play button -->
    <button
      class="play-btn"
      @click="onPlay"
      :disabled="isPlaying || balance < bet * ballCount"
    >
      <svg v-if="!isPlaying" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M8 5v14l11-7z"/>
      </svg>
      <span v-if="isPlaying" class="spinner"></span>
      <span>{{ isPlaying ? 'ИГРА...' : 'ИГРАТЬ' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTelegram } from '@/composables/useTelegram'

const props = defineProps<{
  bet: number
  risk: 'low' | 'medium' | 'high'
  rows: 8 | 12 | 16
  ballCount: number
  isPlaying: boolean
  balance: number
}>()

const emit = defineEmits<{
  (e: 'update:bet', value: number): void
  (e: 'update:risk', value: 'low' | 'medium' | 'high'): void
  (e: 'update:rows', value: number): void
  (e: 'update:ballCount', value: number): void
  (e: 'play'): void
}>()

const { hapticImpact } = useTelegram()

const riskPosition = computed(() => {
  if (props.risk === 'low') return 15
  if (props.risk === 'medium') return 50
  return 85
})

function onBetInput(e: Event) {
  const val = parseInt((e.target as HTMLInputElement).value) || 10
  emit('update:bet', Math.max(10, Math.min(10000, val)))
}

function changeBallCount(delta: number) {
  const next = props.ballCount + delta
  if (next >= 1 && next <= 10) {
    emit('update:ballCount', next)
    hapticImpact?.('light')
  }
}

function onRiskClick(e: MouseEvent) {
  if (props.isPlaying) return
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const pct = (e.clientX - rect.left) / rect.width
  if (pct < 0.33) emit('update:risk', 'low')
  else if (pct < 0.66) emit('update:risk', 'medium')
  else emit('update:risk', 'high')
  hapticImpact?.('light')
}

function onPlay() {
  hapticImpact?.('medium')
  emit('play')
}
</script>

<style scoped>
.plinko-controls {
  background: var(--plinko-controls-bg, rgba(13, 8, 32, 0.95));
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--plinko-card-border, rgba(62, 30, 84, 0.4));
  padding: 12px 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.controls-row {
  display: flex;
  gap: 10px;
}

.control-group {
  flex: 1;
}

.control-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--plinko-text-secondary);
  margin-bottom: 6px;
}

.input-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--plinko-card, rgba(62, 30, 84, 0.25));
  border: 1px solid var(--plinko-card-border);
  border-radius: 10px;
  padding: 8px 12px;
}

.star-icon { flex-shrink: 0; }

.bet-input {
  background: none;
  border: none;
  color: var(--plinko-white);
  font-family: 'CoFo Sans Mono', 'SF Mono', monospace;
  font-size: 16px;
  font-weight: 700;
  width: 100%;
  outline: none;
  -moz-appearance: textfield;
}
.bet-input::-webkit-inner-spin-button,
.bet-input::-webkit-outer-spin-button { -webkit-appearance: none; }

.counter {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--plinko-card);
  border: 1px solid var(--plinko-card-border);
  border-radius: 10px;
  overflow: hidden;
}

.counter-btn {
  width: 36px;
  height: 38px;
  background: none;
  border: none;
  color: var(--plinko-white);
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.counter-btn:active { background: var(--plinko-purple); }
.counter-btn:disabled { opacity: 0.3; cursor: default; }

.counter-value {
  flex: 1;
  text-align: center;
  font-family: 'CoFo Sans Mono', monospace;
  font-size: 16px;
  font-weight: 700;
  min-width: 32px;
}

/* Risk */
.risk-bar-wrapper { cursor: pointer; }

.plinko-risk-bar {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg, #34CDEF 0%, #00FF62 25%, #FFC502 50%, #E23535 75%, #FF0055 100%);
  position: relative;
}

.risk-indicator {
  position: absolute;
  width: 4px;
  height: 16px;
  background: var(--plinko-white);
  border-radius: 2px;
  top: 50%;
  transform: translate(-50%, -50%);
  transition: left 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 0 6px rgba(253, 253, 253, 0.5);
}

.risk-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 10px;
  font-weight: 600;
  color: var(--plinko-text-tertiary);
}
.risk-labels span.active { color: var(--plinko-white); }

/* Rows */
.rows-section { display: none; }

.row-options {
  display: flex;
  gap: 8px;
}

.row-btn {
  flex: 1;
  padding: 6px;
  border-radius: 8px;
  border: 1px solid var(--plinko-card-border);
  background: var(--plinko-card);
  color: var(--plinko-text-secondary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.row-btn.active {
  background: var(--plinko-purple);
  color: var(--plinko-white);
  border-color: var(--plinko-purple-light, #5A2D7A);
}
.row-btn:disabled { opacity: 0.3; }

/* Play button */
.play-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 12px;
  background: var(--plinko-btn-gradient);
  color: white;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
}
.play-btn:active { transform: scale(0.98); }
.play-btn:disabled { opacity: 0.4; cursor: default; transform: none; }

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
