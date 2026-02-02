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
        <select v-model="rowCount" class="rows-select" @change="onRowCountChange">
          <option :value="8">8</option>
          <option :value="12">12</option>
          <option :value="16">16</option>
        </select>
      </div>
    </div>

    <!-- Game Canvas -->
    <div class="game-container" ref="gameContainer">
      <canvas
        ref="gameCanvas"
        class="game-canvas"
      ></canvas>

      <!-- Result Overlay -->
      <div v-if="showResult" class="result-overlay" :class="{ win: lastWin > 0, lose: lastWin <= 0 }">
        <div class="result-multiplier">{{ lastMultiplier }}x</div>
        <div class="result-amount" :class="{ positive: lastWin > 0 }">
          {{ lastWin > 0 ? '+' : '' }}{{ lastWin.toFixed(2) }} TON
        </div>
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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

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

// Canvas refs
const gameCanvas = ref<HTMLCanvasElement | null>(null)
const gameContainer = ref<HTMLDivElement | null>(null)

// Responsive canvas sizing
let canvasWidth = 380
let canvasHeight = 500

// Multipliers based on risk
const multiplierSets: Record<string, Record<number, number[]>> = {
  low: {
    8: [5.6, 2.1, 1.1, 1, 0.5, 1, 1.1, 2.1, 5.6],
    12: [8.9, 3, 1.4, 1.1, 1, 0.5, 0.3, 0.5, 1, 1.1, 1.4, 3, 8.9],
    16: [16, 9, 2, 1.4, 1.1, 1, 0.5, 0.3, 0.3, 0.5, 1, 1.1, 1.4, 2, 9, 16]
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
  return set[rowCount.value] || set[12]
})

// ========== PHYSICS ENGINE ==========

const BALL_RADIUS = 7
const GRAVITY = 0.25
const FRICTION = 0.99        // Air friction
const BOUNCE_COEFF = 0.65    // Elasticity on peg hit
const WALL_BOUNCE = 0.4
const MAX_SPEED = 12

interface Ball {
  x: number
  y: number
  vx: number
  vy: number
  trail: { x: number; y: number; age: number }[]
}

interface Peg {
  x: number
  y: number
  radius: number
  glowIntensity: number  // For hit glow effect
}

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
  color: string
  size: number
}

let ball: Ball | null = null
let pegs: Peg[] = []
let particles: Particle[] = []
let animationId: number | null = null
let idleAnimId: number | null = null
let targetSlot = 0

// Tube (pendulum) state
const TUBE_WIDTH = 30
const TUBE_HEIGHT = 38
const TUBE_TOP = 4
let tubeX = 0              // Current X position of tube center
let tubeAngle = 0          // Pendulum angle in radians
let tubeAngularVel = 0     // Angular velocity
const TUBE_AMPLITUDE = 0.12  // Max swing angle (~7 degrees) — almost stopped
const TUBE_DAMPING = 0.998   // Very slow decay
const TUBE_FREQ = 0.015      // Slow swing frequency
let dropPhase: 'idle' | 'holding' | 'releasing' | 'falling' = 'idle'
let holdTimer = 0

// Peg layout config
let pegSpacingX = 28
let pegSpacingY = 0
let pegRadius = 4
let startY = 80  // First row Y — shifted down for tube space
let endY = 0     // Last row Y

const computePegs = () => {
  pegs = []
  const rows = rowCount.value

  // Adjust sizing based on row count
  if (rows <= 8) {
    pegSpacingX = 36
    pegRadius = 5
  } else if (rows <= 12) {
    pegSpacingX = 28
    pegRadius = 4
  } else {
    pegSpacingX = 22
    pegRadius = 3.5
  }

  startY = TUBE_TOP + TUBE_HEIGHT + 30  // Below tube with gap
  const slotHeight = 36
  endY = canvasHeight - slotHeight - 10
  pegSpacingY = (endY - startY) / (rows - 1)

  const centerX = canvasWidth / 2

  for (let row = 0; row < rows; row++) {
    const numPegs = row + 3
    const rowWidth = (numPegs - 1) * pegSpacingX
    const rowStartX = centerX - rowWidth / 2

    for (let col = 0; col < numPegs; col++) {
      pegs.push({
        x: rowStartX + col * pegSpacingX,
        y: startY + row * pegSpacingY,
        radius: pegRadius,
        glowIntensity: 0,
      })
    }
  }
}

