<template>
  <div class="ball-escape-view">
    <!-- Header -->
    <header class="game-header">
      <button class="header-close" @click="$router.back()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
        <span>Закрыть</span>
      </button>
      <div class="game-id">
        <span class="label">Game #{{ gameId }}</span>
      </div>
      <div class="balance-badge">
        <span>{{ balance.toFixed(2) }} ◇</span>
      </div>
    </header>

    <!-- Game Arena -->
    <div class="arena-container">
      <canvas
        ref="gameCanvas"
        class="game-canvas"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>

      <!-- Multiplier overlay (only during play/result) -->
      <div class="multiplier-overlay" :class="gameState">
        <div class="multiplier-value" :style="{ color: multiplierColor }">
          {{ multiplier.toFixed(2) }}x
        </div>
        <div v-if="gameState === 'won'" class="result-text won">ESCAPED!</div>
        <div v-if="gameState === 'lost'" class="result-text lost">DEAD</div>
      </div>
    </div>

    <!-- Hash display -->
    <div class="hash-row">
      <span class="hash-label">Hash:</span>
      <span class="hash-value">{{ serverHash }}</span>
    </div>

    <!-- Bet buttons -->
    <div class="bet-row">
      <button
        v-for="amount in betAmounts"
        :key="amount"
        class="bet-btn"
        :class="{ active: selectedBet === amount }"
        @click="selectBet(amount)"
        :disabled="gameState === 'playing'"
      >
        {{ amount }} ◇
      </button>
    </div>

    <!-- Play button -->
    <div class="action-row">
      <button
        class="play-btn"
        :class="{ playing: gameState === 'playing' }"
        :disabled="gameState === 'playing' || balance < selectedBet"
        @click="startGame"
      >
        <span v-if="gameState === 'idle'">Play {{ selectedBet }} ◇</span>
        <span v-else-if="gameState === 'playing'">{{ multiplier.toFixed(2) }}x</span>
        <span v-else>Play Again</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { escapePlay } from '../api/client'

// Canvas
const gameCanvas = ref<HTMLCanvasElement | null>(null)
const canvasWidth = 340
const canvasHeight = 460 // Taller for floor area + preview

// Game state
const balance = ref(10.0)
const betAmounts = [0.5, 1, 3, 5, 10]
const selectedBet = ref(1)
const gameState = ref<'idle' | 'playing' | 'won' | 'lost'>('idle')
const multiplier = ref(1.0)
const gameId = ref(Math.floor(Math.random() * 900000) + 100000)
const serverHash = ref('---')

// Physics
let animationId: number | null = null
let sphereRotation = 0
let sphereAngularVelocity = 0 // radians per frame
let holeAngle = 0
let ballX = 0
let ballY = 0
let ballVX = 0
let ballVY = 0
const SPHERE_RADIUS = 120
const BALL_RADIUS = 12
const HOLE_SIZE = 0.45 // radians
const GRAVITY = 0.28 // moderate gravity
const BOUNCE = 0.72 // strong bounces — ball keeps energy on hits
const SPRING_FORCE = 1.3 // solid kick off walls
const FRICTION = 0.997 // minimal drag — ball holds inertia long
const CENTRIFUGAL_FACTOR = 0.018 // gentle outward push
const CORIOLIS_FACTOR = 0.035 // subtle deflection
const MAX_SPEED = 11 // headroom for lively movement

// Trail effect
const TRAIL_LENGTH = 16
let ballTrail: { x: number; y: number }[] = []

// Impact flash
let impactFlash = 0 // 0..1 decays each frame
let impactAngle = 0

// Sphere position (centered horizontally, upper area)
const SPHERE_CENTER_X = 170
const SPHERE_CENTER_Y = 150

// Floor area
const FLOOR_Y = 360 // Where the floor starts
const FLOOR_HEIGHT = 80

// Preview idle animation
let idleAnimId: number | null = null
let previewBallAngle = 0
let previewBallSpeed = 0.02

