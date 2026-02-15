<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="visible" class="game-overlay" @click="$emit('close')">
        <!-- WIN -->
        <div v-if="type === 'win'" class="overlay-content win">
          <!-- Confetti particles -->
          <div class="confetti-container">
            <div v-for="i in 30" :key="i" class="confetti" :style="confettiStyle(i)"></div>
          </div>
          <!-- Glow ring -->
          <div class="glow-ring"></div>
          <!-- Star burst -->
          <div class="star-burst">
            <div v-for="i in 8" :key="'ray'+i" class="ray" :style="{ transform: `rotate(${i * 45}deg)` }"></div>
          </div>
          <!-- Icon -->
          <div class="icon-container win-icon">
            <svg viewBox="0 0 64 64" width="64" height="64">
              <circle cx="32" cy="32" r="30" fill="#22c55e" class="circle-pop"/>
              <path d="M20 32l8 8 16-16" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" class="check-draw"/>
            </svg>
          </div>
          <!-- Text -->
          <div class="overlay-title win-title">Победа!</div>
          <div v-if="amount" class="overlay-amount win-amount">+{{ amount }}
            <svg width="18" height="18" viewBox="0 0 56 56" fill="none" style="vertical-align:middle;margin-left:4px">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
          </div>
          <div v-if="multiplier" class="overlay-multiplier">x{{ multiplier }}</div>
        </div>

        <!-- LOSE -->
        <div v-if="type === 'lose'" class="overlay-content lose">
          <!-- Shatter particles -->
          <div class="shatter-container">
            <div v-for="i in 12" :key="i" class="shard" :style="shardStyle(i)"></div>
          </div>
          <!-- Icon -->
          <div class="icon-container lose-icon">
            <svg viewBox="0 0 64 64" width="64" height="64">
              <circle cx="32" cy="32" r="30" fill="#ef4444" class="circle-pop"/>
              <path d="M22 22l20 20M42 22l-20 20" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" class="x-draw"/>
            </svg>
          </div>
          <!-- Text -->
          <div class="overlay-title lose-title">Проигрыш</div>
          <div v-if="amount" class="overlay-amount lose-amount">-{{ amount }}
            <svg width="18" height="18" viewBox="0 0 56 56" fill="none" style="vertical-align:middle;margin-left:4px">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
          </div>
        </div>

        <!-- SPIN / Loading -->
        <div v-if="type === 'spin'" class="overlay-content spin">
          <div class="spinner-ring">
            <div class="spinner-segment" v-for="i in 4" :key="i"></div>
          </div>
          <div class="spinner-dots">
            <div class="dot" v-for="i in 3" :key="'d'+i" :style="{ animationDelay: `${i * 0.2}s` }"></div>
          </div>
          <div class="overlay-title spin-title">{{ spinText || 'Играем...' }}</div>
        </div>

        <!-- CASHOUT -->
        <div v-if="type === 'cashout'" class="overlay-content cashout">
          <div class="coins-container">
            <div v-for="i in 10" :key="i" class="coin" :style="coinStyle(i)">💰</div>
          </div>
          <div class="glow-ring cashout-glow"></div>
          <div class="icon-container cashout-icon">
            <svg viewBox="0 0 64 64" width="64" height="64">
              <circle cx="32" cy="32" r="30" fill="#eab308" class="circle-pop"/>
              <text x="32" y="40" text-anchor="middle" fill="#000" font-size="28" font-weight="bold">$</text>
            </svg>
          </div>
          <div class="overlay-title cashout-title">Кешаут!</div>
          <div v-if="amount" class="overlay-amount cashout-amount">+{{ amount }}
            <svg width="18" height="18" viewBox="0 0 56 56" fill="none" style="vertical-align:middle;margin-left:4px">
              <circle cx="28" cy="28" r="28" fill="#0098EA"/>
              <path d="M37.5603 15.6277H18.4386C14.9228 15.6277 12.6944 19.4202 14.4632 22.4861L26.2644 42.9409C27.0345 44.2765 28.9644 44.2765 29.7345 42.9409L41.5765 22.4861C43.3045 19.4202 41.0761 15.6277 37.5603 15.6277Z" fill="white"/>
            </svg>
          </div>
          <div v-if="multiplier" class="overlay-multiplier cashout-mult">x{{ multiplier }}</div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  type: 'win' | 'lose' | 'spin' | 'cashout'
  amount?: string | number
  multiplier?: string | number
  spinText?: string
}>()

defineEmits(['close'])

function confettiStyle(i: number) {
  const colors = ['#22c55e', '#3b82f6', '#eab308', '#ec4899', '#8b5cf6', '#f97316', '#14b8a6', '#ef4444']
  const x = (Math.random() - 0.5) * 300
  const y = -(Math.random() * 400 + 100)
  const rotate = Math.random() * 720 - 360
  const delay = Math.random() * 0.5
  const size = Math.random() * 8 + 4
  return {
    '--x': `${x}px`,
    '--y': `${y}px`,
    '--r': `${rotate}deg`,
    '--delay': `${delay}s`,
    width: `${size}px`,
    height: `${size * 0.6}px`,
    background: colors[i % colors.length],
    animationDelay: `${delay}s`,
  }
}