const spawnParticles = (x: number, y: number, color: string, count: number) => {
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2
    const speed = 1 + Math.random() * 3
    particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      maxLife: 15 + Math.random() * 15,
      color,
      size: 1.5 + Math.random() * 2,
    })
  }
}

const updateParticles = () => {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i]
    p.x += p.vx
    p.y += p.vy
    p.vy += 0.05  // Slight gravity on particles
    p.vx *= 0.97
    p.life += 1
    if (p.life >= p.maxLife) {
      particles.splice(i, 1)
    }
  }
}

// Stars background
const getStarStyle = (_i: number) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  width: `${Math.random() * 2 + 1}px`,
  height: `${Math.random() * 2 + 1}px`,
  animationDelay: `${Math.random() * 3}s`,
  animationDuration: `${Math.random() * 2 + 2}s`
})

const halveBet = () => {
  selectedBet.value = Math.max(0.1, selectedBet.value / 2)
}

const doubleBet = () => {
  selectedBet.value = Math.min(balance.value, selectedBet.value * 2)
}

const playGame = async () => {
  if (isPlaying.value || balance.value < selectedBet.value) return

  isPlaying.value = true
  showResult.value = false
  balance.value -= selectedBet.value
  gameNumber.value++

  // Determine outcome
  const mults = currentMultipliers.value
  const weights = mults.map((m: number) => 1 / (m + 0.1))
  const totalWeight = weights.reduce((a: number, b: number) => a + b, 0)
  let r = Math.random() * totalWeight
  targetSlot = Math.floor(mults.length / 2)

  for (let i = 0; i < weights.length; i++) {
    r -= weights[i]
    if (r <= 0) {
      targetSlot = i
      break
    }
  }

  computePegs()

  // Stop idle animation — game animation takes over
  if (idleAnimId) {
    cancelAnimationFrame(idleAnimId)
    idleAnimId = null
  }

  // Ball starts inside the tube
  ball = {
    x: tubeX,
    y: TUBE_TOP + TUBE_HEIGHT - BALL_RADIUS,
    vx: 0,
    vy: 0,
    trail: [],
  }

  dropPhase = 'holding'
  holdTimer = 0
  particles = []
  animate()
}