// Ring color — changes per game (like MyBalls: pink preview, random per round)
const RING_COLORS = [
  { main: '#fbbf24', glow: 'rgba(251, 191, 36, ', light: '#fde68a' }, // yellow/gold
  { main: '#22d3ee', glow: 'rgba(34, 211, 238, ', light: '#67e8f9' },  // cyan
  { main: '#a855f7', glow: 'rgba(168, 85, 247, ', light: '#c084fc' },  // purple
  { main: '#4ade80', glow: 'rgba(74, 222, 128, ', light: '#86efac' },  // green
  { main: '#f97316', glow: 'rgba(249, 115, 22, ', light: '#fdba74' },  // orange
]
const PREVIEW_RING = { main: '#ec4899', glow: 'rgba(236, 72, 153, ', light: '#f9a8d4' } // pink
let currentRingColor = PREVIEW_RING

// Constant sphere rotation speed — slower for better gameplay feel
const SPHERE_SPEED = 0.016

// Game phases
let startTime = 0
let gameDuration = 5000
let willEscape = false
let targetMultiplier = 1.0
let isFalling = false // Ball escaped and is falling
let landedSide: 'green' | 'red' | null = null
let bounceCount = 0          // How many times ball bounced off floor/walls after escape
const MAX_BOUNCES = 5        // End game after this many floor bounces
const FLOOR_BOUNCE = 0.55    // Floor elasticity — ball loses energy each bounce
const WALL_BOUNCE_FALL = 0.6 // Wall elasticity during fall
const FALL_GRAVITY = 0.35    // Gravity during fall phase
const FALL_FRICTION = 0.992  // Air drag during fall

const multiplierColor = computed(() => {
  if (gameState.value === 'won') return '#4ade80'
  if (gameState.value === 'lost') return '#ef4444'
  if (multiplier.value >= 2) return '#4ade80'
  return '#22d3ee'
})

function selectBet(amount: number) {
  if (gameState.value !== 'idle') return
  selectedBet.value = amount
}

async function startGame() {
  if (gameState.value === 'playing' || balance.value < selectedBet.value) return

  stopIdleAnimation()

  // Pick random ring color for this round (like MyBalls)
  currentRingColor = RING_COLORS[Math.floor(Math.random() * RING_COLORS.length)]

  balance.value -= selectedBet.value
  gameState.value = 'playing'
  multiplier.value = 1.0
  gameId.value = Math.floor(Math.random() * 900000) + 100000

  // Reset ball near top with strong initial velocity for dynamic start
  const startAngle = -Math.PI / 2 + (Math.random() - 0.5) * 1.2 // near top
  const startDist = 30 + Math.random() * 40
  ballX = Math.cos(startAngle) * startDist
  ballY = Math.sin(startAngle) * startDist
  // Strong initial velocity — ball immediately starts bouncing
  const launchAngle = Math.random() * Math.PI * 2
  const launchSpeed = 4 + Math.random() * 3
  ballVX = Math.cos(launchAngle) * launchSpeed
  ballVY = Math.sin(launchAngle) * launchSpeed + 2 // downward bias
  sphereRotation = 0
  sphereAngularVelocity = SPHERE_SPEED
  holeAngle = Math.random() * Math.PI * 2
  ballTrail = []
  impactFlash = 0
  isFalling = false
  landedSide = null
  bounceCount = 0

  // Get server result
  try {
    const result = await escapePlay({
      amount: selectedBet.value,
      client_seed: Math.random().toString(36).substring(2, 10),
      nonce: Date.now(),
      user_id: 'user'
    })
    willEscape = result.escaped
    gameDuration = result.duration_ms
    targetMultiplier = result.multiplier
    serverHash.value = result.server_seed_hash.slice(0, 6) + '...' + result.server_seed_hash.slice(-4)
  } catch {
    // Fallback random
    willEscape = Math.random() < 0.4
    gameDuration = 4000 + Math.random() * 3000
    targetMultiplier = 1.5 + Math.random() * 3.5
    serverHash.value = Math.random().toString(36).slice(2, 8) + '...'
  }

  startTime = Date.now()
  animationId = requestAnimationFrame(gameLoop)
}

