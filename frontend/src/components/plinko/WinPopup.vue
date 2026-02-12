<template>
  <Transition name="plinko-popup">
    <div v-if="visible" class="win-popup-overlay" @click.self="close">
      <div class="win-popup">
        <h2 class="popup-title">ПОЗДРАВЛЯЕМ</h2>
        <p class="popup-subtitle">Ваш выигрыш</p>

        <div class="popup-amount">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="#FFB800"/>
            <path d="M12 5l2.5 5 5.5.8-4 3.8 1 5.4-5-2.6-5 2.6 1-5.4-4-3.8 5.5-.8z" fill="white"/>
          </svg>
          <span class="amount-value">{{ payout.toFixed(2) }}</span>
          <span class="mult-badge">{{ multiplier.toFixed(1) }}x</span>
        </div>

        <button class="popup-close" @click="close">OK</button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useTelegram } from '@/composables/useTelegram'

defineProps<{
  multiplier: number
  payout: number
}>()

const emit = defineEmits<{ close: [] }>()
const { hapticNotification } = useTelegram()

const visible = ref(true)

onMounted(() => {
  hapticNotification?.('success')
  // Auto-dismiss after 3s
  setTimeout(() => {
    close()
  }, 3000)
})

function close() {
  visible.value = false
  setTimeout(() => emit('close'), 300)
}
</script>

<style scoped>
.win-popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7, 4, 19, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.win-popup {
  background: linear-gradient(160deg, #1A0E2E 0%, #0D0820 100%);
  border: 1px solid rgba(62, 30, 84, 0.5);
  border-radius: 24px;
  padding: 32px 28px;
  text-align: center;
  width: 100%;
  max-width: 320px;
  box-shadow: 0 20px 60px rgba(57, 26, 173, 0.3);
}

.popup-title {
  font-family: 'Chroma ST', 'SF Pro Display', sans-serif;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 2px;
  margin: 0 0 4px;
  background: linear-gradient(135deg, #FDFDFD 0%, #BF8B77 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.popup-subtitle {
  font-size: 14px;
  color: var(--plinko-text-secondary, rgba(253,253,253,0.5));
  margin: 0 0 24px;
}

.popup-amount {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 28px;
}

.amount-value {
  font-family: 'CoFo Sans Mono', monospace;
  font-size: 32px;
  font-weight: 800;
  color: var(--plinko-white, #FDFDFD);
}

.mult-badge {
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(0, 255, 98, 0.15);
  color: #00FF62;
  font-size: 14px;
  font-weight: 700;
  font-family: 'CoFo Sans Mono', monospace;
}

.popup-close {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 12px;
  background: var(--plinko-btn-gradient, linear-gradient(135deg, #391AAD, #6B2FBE));
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s;
}
.popup-close:active { opacity: 0.8; }

/* Transition */
.plinko-popup-enter-active { animation: plinko-popup-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.plinko-popup-leave-active { animation: plinko-popup-out 0.2s ease-in; }

@keyframes plinko-popup-in {
  from { opacity: 0; transform: scale(0.85); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes plinko-popup-out {
  from { opacity: 1; transform: scale(1); }
  to { opacity: 0; transform: scale(0.85); }
}
</style>