const animate = () => {
  if (!ball) return

  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // === TUBE PENDULUM UPDATE (always swings) ===
  tubeAngle += tubeAngularVel
  tubeAngularVel += -TUBE_FREQ * tubeAngle  // Restoring force
  tubeAngularVel *= TUBE_DAMPING
  // Re-energize pendulum subtly so it never fully stops
  if (Math.abs(tubeAngle) < 0.01 && Math.abs(tubeAngularVel) < 0.001) {
    tubeAngularVel += (Math.random() - 0.5) * 0.005
  }
  tubeX = canvasWidth / 2 + Math.sin(tubeAngle) * canvasWidth * 0.12

  // === DROP PHASE HANDLING ===
  if (dropPhase === 'holding') {
    // Ball sits in tube, moves with it
    ball.x = tubeX
    ball.y = TUBE_TOP + TUBE_HEIGHT - BALL_RADIUS - 2
    holdTimer++
    if (holdTimer > 25) {
      // Release!
      dropPhase = 'releasing'
      ball.vx = tubeAngularVel * canvasWidth * 0.08 // Inherit tube momentum
      ball.vy = 0.5
    }
    draw(ctx)
    animationId = requestAnimationFrame(animate)
    return
  }

  if (dropPhase === 'releasing') {
    // Ball accelerates out of tube bottom
    ball.vy += GRAVITY * 0.8
    ball.x += ball.vx
    ball.y += ball.vy
    if (ball.y > TUBE_TOP + TUBE_HEIGHT + 15) {
      dropPhase = 'falling'
    }
    draw(ctx)
    animationId = requestAnimationFrame(animate)
    return
  }

  // === FALLING PHASE — full physics ===

  // Gravity
  ball.vy += GRAVITY

  // Air friction
  ball.vx *= FRICTION
  ball.vy *= FRICTION

  // Update position
  ball.x += ball.vx
  ball.y += ball.vy

  // Speed limit
  const speed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy)
  if (speed > MAX_SPEED) {
    ball.vx = (ball.vx / speed) * MAX_SPEED
    ball.vy = (ball.vy / speed) * MAX_SPEED
  }

  // Trail
  ball.trail.push({ x: ball.x, y: ball.y, age: 0 })
  if (ball.trail.length > 12) ball.trail.shift()
  for (const t of ball.trail) t.age++

  // === PEG COLLISIONS ===
  for (const peg of pegs) {
    const dx = ball.x - peg.x
    const dy = ball.y - peg.y
    const distSq = dx * dx + dy * dy
    const minDist = peg.radius + BALL_RADIUS
    const minDistSq = minDist * minDist

    if (distSq < minDistSq && distSq > 0.01) {
      const dist = Math.sqrt(distSq)
      const nx = dx / dist
      const ny = dy / dist

      // Separate ball from peg (push out)
      const overlap = minDist - dist
      ball.x += nx * (overlap + 0.5)
      ball.y += ny * (overlap + 0.5)

      // Relative velocity along normal
      const velAlongNormal = ball.vx * nx + ball.vy * ny

      // Only resolve if moving toward peg
      if (velAlongNormal < 0) {
        // Reflect with bounce coefficient
        ball.vx -= (1 + BOUNCE_COEFF) * velAlongNormal * nx
        ball.vy -= (1 + BOUNCE_COEFF) * velAlongNormal * ny

        // Add random horizontal deflection (the key to natural plinko feel)
        const deflection = (Math.random() - 0.5) * 1.8
        ball.vx += deflection

        // Subtle steering toward target (only in bottom 40%)
        const progress = ball.y / canvasHeight
        if (progress > 0.6) {
          const mults = currentMultipliers.value
          const slotWidth = canvasWidth / mults.length
          const targetX = (targetSlot + 0.5) * slotWidth
          const steerForce = (targetX - ball.x) * 0.005 * (progress - 0.6)
          ball.vx += steerForce
        }
      }

      // Peg glow effect
      peg.glowIntensity = 1.0

      // Spawn particles on hit
      const pegRow = Math.round((peg.y - startY) / pegSpacingY)
      const t = pegRow / rowCount.value
      const pr = Math.round(59 + (14 - 59) * t)
      const pg = Math.round(130 + (211 - 130) * t)
      const pb = Math.round(246 + (238 - 246) * t)
      spawnParticles(peg.x, peg.y, `rgb(${pr},${pg},${pb})`, 4)
    }
  }

  // Wall collisions with bounce
  if (ball.x < BALL_RADIUS + 10) {
    ball.x = BALL_RADIUS + 10
    ball.vx = Math.abs(ball.vx) * WALL_BOUNCE
  }
  if (ball.x > canvasWidth - BALL_RADIUS - 10) {
    ball.x = canvasWidth - BALL_RADIUS - 10
    ball.vx = -Math.abs(ball.vx) * WALL_BOUNCE
  }

  // Decay peg glow
  for (const peg of pegs) {
    if (peg.glowIntensity > 0) {
      peg.glowIntensity *= 0.9
      if (peg.glowIntensity < 0.01) peg.glowIntensity = 0
    }
  }

  // Update particles
  updateParticles()

  // Draw everything
  draw(ctx)

  // Check if ball reached bottom slots
  const slotY = canvasHeight - 36
  if (ball.y > slotY) {
    finishGame()
    return
  }

  animationId = requestAnimationFrame(animate)
}