function shardStyle(i: number) {
  const angle = (360 / 12) * i
  const distance = 60 + Math.random() * 40
  return {
    '--angle': `${angle}deg`,
    '--distance': `${distance}px`,
    animationDelay: `${Math.random() * 0.2}s`,
  }
}

function coinStyle(i: number) {
  const angle = (360 / 10) * i
  const dist = 80 + Math.random() * 60
  return {
    '--angle': `${angle}deg`,
    '--dist': `${dist}px`,
    animationDelay: `${i * 0.05}s`,
  }
}
</script>

<style scoped>
.game-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  animation: contentPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes contentPop {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

/* Transition */
.overlay-enter-active { transition: opacity 0.2s; }
.overlay-leave-active { transition: opacity 0.3s; }
.overlay-enter-from, .overlay-leave-to { opacity: 0; }

/* ============ ICONS ============ */
.icon-container {
  position: relative;
  z-index: 10;
  margin-bottom: 16px;
}

.circle-pop {
  animation: circlePop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes circlePop {
  0% { r: 0; }
  60% { r: 34; }
  100% { r: 30; }
}

.check-draw {
  stroke-dasharray: 50;
  stroke-dashoffset: 50;
  animation: drawCheck 0.4s 0.3s ease forwards;
}

@keyframes drawCheck {
  to { stroke-dashoffset: 0; }
}

.x-draw {
  stroke-dasharray: 30;
  stroke-dashoffset: 30;
  animation: drawX 0.3s 0.3s ease forwards;
}

@keyframes drawX {
  to { stroke-dashoffset: 0; }
}

/* ============ TEXT ============ */
.overlay-title {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 8px;
  animation: titleSlide 0.4s 0.2s ease both;
}

@keyframes titleSlide {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.win-title { color: #22c55e; }
.lose-title { color: #ef4444; }
.spin-title { color: #fff; }
.cashout-title { color: #eab308; }

.overlay-amount {
  font-size: 36px;
  font-weight: 800;
  animation: amountPop 0.3s 0.4s ease both;
}

@keyframes amountPop {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.win-amount { color: #4ade80; }
.lose-amount { color: #f87171; }
.cashout-amount { color: #facc15; }

.overlay-multiplier {
  font-size: 18px;
  font-weight: 700;
  color: rgba(255,255,255,0.6);
  animation: amountPop 0.3s 0.5s ease both;
}

.cashout-mult { color: rgba(234,179,8,0.7); }

/* ============ GLOW RING ============ */
.glow-ring {
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  border: 3px solid rgba(34, 197, 94, 0.4);
  animation: glowPulse 1s ease infinite;
  z-index: 1;
}

.cashout-glow {
  border-color: rgba(234, 179, 8, 0.4);
}

@keyframes glowPulse {
  0% { transform: scale(0.8); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 0.2; }
  100% { transform: scale(0.8); opacity: 0.8; }
}

/* ============ STAR BURST ============ */
.star-burst {
  position: absolute;
  width: 200px;
  height: 200px;
  z-index: 0;
}

.ray {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 80px;
  background: linear-gradient(to top, transparent, rgba(34, 197, 94, 0.6));
  transform-origin: center bottom;
  animation: rayShoot 0.6s 0.2s ease-out both;
}

@keyframes rayShoot {
  from { height: 0; opacity: 0; }
  to { height: 80px; opacity: 1; }
}

/* ============ CONFETTI ============ */
.confetti-container {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 0;
}

.confetti {
  position: absolute;
  border-radius: 2px;
  animation: confettiFall 1s var(--delay) ease-out both;
}

@keyframes confettiFall {
  0% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translate(var(--x), var(--y)) rotate(var(--r));
    opacity: 0;
  }
}

/* ============ SHATTER ============ */
.shatter-container {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 0;
}

.shard {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 2px;
  animation: shardFly 0.6s ease-out both;
}

@keyframes shardFly {
  0% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform:
      translate(
        calc(cos(var(--angle)) * var(--distance)),
        calc(sin(var(--angle)) * var(--distance))
      )
      rotate(720deg);
    opacity: 0;
  }
}

/* ============ SPINNER ============ */
.spinner-ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 4px solid rgba(255,255,255,0.1);
  border-top-color: #3b82f6;
  border-right-color: #8b5cf6;
  animation: spinRing 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spinRing {
  to { transform: rotate(360deg); }
}

.spinner-dots {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: dotBounce 0.6s ease-in-out infinite alternate;
}

@keyframes dotBounce {
  from { transform: translateY(0); opacity: 0.3; }
  to { transform: translateY(-12px); opacity: 1; }
}

/* ============ COINS ============ */
.coins-container {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 0;
}

.coin {
  position: absolute;
  font-size: 20px;
  animation: coinFly 0.8s ease-out both;
}

@keyframes coinFly {
  0% {
    transform: translate(0, 0) scale(0);
    opacity: 1;
  }
  100% {
    transform:
      translate(
        calc(cos(var(--angle)) * var(--dist)),
        calc(sin(var(--angle)) * var(--dist))
      )
      scale(1);
    opacity: 0;
  }
}
</style>
