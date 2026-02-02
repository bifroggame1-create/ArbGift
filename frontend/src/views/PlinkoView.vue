<template>
  <div class="plinko-view">
    <!-- Animated stars background -->
    <div class="stars-bg">
      <div v-for="i in 20" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- Header -->
    <header class="plinko-header">
      <button class="header-back" @click="$router.push('/solo')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="header-title">
        <span class="title-main">Plinko</span>
        <span class="title-badge">x1000</span>
      </div>
      <div class="header-balance">
        <span class="balance-icon">💎</span>
        <span class="balance-value">{{ balance.toFixed(2) }}</span>
        <button class="balance-add">+</button>
      </div>
    </header>

    <!-- Game Info Bar -->
    <div class="game-info-bar">
      <div class="info-item">
        <span class="info-label">ИГРА</span>
        <span class="info-value">#{{ gameNumber }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">РИСК</span>
        <select v-model="riskLevel" class="risk-select">
          <option value="low">Низкий</option>
          <option value="medium">Средний</option>
          <option value="high">Высокий</option>
        </select>
      </div>
      <div class="info-item">
        <span class="info-label">РЯДЫ</span>
        <select v-model="rowCount" class="rows-select">
          <option :value="8">8</option>
          <option :value="12">12</option>
          <option :value="16">16</option>
        </select>
      </div>
    </div>

    <!-- Game Canvas -->
    <div class="game-container">
      <canvas
        ref="gameCanvas"
        class="game-canvas"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>

      <!-- Result Overlay -->
      <div v-if="showResult" class="result-overlay" :class="{ win: lastWin > 0, lose: lastWin <= 0 }">
        <div class="result-multiplier">{{ lastMultiplier }}x</div>
        <div class="result-amount" :class="{ positive: lastWin > 0 }">
          {{ lastWin > 0 ? '+' : '' }}{{ lastWin.toFixed(2) }} TON
        </div>
      </div>
    </div>

    <!-- Multiplier Slots Preview -->
    <div class="multipliers-row">
      <div
        v-for="(mult, i) in currentMultipliers"
        :key="i"
        :class="['mult-slot', getMultiplierClass(mult)]"
      >
        {{ mult }}x
      </div>
    </div>

    <!-- Bet Controls -->
    <div class="bet-section">
      <div class="bet-amounts">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          :class="['bet-btn', { active: selectedBet === amount }]"
          @click="selectedBet = amount"
          :disabled="isPlaying"
        >
          {{ amount }} 💎
        </button>
      </div>

      <div class="action-row">
        <button class="btn-half" @click="halveBet" :disabled="isPlaying">½</button>
        <button
          class="btn-play"
          @click="playGame"
          :disabled="isPlaying || balance < selectedBet"
        >
          <span v-if="isPlaying" class="loading-spinner"></span>
          <span v-else>{{ isPlaying ? 'Игра...' : `Играть ${selectedBet} TON` }}</span>
        </button>
        <button class="btn-double" @click="doubleBet" :disabled="isPlaying">2x</button>
      </div>

      <div class="auto-play">
        <label class="auto-label">
          <input type="checkbox" v-model="autoPlay" :disabled="isPlaying" />
          <span>Авто-игра</span>
        </label>
        <input
          v-if="autoPlay"
          type="number"
          v-model.number="autoPlayCount"
          class="auto-count"
          min="1"
          max="100"
          placeholder="Кол-во"
        />
      </div>
    </div>

    <!-- History -->
    <div class="history-section">
      <div class="history-header">
        <span>История</span>
        <span class="history-clear" @click="history = []">Очистить</span>
      </div>
      <div class="history-list">
        <div
          v-for="(item, i) in history.slice(0, 10)"
          :key="i"
          :class="['history-item', { win: item.win > 0 }]"
        >
          <span class="history-mult">{{ item.multiplier }}x</span>
          <span class="history-amount">{{ item.win > 0 ? '+' : '' }}{{ item.win.toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface HistoryItem {
  multiplier: number
  win: number
  bet: number
}

// Game state
const balance = ref(5.16)
const gameNumber = ref(48291)
const isPlaying = ref(false)
const showResult = ref(false)
const lastMultiplier = ref(0)
const lastWin = ref(0)

// Settings
const riskLevel = ref<'low' | 'medium' | 'high'>('medium')
const rowCount = ref(12)
const betAmounts = [0.5, 1, 2, 5, 10]
const selectedBet = ref(1)
const autoPlay = ref(false)
const autoPlayCount = ref(10)
const history = ref<HistoryItem[]>([])

// Canvas
const gameCanvas = ref<HTMLCanvasElement | null>(null)
const canvasWidth = 340
const canvasHeight = 280

// Multipliers based on risk
const multiplierSets = {
  low: {
    8: [5.6, 2.1, 1.1, 1, 0.5, 1, 1.1, 2.1, 5.6],
    12: [8.9, 3, 1.4, 1.1, 1, 0.5, 1, 1.1, 1.4, 3, 8.9],
    16: [16, 9, 2, 1.4, 1.1, 1, 0.5, 1, 1.1, 1.4, 2, 9, 16]
  },
  medium: {
    8: [13, 3, 1.3, 0.7, 0.4, 0.7, 1.3, 3, 13],
    12: [33, 11, 4, 2, 1.1, 0.6, 0.3, 0.6, 1.1, 2, 4, 11, 33],
    16: [110, 41, 10, 5, 3, 1.5, 1, 0.5, 0.3, 0.5, 1, 1.5, 3, 5, 10, 41, 110]
  },
  high: {
    8: [29, 4, 1.5, 0.3, 0.2, 0.3, 1.5, 4, 29],
    12: [170, 24, 8.1, 2, 0.7, 0.2, 0.2, 0.7, 2, 8.1, 24, 170],
    16: [1000, 130, 26, 9, 4, 2, 0.2, 0.2, 0.2, 0.2, 2, 4, 9, 26, 130, 1000]
  }
}

const currentMultipliers = computed(() => {
  const set = multiplierSets[riskLevel.value]
  return set[rowCount.value as keyof typeof set] || set[12]
})

// Plinko physics - slower, more realistic
const PEG_RADIUS = 5
const BALL_RADIUS = 6
const GRAVITY = 0.15  // Slower fall for drama
const BOUNCE = 0.6    // Good bounce off pegs
const MAX_FRAMES = 800 // More time for slower fall

// Tube visual
const TUBE_WIDTH = 28
const TUBE_HEIGHT = 35
const TUBE_Y = 0

// Ball drop animation
let dropPhase: 'in_tube' | 'dropping' | 'falling' = 'in_tube'
let dropTimer = 0

interface Ball {
  x: number
  y: number
  vx: number
  vy: number
}

interface Peg {
  x: number
  y: number
}

let ball: Ball | null = null
let pegs: Peg[] = []
let animationId: number | null = null
let targetSlot = 0
let frameCount = 0

// Stars background
const getStarStyle = (_i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

const getMultiplierClass = (mult: number) => {
  if (mult >= 10) return 'high'
  if (mult >= 2) return 'medium'
  if (mult >= 1) return 'low'
  return 'lose'
}

const halveBet = () => {
  selectedBet.value = Math.max(0.1, selectedBet.value / 2)
}

const doubleBet = () => {
  selectedBet.value = Math.min(balance.value, selectedBet.value * 2)
}

const computePegs = () => {
  pegs = []
  const rows = rowCount.value
  const topY = TUBE_HEIGHT + 40 // Well below tube — leaves gap for ball to gain speed
  const bottomY = canvasHeight - 45
  const rowHeight = (bottomY - topY) / rows
  const centerX = canvasWidth / 2

  for (let row = 0; row < rows; row++) {
    const numPegs = row + 3
    const spacing = 22
    const startX = centerX - ((numPegs - 1) * spacing) / 2

    for (let col = 0; col < numPegs; col++) {
      pegs.push({
        x: startX + col * spacing,
        y: topY + row * rowHeight
      })
    }
  }
}

const playGame = async () => {
  if (isPlaying.value || balance.value < selectedBet.value) return

  isPlaying.value = true
  showResult.value = false
  balance.value -= selectedBet.value
  gameNumber.value++

  // Determine outcome
  const mults = currentMultipliers.value
  const weights = mults.map(m => 1 / (m + 0.1)) // Lower multipliers more likely
  const totalWeight = weights.reduce((a, b) => a + b, 0)
  let r = Math.random() * totalWeight
  targetSlot = Math.floor(mults.length / 2)

  for (let i = 0; i < weights.length; i++) {
    r -= weights[i]
    if (r <= 0) {
      targetSlot = i
      break
    }
  }

  // Start ball in tube
  ball = {
    x: canvasWidth / 2,
    y: 8,
    vx: 0,
    vy: 0
  }

  frameCount = 0
  dropPhase = 'in_tube'
  dropTimer = 0
  computePegs()
  animate()
}

const animate = () => {
  if (!ball) return

  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  frameCount++

  // === DROP PHASES ===
  if (dropPhase === 'in_tube') {
    // Ball waits in tube for a moment
    dropTimer++
    if (dropTimer > 30) {
      dropPhase = 'dropping'
      ball.vy = 0.5 // Start slow
      ball.vx = (Math.random() - 0.5) * 0.5
    }
    draw(ctx)
    animationId = requestAnimationFrame(animate)
    return
  }

  if (dropPhase === 'dropping') {
    // Ball exits tube with acceleration
    ball.vy += 0.12
    ball.y += ball.vy

    // Wait until ball is well clear of tube before starting physics
    if (ball.y > TUBE_HEIGHT + 25) {
      dropPhase = 'falling'
      // Give ball good initial velocity to avoid getting stuck
      ball.vy = Math.max(ball.vy, 2.5)
      ball.vx = (Math.random() - 0.5) * 2
    }

    draw(ctx)
    animationId = requestAnimationFrame(animate)
    return
  }

  // === FALLING PHASE ===
  // Timeout - force finish if stuck too long
  if (frameCount > MAX_FRAMES) {
    ball.y = canvasHeight - 25
    ball.vy = 0
  }

  // Physics with slower gravity for dramatic effect
  ball.vy += GRAVITY
  ball.x += ball.vx
  ball.y += ball.vy

  // Limit max velocity
  const maxVel = 8
  ball.vx = Math.max(-maxVel, Math.min(maxVel, ball.vx))
  ball.vy = Math.max(-maxVel, Math.min(maxVel, ball.vy))

  // Anti-stuck: ensure ball always moves downward
  if (ball.vy < 0.3) {
    ball.vy = 0.3 + GRAVITY
  }

  // Peg collisions - only one peg per frame to prevent multi-collision stuck
  let collided = false
  for (const peg of pegs) {
    if (collided) break  // Only handle first collision per frame

    const dx = ball.x - peg.x
    const dy = ball.y - peg.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    const minDist = PEG_RADIUS + BALL_RADIUS

    if (dist < minDist && dist > 0.1) {
      collided = true
      const nx = dx / dist
      const ny = dy / dist

      // Push ball fully out of peg
      const overlap = minDist - dist + 1.0
      ball.x += nx * overlap
      ball.y += ny * overlap

      // Always push ball downward if collision pushes it up
      if (ball.y < peg.y) {
        ball.y = peg.y + minDist + 1
      }

      // Reflect velocity with satisfying bounce
      const dot = ball.vx * nx + ball.vy * ny
      if (dot < 0) {
        ball.vx -= 2 * dot * nx * BOUNCE * 1.2
        ball.vy -= 2 * dot * ny * BOUNCE * 0.8

        ball.vx *= 0.95
        ball.vy *= 0.95
      }

      // Random deflection for unpredictability
      ball.vx += (Math.random() - 0.5) * 1.0

      // Subtle steering toward target in lower half
      if (ball.y > canvasHeight * 0.6) {
        const mults = currentMultipliers.value
        const slotWidth = canvasWidth / mults.length
        const targetX = targetSlot * slotWidth + slotWidth / 2
        ball.vx += (targetX - ball.x) * 0.003
      }

      // Enforce minimum downward velocity after every collision
      if (ball.vy < 1.0) {
        ball.vy = 1.5
      }
    }
  }

  // Wall collisions
  if (ball.x < BALL_RADIUS) {
    ball.x = BALL_RADIUS
    ball.vx = Math.abs(ball.vx) * BOUNCE
  }
  if (ball.x > canvasWidth - BALL_RADIUS) {
    ball.x = canvasWidth - BALL_RADIUS
    ball.vx = -Math.abs(ball.vx) * BOUNCE
  }

  // Draw
  draw(ctx)

  // Check if ball reached bottom
  if (ball.y > canvasHeight - 30) {
    const mults = currentMultipliers.value
    const slotWidth = canvasWidth / mults.length
    const landedSlot = Math.floor(ball.x / slotWidth)
    const finalSlot = Math.max(0, Math.min(mults.length - 1, landedSlot))

    lastMultiplier.value = mults[finalSlot]
    lastWin.value = selectedBet.value * mults[finalSlot] - selectedBet.value
    balance.value += selectedBet.value * mults[finalSlot]

    history.value.unshift({
      multiplier: mults[finalSlot],
      win: lastWin.value,
      bet: selectedBet.value
    })

    showResult.value = true
    ball = null
    isPlaying.value = false

    setTimeout(() => {
      showResult.value = false
      if (autoPlay.value && autoPlayCount.value > 0) {
        autoPlayCount.value--
        if (autoPlayCount.value > 0 && balance.value >= selectedBet.value) {
          playGame()
        }
      }
    }, 1500)
    return
  }

  animationId = requestAnimationFrame(animate)
}

const draw = (ctx: CanvasRenderingContext2D) => {
  // Clear
  ctx.fillStyle = '#0a1628'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  // === TUBE at top center ===
  const tubeX = canvasWidth / 2 - TUBE_WIDTH / 2
  const tubeGradient = ctx.createLinearGradient(tubeX, 0, tubeX + TUBE_WIDTH, 0)
  tubeGradient.addColorStop(0, '#374151')
  tubeGradient.addColorStop(0.3, '#4b5563')
  tubeGradient.addColorStop(0.7, '#4b5563')
  tubeGradient.addColorStop(1, '#374151')

  // Tube body
  ctx.fillStyle = tubeGradient
  ctx.beginPath()
  ctx.roundRect(tubeX, TUBE_Y, TUBE_WIDTH, TUBE_HEIGHT, [0, 0, 8, 8])
  ctx.fill()

  // Tube inner shadow
  const innerGradient = ctx.createLinearGradient(tubeX + 4, 0, tubeX + TUBE_WIDTH - 4, 0)
  innerGradient.addColorStop(0, 'rgba(0,0,0,0.4)')
  innerGradient.addColorStop(0.5, 'rgba(0,0,0,0.1)')
  innerGradient.addColorStop(1, 'rgba(0,0,0,0.4)')
  ctx.fillStyle = innerGradient
  ctx.fillRect(tubeX + 3, TUBE_Y, TUBE_WIDTH - 6, TUBE_HEIGHT - 4)

  // Tube opening glow when ball is dropping
  if (dropPhase === 'dropping' || dropPhase === 'in_tube') {
    ctx.shadowColor = 'rgba(236, 72, 153, 0.5)'
    ctx.shadowBlur = 10
    ctx.fillStyle = 'rgba(236, 72, 153, 0.2)'
    ctx.beginPath()
    ctx.ellipse(canvasWidth / 2, TUBE_HEIGHT, 12, 4, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.shadowBlur = 0
  }

  // Draw pegs
  const rows = rowCount.value
  for (let i = 0; i < pegs.length; i++) {
    const peg = pegs[i]
    const row = Math.floor((-3 + Math.sqrt(9 + 8 * i)) / 2)
    const t = row / rows

    // Gradient from blue to cyan
    const r = Math.round(59 + (34 - 59) * t)
    const g = Math.round(130 + (211 - 130) * t)
    const b = Math.round(246 + (238 - 246) * t)

    ctx.fillStyle = `rgb(${r},${g},${b})`
    ctx.shadowColor = `rgba(${r},${g},${b},0.5)`
    ctx.shadowBlur = 6
    ctx.beginPath()
    ctx.arc(peg.x, peg.y, PEG_RADIUS, 0, Math.PI * 2)
    ctx.fill()
  }
  ctx.shadowBlur = 0

  // Draw ball
  if (ball) {
    // Ball visibility based on phase
    let ballVisible = true
    let ballY = ball.y

    if (dropPhase === 'in_tube') {
      // Ball visible in tube opening
      ballY = TUBE_HEIGHT - 4
      // Wobble animation
      ball.x = canvasWidth / 2 + Math.sin(frameCount * 0.15) * 2
    }

    if (ballVisible) {
      // Ball glow
      ctx.shadowColor = 'rgba(236, 72, 153, 0.8)'
      ctx.shadowBlur = 15

      // Ball gradient for 3D effect
      const ballGrad = ctx.createRadialGradient(
        ball.x - 2, ballY - 2, 0,
        ball.x, ballY, BALL_RADIUS
      )
      ballGrad.addColorStop(0, '#f472b6')
      ballGrad.addColorStop(0.5, '#ec4899')
      ballGrad.addColorStop(1, '#be185d')

      ctx.fillStyle = ballGrad
      ctx.beginPath()
      ctx.arc(ball.x, ballY, BALL_RADIUS, 0, Math.PI * 2)
      ctx.fill()
      ctx.shadowBlur = 0

      // Highlight
      ctx.fillStyle = 'rgba(255, 255, 255, 0.5)'
      ctx.beginPath()
      ctx.arc(ball.x - 2, ballY - 2, BALL_RADIUS * 0.35, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // Draw slot zones
  const mults = currentMultipliers.value
  const slotWidth = canvasWidth / mults.length
  const slotY = canvasHeight - 28

  mults.forEach((mult, i) => {
    const x = i * slotWidth

    // Color based on multiplier
    let color = 'rgba(99,102,241,0.3)'
    if (mult >= 10) color = 'rgba(34,197,94,0.4)'
    else if (mult >= 2) color = 'rgba(34,211,238,0.3)'
    else if (mult < 1) color = 'rgba(239,68,68,0.3)'

    ctx.fillStyle = color
    ctx.fillRect(x + 1, slotY, slotWidth - 2, 26)

    ctx.fillStyle = '#fff'
    ctx.font = 'bold 9px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(`${mult}x`, x + slotWidth / 2, slotY + 16)
  })
}

watch([riskLevel, rowCount], () => {
  computePegs()
  if (gameCanvas.value) {
    const ctx = gameCanvas.value.getContext('2d')
    if (ctx) draw(ctx)
  }
})

onMounted(() => {
  computePegs()
  if (gameCanvas.value) {
    const ctx = gameCanvas.value.getContext('2d')
    if (ctx) draw(ctx)
  }
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.plinko-view {
  min-height: 100vh;
  background: #000;
  color: #fff;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 90px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
}

/* Stars */
.stars-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  background: #fff;
  border-radius: 50%;
  opacity: 0.3;
  animation: twinkle 3s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.3); }
}

/* Header */
.plinko-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  position: relative;
  z-index: 10;
}

.header-back {
  width: 40px;
  height: 40px;
  background: #1c1c1e;
  border: none;
  border-radius: 12px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-main {
  font-size: 18px;
  font-weight: 700;
}

.title-badge {
  background: #22c55e;
  color: #000;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}

.header-balance {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1c1c1e;
  padding: 8px 12px;
  border-radius: 12px;
}

.balance-icon { font-size: 14px; }
.balance-value { font-size: 14px; font-weight: 600; }

.balance-add {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid #4b5563;
  background: transparent;
  color: #fff;
  font-size: 14px;
}

/* Game Info Bar */
.game-info-bar {
  display: flex;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 12px;
  position: relative;
  z-index: 10;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.info-label {
  font-size: 10px;
  color: #6b7280;
}

.info-value {
  font-size: 12px;
  font-weight: 600;
}

.risk-select, .rows-select {
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  border-radius: 8px;
  padding: 4px 8px;
  font-size: 12px;
  color: #fff;
  outline: none;
}

/* Game Container */
.game-container {
  margin: 0 16px;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  z-index: 10;
  background: #0a1628;
}

.game-canvas {
  display: block;
  width: 100%;
  max-width: 340px;
  margin: 0 auto;
}

/* Result Overlay */
.result-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  padding: 20px 40px;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  animation: popIn 0.3s ease;
}

@keyframes popIn {
  from { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
  to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

.result-overlay.win { border: 2px solid #22c55e; }
.result-overlay.lose { border: 2px solid #ef4444; }

.result-multiplier {
  font-size: 32px;
  font-weight: 800;
  color: #fff;
}

.result-amount {
  font-size: 16px;
  color: #ef4444;
  margin-top: 4px;
}

.result-amount.positive {
  color: #4ade80;
}

/* Multipliers Row */
.multipliers-row {
  display: flex;
  justify-content: center;
  gap: 4px;
  padding: 12px 16px;
  position: relative;
  z-index: 10;
  overflow-x: auto;
}

.mult-slot {
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.mult-slot.high {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.mult-slot.medium {
  background: rgba(34, 211, 238, 0.2);
  color: #22d3ee;
}

.mult-slot.low {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}

.mult-slot.lose {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

/* Bet Section */
.bet-section {
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.bet-amounts {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  overflow-x: auto;
}

.bet-btn {
  flex: 1;
  min-width: 60px;
  padding: 10px 8px;
  background: #1c1c1e;
  border: 2px solid transparent;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.bet-btn.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.15);
}

.bet-btn:disabled {
  opacity: 0.5;
}

.action-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.btn-half, .btn-double {
  width: 50px;
  height: 50px;
  background: #1c1c1e;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.btn-half:disabled, .btn-double:disabled {
  opacity: 0.4;
}

.btn-play {
  flex: 1;
  height: 50px;
  background: linear-gradient(135deg, #3b82f6, #22d3ee);
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-play:disabled {
  opacity: 0.5;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Auto Play */
.auto-play {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #1c1c1e;
  border-radius: 12px;
  margin-bottom: 16px;
}

.auto-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #9ca3af;
}

.auto-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #3b82f6;
}

.auto-count {
  width: 60px;
  background: #27272a;
  border: 1px solid #3a3a3c;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  color: #fff;
  outline: none;
}

/* History */
.history-section {
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
}

.history-clear {
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
}

.history-list {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.history-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.15);
  border-radius: 10px;
  min-width: 60px;
}

.history-item.win {
  background: rgba(34, 197, 94, 0.15);
}

.history-mult {
  font-size: 12px;
  font-weight: 600;
}

.history-amount {
  font-size: 10px;
  color: #f87171;
}

.history-item.win .history-amount {
  color: #4ade80;
}

/* Bottom Nav */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #000;
  border-top: 1px solid #1c1c1e;
  display: flex;
  padding: 8px 0 24px;
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  text-decoration: none;
  font-size: 10px;
}

.nav-item.active { color: #fff; }
.nav-item svg { width: 22px; height: 22px; }
</style>