function gameLoop() {
  const elapsed = Date.now() - startTime
  const progress = Math.min(elapsed / gameDuration, 1)

  // Update multiplier
  multiplier.value = 1 + (targetMultiplier - 1) * progress

  // Constant sphere rotation (like MyBalls — no acceleration)
  sphereAngularVelocity = SPHERE_SPEED
  sphereRotation += SPHERE_SPEED
  const currentHoleAngle = holeAngle + sphereRotation

  if (isFalling) {
    // === FALLING PHASE — ball bounces off floor & walls before settling ===
    ballVY += FALL_GRAVITY
    ballVX *= FALL_FRICTION
    ballVY *= FALL_FRICTION

    // Subtle steering toward correct side (only before first floor bounce)
    if (bounceCount === 0) {
      const absoluteX = SPHERE_CENTER_X + ballX
      const targetSide = willEscape ? canvasWidth * 0.25 : canvasWidth * 0.75
      const correction = (targetSide - absoluteX) * 0.004
      ballVX += correction
    }

    ballX += ballVX
    ballY += ballVY

    const absoluteX = SPHERE_CENTER_X + ballX
    const absoluteY = SPHERE_CENTER_Y + ballY

    // --- Floor bounce ---
    if (absoluteY >= FLOOR_Y - BALL_RADIUS) {
      ballY = FLOOR_Y - BALL_RADIUS - SPHERE_CENTER_Y
      ballVY = -Math.abs(ballVY) * FLOOR_BOUNCE
      ballVX *= 0.85 // friction on floor contact
      bounceCount++

      // Update which side the ball is on each floor contact
      landedSide = absoluteX < canvasWidth / 2 ? 'green' : 'red'

      // If ball is barely bouncing or exceeded max bounces — settle
      if (bounceCount >= MAX_BOUNCES || Math.abs(ballVY) < 1.2) {
        ballVY = 0
        ballVX = 0
        const won = landedSide === 'green'
        endGame(won)
        return
      }
    }

    // --- Left wall bounce ---
    if (absoluteX <= BALL_RADIUS) {
      ballX = BALL_RADIUS - SPHERE_CENTER_X
      ballVX = Math.abs(ballVX) * WALL_BOUNCE_FALL
    }

    // --- Right wall bounce ---
    if (absoluteX >= canvasWidth - BALL_RADIUS) {
      ballX = canvasWidth - BALL_RADIUS - SPHERE_CENTER_X
      ballVX = -Math.abs(ballVX) * WALL_BOUNCE_FALL
    }

    // --- Bounce off sphere exterior (ball can hit ring from outside) ---
    const distFromCenter = Math.sqrt(ballX * ballX + ballY * ballY)
    if (distFromCenter < SPHERE_RADIUS + BALL_RADIUS + 5 && ballY < 0) {
      // Push ball away from sphere
      const pushAngle = Math.atan2(ballY, ballX)
      const pushDist = SPHERE_RADIUS + BALL_RADIUS + 6
      ballX = Math.cos(pushAngle) * pushDist
      ballY = Math.sin(pushAngle) * pushDist
      // Reflect velocity outward
      const nx = Math.cos(pushAngle)
      const ny = Math.sin(pushAngle)
      const dot = ballVX * nx + ballVY * ny
      if (dot < 0) {
        ballVX -= 2 * dot * nx * 0.5
        ballVY -= 2 * dot * ny * 0.5
      }
    }

    // Update trail
    ballTrail.unshift({ x: SPHERE_CENTER_X + ballX, y: SPHERE_CENTER_Y + ballY })
    if (ballTrail.length > TRAIL_LENGTH) {
      ballTrail.pop()
    }

    draw()
    animationId = requestAnimationFrame(gameLoop)
    return
  }

  // === INSIDE SPHERE PHASE ===
  const dist = Math.sqrt(ballX * ballX + ballY * ballY)

  // === CENTRIFUGAL FORCE (rotating frame pushes ball outward) ===
  if (dist > 1) {
    const omega2 = sphereAngularVelocity * sphereAngularVelocity
    const centrifugalMag = CENTRIFUGAL_FACTOR * omega2 * dist
    ballVX += (ballX / dist) * centrifugalMag
    ballVY += (ballY / dist) * centrifugalMag
  }

  // === CORIOLIS EFFECT (deflects ball sideways in rotating frame) ===
  const cStr = CORIOLIS_FACTOR * sphereAngularVelocity
  ballVX += -ballVY * cStr
  ballVY += ballVX * cStr

  // === GRAVITY ===
  ballVY += GRAVITY

  // === FRICTION (very light — ball stays energetic) ===
  ballVX *= FRICTION
  ballVY *= FRICTION

  // === SPEED LIMIT ===
  const speed = Math.sqrt(ballVX * ballVX + ballVY * ballVY)
  if (speed > MAX_SPEED) {
    ballVX = (ballVX / speed) * MAX_SPEED
    ballVY = (ballVY / speed) * MAX_SPEED
  }

  // Update position
  ballX += ballVX
  ballY += ballVY

  // Update trail
  ballTrail.unshift({ x: ballX, y: ballY })
  if (ballTrail.length > TRAIL_LENGTH) {
    ballTrail.pop()
  }

  // === Decay impact flash ===
  impactFlash *= 0.88

  // === WALL COLLISION (springy bounce) ===
  const maxDist = SPHERE_RADIUS - BALL_RADIUS
  const newDist = Math.sqrt(ballX * ballX + ballY * ballY)

  if (newDist > maxDist) {
    const angle = Math.atan2(ballY, ballX)

    // Check if near hole
    const angleDiff = Math.abs(normalizeAngle(angle - currentHoleAngle))
    const nearHole = angleDiff < HOLE_SIZE / 2

    // Ball escapes through hole
    if (nearHole && newDist > maxDist - 5) {
      isFalling = true
      ballTrail = []

      // Give ball outward velocity through the hole — enough to fly visibly
      ballVX = Math.cos(angle) * 6
      ballVY = Math.sin(angle) * 5 + 3

      draw()
      animationId = requestAnimationFrame(gameLoop)
      return
    }

    // === SPRING BOUNCE off sphere wall ===
    // Push ball back inside
    ballX = Math.cos(angle) * maxDist
    ballY = Math.sin(angle) * maxDist

    // Normal vector (pointing inward)
    const nx = Math.cos(angle)
    const ny = Math.sin(angle)

    // Radial velocity (outward component)
    const vDotN = ballVX * nx + ballVY * ny

    if (vDotN > 0) {
      // Reflect velocity
      ballVX -= 2 * vDotN * nx
      ballVY -= 2 * vDotN * ny

      // Apply bounce coefficient (elastic)
      ballVX *= BOUNCE
      ballVY *= BOUNCE

      // === SPRING PUSH: extra kick away from wall ===
      const springKick = SPRING_FORCE + Math.abs(vDotN) * 0.3
      ballVX -= nx * springKick
      ballVY -= ny * springKick

      // === WALL FRICTION: rotating wall imparts tangential velocity ===
      const tangentX = -ny
      const tangentY = nx
      const wallTangentSpeed = sphereAngularVelocity * SPHERE_RADIUS * 0.5
      ballVX += tangentX * wallTangentSpeed
      ballVY += tangentY * wallTangentSpeed

      // === RANDOMIZED DEFLECTION for unpredictability ===
      const deflection = (Math.random() - 0.5) * 2.5
      ballVX += tangentX * deflection
      ballVY += tangentY * deflection

      // Trigger impact flash
      impactFlash = 1.0
      impactAngle = angle
    }
  }

  // Time's up - force escape
  if (progress >= 1 && !isFalling) {
    // Force ball to escape towards correct side based on server result
    isFalling = true
    ballTrail = []

    const targetX = willEscape ? -60 : 60 // Left for win, right for lose
    ballX = 0
    ballY = SPHERE_RADIUS // At bottom of sphere
    ballVX = targetX / 25 // Velocity towards correct side
    ballVY = 2
  }

  draw()
  animationId = requestAnimationFrame(gameLoop)
}