const finishGame = () => {
  if (!ball) return

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

  // Final burst of particles at landing
  const slotCenterX = (finalSlot + 0.5) * slotWidth
  const color = mults[finalSlot] >= 2 ? '#22c55e' : mults[finalSlot] >= 1 ? '#3b82f6' : '#ef4444'
  spawnParticles(slotCenterX, canvasHeight - 30, color, 12)

  showResult.value = true
  ball = null
  isPlaying.value = false
  dropPhase = 'idle'

  // Keep drawing for particle effects, then restart idle
  const fadeOut = () => {
    const canvas = gameCanvas.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Keep pendulum moving during fadeout
    tubeAngle += tubeAngularVel
    tubeAngularVel += -TUBE_FREQ * tubeAngle
    tubeAngularVel *= TUBE_DAMPING
    tubeX = canvasWidth / 2 + Math.sin(tubeAngle) * canvasWidth * 0.12

    updateParticles()
    draw(ctx)
    if (particles.length > 0) {
      animationId = requestAnimationFrame(fadeOut)
    } else {
      // Restart idle animation
      startIdleAnimation()
    }
  }
  fadeOut()

  setTimeout(() => {
    showResult.value = false
    if (autoPlay.value && autoPlayCount.value > 0) {
      autoPlayCount.value--
      if (autoPlayCount.value > 0 && balance.value >= selectedBet.value) {
        playGame()
      }
    }
  }, 1500)
}

const draw = (ctx: CanvasRenderingContext2D) => {
  const w = canvasWidth
  const h = canvasHeight

  // Clear with dark background
  ctx.fillStyle = '#0a0e1a'
  ctx.fillRect(0, 0, w, h)

  // Subtle radial gradient overlay
  const bgGrad = ctx.createRadialGradient(w / 2, h * 0.3, 0, w / 2, h * 0.3, w * 0.8)
  bgGrad.addColorStop(0, 'rgba(59, 130, 246, 0.04)')
  bgGrad.addColorStop(1, 'rgba(0, 0, 0, 0)')
  ctx.fillStyle = bgGrad
  ctx.fillRect(0, 0, w, h)

  // === DRAW TUBE (pendulum dispenser) ===
  const tubeLeft = tubeX - TUBE_WIDTH / 2
  const tubeBottom = TUBE_TOP + TUBE_HEIGHT

  // Tube body — metallic blue gradient
  const tubeGrad = ctx.createLinearGradient(tubeLeft, 0, tubeLeft + TUBE_WIDTH, 0)
  tubeGrad.addColorStop(0, '#1e3a5f')
  tubeGrad.addColorStop(0.2, '#2563eb')
  tubeGrad.addColorStop(0.5, '#3b82f6')
  tubeGrad.addColorStop(0.8, '#2563eb')
  tubeGrad.addColorStop(1, '#1e3a5f')

  ctx.fillStyle = tubeGrad
  ctx.beginPath()
  ctx.roundRect(tubeLeft, TUBE_TOP, TUBE_WIDTH, TUBE_HEIGHT, [6, 6, 4, 4])
  ctx.fill()

  // Tube inner dark channel
  const innerW = TUBE_WIDTH * 0.55
  const innerGrad = ctx.createLinearGradient(tubeX - innerW / 2, 0, tubeX + innerW / 2, 0)
  innerGrad.addColorStop(0, 'rgba(0,0,0,0.5)')
  innerGrad.addColorStop(0.5, 'rgba(0,0,0,0.25)')
  innerGrad.addColorStop(1, 'rgba(0,0,0,0.5)')
  ctx.fillStyle = innerGrad
  ctx.fillRect(tubeX - innerW / 2, TUBE_TOP + 3, innerW, TUBE_HEIGHT - 3)

  // Tube bottom lip (wider, like a funnel exit)
  ctx.fillStyle = '#2563eb'
  ctx.beginPath()
  ctx.roundRect(tubeLeft - 3, tubeBottom - 6, TUBE_WIDTH + 6, 6, [0, 0, 4, 4])
  ctx.fill()

  // Tube highlight line
  ctx.strokeStyle = 'rgba(147, 197, 253, 0.4)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(tubeLeft + 4, TUBE_TOP + 3)
  ctx.lineTo(tubeLeft + 4, tubeBottom - 8)
  ctx.stroke()

  // Tube glow when ball is inside
  if (dropPhase === 'holding' || dropPhase === 'releasing') {
    ctx.save()
    ctx.shadowColor = 'rgba(236, 72, 153, 0.6)'
    ctx.shadowBlur = 15
    ctx.fillStyle = 'rgba(236, 72, 153, 0.15)'
    ctx.beginPath()
    ctx.ellipse(tubeX, tubeBottom, TUBE_WIDTH * 0.6, 6, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }

  // === DRAW PEGS ===
  const rows = rowCount.value
  for (const peg of pegs) {
    const pegRow = Math.round((peg.y - startY) / pegSpacingY)
    const t = Math.min(1, pegRow / (rows - 1))

    // Color gradient from blue → cyan down the rows
    const r = Math.round(59 + (14 - 59) * t)
    const g = Math.round(130 + (211 - 130) * t)
    const b = Math.round(246 + (238 - 246) * t)
    const baseColor = `rgb(${r},${g},${b})`

    // Glow effect when hit
    if (peg.glowIntensity > 0.01) {
      ctx.save()
      ctx.shadowColor = baseColor
      ctx.shadowBlur = 12 * peg.glowIntensity
      ctx.fillStyle = `rgba(${r},${g},${b},${0.3 * peg.glowIntensity})`
      ctx.beginPath()
      ctx.arc(peg.x, peg.y, peg.radius * 3, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()
    }

    // Peg body
    ctx.save()
    ctx.shadowColor = `rgba(${r},${g},${b},0.4)`
    ctx.shadowBlur = 4

    const pegGrad = ctx.createRadialGradient(
      peg.x - peg.radius * 0.3, peg.y - peg.radius * 0.3, 0,
      peg.x, peg.y, peg.radius
    )
    const bright = peg.glowIntensity > 0.1 ? 1.5 : 1
    pegGrad.addColorStop(0, `rgba(${Math.min(255, r * bright + 80)},${Math.min(255, g * bright + 80)},${Math.min(255, b * bright + 80)},1)`)
    pegGrad.addColorStop(1, baseColor)

    ctx.fillStyle = pegGrad
    ctx.beginPath()
    ctx.arc(peg.x, peg.y, peg.radius + peg.glowIntensity * 1.5, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }

  // === DRAW PARTICLES ===
  for (const p of particles) {
    const alpha = 1 - p.life / p.maxLife
    ctx.fillStyle = p.color.replace('rgb', 'rgba').replace(')', `,${alpha * 0.8})`)
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * (1 - p.life / p.maxLife * 0.5), 0, Math.PI * 2)
    ctx.fill()
  }

  // === DRAW BALL ===
  if (ball) {
    // Trail
    for (let i = 0; i < ball.trail.length; i++) {
      const t = ball.trail[i]
      const alpha = (1 - i / ball.trail.length) * 0.4
      const size = BALL_RADIUS * (0.3 + 0.7 * (1 - i / ball.trail.length))
      ctx.fillStyle = `rgba(236, 72, 153, ${alpha})`
      ctx.beginPath()
      ctx.arc(t.x, t.y, size, 0, Math.PI * 2)
      ctx.fill()
    }

    // Ball glow
    ctx.save()
    ctx.shadowColor = 'rgba(236, 72, 153, 0.7)'
    ctx.shadowBlur = 18

    // Ball body with 3D gradient
    const ballGrad = ctx.createRadialGradient(
      ball.x - BALL_RADIUS * 0.3, ball.y - BALL_RADIUS * 0.3, 0,
      ball.x, ball.y, BALL_RADIUS
    )
    ballGrad.addColorStop(0, '#f9a8d4')
    ballGrad.addColorStop(0.4, '#ec4899')
    ballGrad.addColorStop(1, '#be185d')

    ctx.fillStyle = ballGrad
    ctx.beginPath()
    ctx.arc(ball.x, ball.y, BALL_RADIUS, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()

    // Specular highlight
    ctx.fillStyle = 'rgba(255, 255, 255, 0.55)'
    ctx.beginPath()
    ctx.arc(ball.x - BALL_RADIUS * 0.25, ball.y - BALL_RADIUS * 0.3, BALL_RADIUS * 0.35, 0, Math.PI * 2)
    ctx.fill()
  }

  // === DRAW BOTTOM SLOTS ===
  const mults = currentMultipliers.value
  const slotWidth = w / mults.length
  const slotY = h - 36
  const slotH = 34

  mults.forEach((mult: number, i: number) => {
    const x = i * slotWidth + 1
    const sw = slotWidth - 2

    // Color based on multiplier value
    let bgColor: string
    let textColor: string
    if (mult >= 10) {
      bgColor = 'rgba(34, 197, 94, 0.35)'
      textColor = '#4ade80'
    } else if (mult >= 2) {
      bgColor = 'rgba(34, 211, 238, 0.25)'
      textColor = '#22d3ee'
    } else if (mult >= 1) {
      bgColor = 'rgba(99, 102, 241, 0.2)'
      textColor = '#a5b4fc'
    } else {
      bgColor = 'rgba(239, 68, 68, 0.25)'
      textColor = '#f87171'
    }

    // Slot background with rounded top
    ctx.fillStyle = bgColor
    ctx.beginPath()
    const r = 4
    ctx.moveTo(x + r, slotY)
    ctx.lineTo(x + sw - r, slotY)
    ctx.arcTo(x + sw, slotY, x + sw, slotY + r, r)
    ctx.lineTo(x + sw, slotY + slotH)
    ctx.lineTo(x, slotY + slotH)
    ctx.lineTo(x, slotY + r)
    ctx.arcTo(x, slotY, x + r, slotY, r)
    ctx.fill()

    // Multiplier text
    ctx.fillStyle = textColor
    ctx.font = `bold ${mults.length > 13 ? 8 : 10}px -apple-system, sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(`${mult}x`, x + sw / 2, slotY + slotH / 2)
  })

  // Separator lines between slots
  ctx.strokeStyle = 'rgba(255,255,255,0.06)'
  ctx.lineWidth = 1
  for (let i = 1; i < mults.length; i++) {
    const x = i * slotWidth
    ctx.beginPath()
    ctx.moveTo(x, slotY)
    ctx.lineTo(x, slotY + slotH)
    ctx.stroke()
  }
}

const resizeCanvas = () => {
  const canvas = gameCanvas.value
  const container = gameContainer.value
  if (!canvas || !container) return

  const containerWidth = container.clientWidth
  const dpr = window.devicePixelRatio || 1

  canvasWidth = Math.min(containerWidth, 500)
  canvasHeight = Math.round(canvasWidth * 1.3)

  canvas.width = canvasWidth * dpr
  canvas.height = canvasHeight * dpr
  canvas.style.width = canvasWidth + 'px'
  canvas.style.height = canvasHeight + 'px'

  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.scale(dpr, dpr)
  }

  tubeX = canvasWidth / 2
  computePegs()
}

const onRowCountChange = () => {
  computePegs()
  if (gameCanvas.value) {
    const ctx = gameCanvas.value.getContext('2d')
    if (ctx) draw(ctx)
  }
}

watch(riskLevel, () => {
  if (gameCanvas.value && !ball) {
    const ctx = gameCanvas.value.getContext('2d')
    if (ctx) draw(ctx)
  }
})

// Idle animation — tube sways even when no game is active
const startIdleAnimation = () => {
  // Initialize pendulum with small random swing
  tubeAngle = (Math.random() - 0.5) * TUBE_AMPLITUDE
  tubeAngularVel = (Math.random() - 0.5) * 0.008
  tubeX = canvasWidth / 2

  const idleLoop = () => {
    const canvas = gameCanvas.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Update pendulum
    tubeAngle += tubeAngularVel
    tubeAngularVel += -TUBE_FREQ * tubeAngle
    tubeAngularVel *= TUBE_DAMPING
    if (Math.abs(tubeAngle) < 0.01 && Math.abs(tubeAngularVel) < 0.001) {
      tubeAngularVel += (Math.random() - 0.5) * 0.004
    }
    tubeX = canvasWidth / 2 + Math.sin(tubeAngle) * canvasWidth * 0.12

    draw(ctx)
    idleAnimId = requestAnimationFrame(idleLoop)
  }
  idleLoop()
}

onMounted(async () => {
  await nextTick()
  resizeCanvas()
  startIdleAnimation()
  window.addEventListener('resize', resizeCanvas)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (idleAnimId) cancelAnimationFrame(idleAnimId)
  window.removeEventListener('resize', resizeCanvas)
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
  margin-bottom: 8px;
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
  margin: 0 auto;
  max-width: 500px;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  z-index: 10;
  background: #0a0e1a;
}

.game-canvas {
  display: block;
  width: 100%;
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
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  animation: popIn 0.3s ease;
  z-index: 20;
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

/* Bet Section */
.bet-section {
  padding: 12px 16px 0;
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
</style>