function endGame(escaped: boolean) {
  if (animationId) cancelAnimationFrame(animationId)

  multiplier.value = targetMultiplier

  if (escaped) {
    gameState.value = 'won'
    balance.value += selectedBet.value * targetMultiplier
  } else {
    gameState.value = 'lost'
  }

  draw()

  // Reset after delay, restart idle animation
  setTimeout(() => {
    gameState.value = 'idle'
    multiplier.value = 1.0
    landedSide = null
    startIdleAnimation()
  }, 2500)
}

function normalizeAngle(angle: number): number {
  while (angle > Math.PI) angle -= Math.PI * 2
  while (angle < -Math.PI) angle += Math.PI * 2
  return angle
}

function draw() {
  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const cx = SPHERE_CENTER_X
  const cy = SPHERE_CENTER_Y

  // Clear
  ctx.fillStyle = '#0a0c14'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  // === FLOOR with upward glow (MyBalls style) ===
  const floorMidY = FLOOR_Y + FLOOR_HEIGHT / 2

  // Green side — upward glow
  const greenGlow = ctx.createLinearGradient(0, FLOOR_Y - 60, 0, FLOOR_Y + FLOOR_HEIGHT)
  greenGlow.addColorStop(0, 'rgba(34, 197, 94, 0)')
  greenGlow.addColorStop(0.3, 'rgba(34, 197, 94, 0.08)')
  greenGlow.addColorStop(0.6, 'rgba(34, 197, 94, 0.25)')
  greenGlow.addColorStop(1, 'rgba(34, 197, 94, 0.5)')
  ctx.fillStyle = greenGlow
  ctx.fillRect(0, FLOOR_Y - 60, canvasWidth / 2, FLOOR_HEIGHT + 60)

  // Red side — upward glow
  const redGlow = ctx.createLinearGradient(0, FLOOR_Y - 60, 0, FLOOR_Y + FLOOR_HEIGHT)
  redGlow.addColorStop(0, 'rgba(239, 68, 68, 0)')
  redGlow.addColorStop(0.3, 'rgba(239, 68, 68, 0.08)')
  redGlow.addColorStop(0.6, 'rgba(239, 68, 68, 0.25)')
  redGlow.addColorStop(1, 'rgba(239, 68, 68, 0.5)')
  ctx.fillStyle = redGlow
  ctx.fillRect(canvasWidth / 2, FLOOR_Y - 60, canvasWidth / 2, FLOOR_HEIGHT + 60)

  // Solid floor base
  ctx.fillStyle = 'rgba(34, 197, 94, 0.6)'
  ctx.fillRect(0, FLOOR_Y + 10, canvasWidth / 2, FLOOR_HEIGHT - 10)
  ctx.fillStyle = 'rgba(239, 68, 68, 0.6)'
  ctx.fillRect(canvasWidth / 2, FLOOR_Y + 10, canvasWidth / 2, FLOOR_HEIGHT - 10)

  // Floor divider — glowing white line
  ctx.save()
  ctx.shadowColor = 'rgba(255, 255, 255, 0.5)'
  ctx.shadowBlur = 8
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(canvasWidth / 2, FLOOR_Y - 30)
  ctx.lineTo(canvasWidth / 2, FLOOR_Y + FLOOR_HEIGHT)
  ctx.stroke()
  ctx.restore()

  // Floor emojis
  ctx.font = '28px -apple-system, sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  // Green side emojis (win)
  const greenCx = canvasWidth / 4
  const greenActive = landedSide === 'green'
  ctx.globalAlpha = greenActive ? 1.0 : 0.7
  ctx.fillText('👑', greenCx - 18, floorMidY + 8)
  ctx.fillText('💎', greenCx + 18, floorMidY + 8)
  ctx.globalAlpha = 1.0

  // Red side emojis (lose)
  const redCx = canvasWidth * 3 / 4
  const redActive = landedSide === 'red'
  ctx.globalAlpha = redActive ? 1.0 : 0.7
  ctx.fillText('💀', redCx - 18, floorMidY + 8)
  ctx.fillText('☠️', redCx + 18, floorMidY + 8)
  ctx.globalAlpha = 1.0

  // === SPHERE (dynamic ring color like MyBalls) ===
  const currentHoleAngle = holeAngle + sphereRotation
  const rc = currentRingColor // shorthand

  // Outer glow — ring color
  const gradient = ctx.createRadialGradient(cx, cy, SPHERE_RADIUS - 20, cx, cy, SPHERE_RADIUS + 15)
  gradient.addColorStop(0, rc.glow + '0.0)')
  gradient.addColorStop(0.6, rc.glow + '0.12)')
  gradient.addColorStop(1, rc.glow + '0.0)')
  ctx.fillStyle = gradient
  ctx.beginPath()
  ctx.arc(cx, cy, SPHERE_RADIUS + 15, 0, Math.PI * 2)
  ctx.fill()

  // Sphere ring — thick, just a gap for the hole
  const holeStart = currentHoleAngle - HOLE_SIZE / 2
  const holeEnd = currentHoleAngle + HOLE_SIZE / 2

  ctx.save()
  ctx.lineWidth = 10
  ctx.lineCap = 'round'

  // Ring gradient using current color
  const ringGrad = ctx.createLinearGradient(cx - SPHERE_RADIUS, cy - SPHERE_RADIUS, cx + SPHERE_RADIUS, cy + SPHERE_RADIUS)
  ringGrad.addColorStop(0, rc.main)
  ringGrad.addColorStop(0.3, rc.light)
  ringGrad.addColorStop(0.5, rc.main)
  ringGrad.addColorStop(0.8, rc.main)
  ringGrad.addColorStop(1, rc.light)
  ctx.strokeStyle = ringGrad

  ctx.shadowColor = rc.glow + '0.5)'
  ctx.shadowBlur = 12

  ctx.beginPath()
  ctx.arc(cx, cy, SPHERE_RADIUS, holeEnd, holeStart + Math.PI * 2)
  ctx.stroke()
  ctx.restore()

  // === IMPACT FLASH on wall ===
  if (impactFlash > 0.05 && gameState.value === 'playing' && !isFalling) {
    const flashX = cx + Math.cos(impactAngle) * SPHERE_RADIUS
    const flashY = cy + Math.sin(impactAngle) * SPHERE_RADIUS
    const flashGlow = ctx.createRadialGradient(flashX, flashY, 0, flashX, flashY, 30 * impactFlash)
    flashGlow.addColorStop(0, rc.glow + `${impactFlash * 0.8})`)
    flashGlow.addColorStop(0.5, rc.glow + `${impactFlash * 0.4})`)
    flashGlow.addColorStop(1, rc.glow + '0)')
    ctx.fillStyle = flashGlow
    ctx.beginPath()
    ctx.arc(flashX, flashY, 30 * impactFlash, 0, Math.PI * 2)
    ctx.fill()
  }

  // Inner sphere subtle fill
  const innerGradient = ctx.createRadialGradient(cx - 30, cy - 30, 0, cx, cy, SPHERE_RADIUS)
  innerGradient.addColorStop(0, rc.glow + '0.05)')
  innerGradient.addColorStop(0.5, rc.glow + '0.02)')
  innerGradient.addColorStop(1, 'rgba(0, 0, 0, 0)')
  ctx.fillStyle = innerGradient
  ctx.beginPath()
  ctx.arc(cx, cy, SPHERE_RADIUS - 10, 0, Math.PI * 2)
  ctx.fill()

  // === BALL TRAIL (brighter when fast) ===
  if (ballTrail.length > 1 && gameState.value === 'playing') {
    const ballSpeed = Math.sqrt(ballVX * ballVX + ballVY * ballVY)
    const trailIntensity = Math.min(ballSpeed / 8, 1)

    for (let i = 1; i < ballTrail.length; i++) {
      const alpha = (1 - i / TRAIL_LENGTH) * (0.3 + trailIntensity * 0.5)
      const radius = BALL_RADIUS * (1 - i / TRAIL_LENGTH * 0.7)

      ctx.fillStyle = `rgba(34, 211, 238, ${alpha})`
      ctx.beginPath()
      const trailX = isFalling ? ballTrail[i].x : cx + ballTrail[i].x
      const trailY = isFalling ? ballTrail[i].y : cy + ballTrail[i].y
      ctx.arc(trailX, trailY, radius, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // === BALL ===
  let ballScreenX: number, ballScreenY: number
  if (isFalling) {
    ballScreenX = SPHERE_CENTER_X + ballX
    ballScreenY = SPHERE_CENTER_Y + ballY
  } else {
    ballScreenX = cx + ballX
    ballScreenY = cy + ballY
  }

  // Ball shadow/glow (stronger when bouncing fast)
  const currentSpeed = Math.sqrt(ballVX * ballVX + ballVY * ballVY)
  const glowStrength = Math.min(0.4 + currentSpeed / 10, 1.0)
  ctx.shadowColor = gameState.value === 'won' ? `rgba(74, 222, 128, ${glowStrength})` :
                    gameState.value === 'lost' ? `rgba(239, 68, 68, ${glowStrength})` :
                    `rgba(34, 211, 238, ${glowStrength})`
  ctx.shadowBlur = 10 + currentSpeed * 2

  // Ball gradient
  const ballGradient = ctx.createRadialGradient(
    ballScreenX - 3, ballScreenY - 3, 0,
    ballScreenX, ballScreenY, BALL_RADIUS
  )

  if (gameState.value === 'won') {
    ballGradient.addColorStop(0, '#86efac')
    ballGradient.addColorStop(1, '#22c55e')
  } else if (gameState.value === 'lost') {
    ballGradient.addColorStop(0, '#fca5a5')
    ballGradient.addColorStop(1, '#ef4444')
  } else {
    ballGradient.addColorStop(0, '#67e8f9')
    ballGradient.addColorStop(1, '#06b6d4')
  }

  ctx.fillStyle = ballGradient
  ctx.beginPath()
  ctx.arc(ballScreenX, ballScreenY, BALL_RADIUS, 0, Math.PI * 2)
  ctx.fill()

  // Ball highlight
  ctx.shadowBlur = 0
  ctx.fillStyle = 'rgba(255, 255, 255, 0.4)'
  ctx.beginPath()
  ctx.arc(ballScreenX - 3, ballScreenY - 3, BALL_RADIUS * 0.3, 0, Math.PI * 2)
  ctx.fill()

  // === IDLE/PREVIEW STATE ===
  if (gameState.value === 'idle') {
    // "This is Preview" text below the sphere
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.font = 'bold 18px -apple-system, sans-serif'
    ctx.fillText('This is Preview', cx, cy + SPHERE_RADIUS + 30)

    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)'
    ctx.font = '13px -apple-system, sans-serif'
    ctx.fillText('Tap button below to play', cx, cy + SPHERE_RADIUS + 52)
  }
}

function startIdleAnimation() {
  // In idle, ball gently floats inside the sphere
  currentRingColor = PREVIEW_RING // pink ring for preview
  previewBallAngle = Math.random() * Math.PI * 2
  previewBallSpeed = 0.015
  sphereRotation = 0
  sphereAngularVelocity = SPHERE_SPEED // same constant speed
  holeAngle = Math.PI * 0.7 // hole visible

  const idleLoop = () => {
    // Gentle orbit
    previewBallAngle += previewBallSpeed
    const orbitRadius = SPHERE_RADIUS * 0.4
    ballX = Math.cos(previewBallAngle) * orbitRadius
    ballY = Math.sin(previewBallAngle) * orbitRadius * 0.6 + 15 // slight downward offset
    ballVX = 0
    ballVY = 0

    // Constant sphere rotation
    sphereRotation += SPHERE_SPEED

    draw()
    idleAnimId = requestAnimationFrame(idleLoop)
  }
  idleLoop()
}

function stopIdleAnimation() {
  if (idleAnimId) {
    cancelAnimationFrame(idleAnimId)
    idleAnimId = null
  }
}

onMounted(() => {
  startIdleAnimation()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  stopIdleAnimation()
})
</script>

<style scoped>
.ball-escape-view {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0c14 0%, #0f1219 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding-bottom: 100px;
}

.game-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}

.header-close {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: #fff;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 13px;
}

.game-id {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.balance-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.arena-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 20px;
}

.game-canvas {
  border-radius: 24px;
}

.multiplier-overlay {
  position: absolute;
  top: 38%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s;
}

.multiplier-overlay.playing,
.multiplier-overlay.won,
.multiplier-overlay.lost {
  opacity: 1;
}

.multiplier-value {
  font-size: 42px;
  font-weight: 800;
  text-shadow: 0 0 30px currentColor, 0 0 60px currentColor;
}

.result-text {
  font-size: 16px;
  font-weight: 700;
  margin-top: 4px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.result-text.won {
  color: #4ade80;
  text-shadow: 0 0 15px rgba(74, 222, 128, 0.6);
}

.result-text.lost {
  color: #ef4444;
  text-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
}

.hash-row {
  text-align: center;
  padding: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
}

.hash-label {
  margin-right: 4px;
}

.hash-value {
  font-family: monospace;
}

.bet-row {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  margin-bottom: 12px;
}

.bet-btn {
  flex: 1;
  padding: 10px 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid transparent;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.bet-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bet-btn.active {
  background: rgba(34, 211, 238, 0.15);
  border-color: rgba(34, 211, 238, 0.4);
  color: #22d3ee;
}

.action-row {
  padding: 0 16px;
}

.play-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border: none;
  border-radius: 16px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.play-btn.playing {
  background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 100%);
}

.play-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
}
</style>
