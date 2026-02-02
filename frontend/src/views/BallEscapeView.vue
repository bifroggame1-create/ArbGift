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

      <!-- Multiplier overlay -->
      <div class="multiplier-overlay" :class="gameState">
        <div class="multiplier-value" :style="{ color: multiplierColor }">
          {{ multiplier.toFixed(2) }}x
        </div>
        <div v-if="gameState === 'won'" class="result-text won">ESCAPED! 🎉</div>
        <div v-if="gameState === 'lost'" class="result-text lost">CAUGHT! 💀</div>
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
const canvasWidth = 320
const canvasHeight = 420 // Taller for floor area

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
const GRAVITY = 0.12
const BOUNCE = 0.65 // inelastic collisions
const FRICTION = 0.992
const CENTRIFUGAL_FACTOR = 0.008 // centrifugal force strength
const CORIOLIS_FACTOR = 0.02 // Coriolis deflection

// Trail effect
const TRAIL_LENGTH = 12
let ballTrail: { x: number; y: number }[] = []

// Sphere position (centered horizontally, upper area)
const SPHERE_CENTER_X = 160
const SPHERE_CENTER_Y = 140

// Floor area
const FLOOR_Y = 340 // Where the floor starts
const FLOOR_HEIGHT = 60

// Game phases
let startTime = 0
let gameDuration = 5000
let willEscape = false
let targetMultiplier = 1.0
let isFalling = false // Ball escaped and is falling
let landedSide: 'green' | 'red' | null = null

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

  balance.value -= selectedBet.value
  gameState.value = 'playing'
  multiplier.value = 1.0
  gameId.value = Math.floor(Math.random() * 900000) + 100000

  // Reset ball slightly off-center for initial motion
  const startAngle = Math.random() * Math.PI * 2
  const startDist = 20 + Math.random() * 30
  ballX = Math.cos(startAngle) * startDist
  ballY = Math.sin(startAngle) * startDist
  ballVX = (Math.random() - 0.5) * 2
  ballVY = (Math.random() - 0.5) * 2 + 1 // slight downward bias
  sphereRotation = 0
  sphereAngularVelocity = 0.02
  holeAngle = Math.random() * Math.PI * 2
  ballTrail = []
  isFalling = false
  landedSide = null

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

  // Keep sphere rotating
  sphereAngularVelocity = 0.02 + progress * 0.025
  sphereRotation += sphereAngularVelocity
  const currentHoleAngle = holeAngle + sphereRotation

  if (isFalling) {
    // === FALLING PHASE ===
    ballVY += 0.4 // gravity
    ballVX *= 0.99 // air resistance

    // Subtle correction to guide ball to correct side (server result)
    const absoluteX = SPHERE_CENTER_X + ballX
    const targetSide = willEscape ? canvasWidth * 0.25 : canvasWidth * 0.75
    const correction = (targetSide - absoluteX) * 0.003
    ballVX += correction

    ballX += ballVX
    ballY += ballVY

    // Update trail
    ballTrail.unshift({ x: SPHERE_CENTER_X + ballX, y: SPHERE_CENTER_Y + ballY })
    if (ballTrail.length > TRAIL_LENGTH) {
      ballTrail.pop()
    }

    // Check if landed on floor
    const absoluteY = SPHERE_CENTER_Y + ballY
    if (absoluteY >= FLOOR_Y - BALL_RADIUS) {
      // Landed!
      const finalX = SPHERE_CENTER_X + ballX
      landedSide = finalX < canvasWidth / 2 ? 'green' : 'red'

      // Stop ball on floor
      ballY = FLOOR_Y - BALL_RADIUS - SPHERE_CENTER_Y
      ballVY = 0
      ballVX = 0

      // End game based on where it landed
      const won = landedSide === 'green'
      endGame(won)
      return
    }

    draw()
    animationId = requestAnimationFrame(gameLoop)
    return
  }

  // === INSIDE SPHERE PHASE ===
  const dist = Math.sqrt(ballX * ballX + ballY * ballY)

  // === CENTRIFUGAL FORCE ===
  if (dist > 0.1) {
    const centrifugalMagnitude = CENTRIFUGAL_FACTOR * sphereAngularVelocity * sphereAngularVelocity * dist
    const outwardX = (ballX / dist) * centrifugalMagnitude
    const outwardY = (ballY / dist) * centrifugalMagnitude
    ballVX += outwardX
    ballVY += outwardY
  }

  // === CORIOLIS EFFECT ===
  const coriolisStrength = CORIOLIS_FACTOR * sphereAngularVelocity
  const coriolisX = -ballVY * coriolisStrength
  const coriolisY = ballVX * coriolisStrength
  ballVX += coriolisX
  ballVY += coriolisY

  // === GRAVITY ===
  ballVY += GRAVITY

  // === FRICTION ===
  ballVX *= FRICTION
  ballVY *= FRICTION

  // Update position
  ballX += ballVX
  ballY += ballVY

  // Update trail
  ballTrail.unshift({ x: ballX, y: ballY })
  if (ballTrail.length > TRAIL_LENGTH) {
    ballTrail.pop()
  }

  // === WALL COLLISION ===
  const maxDist = SPHERE_RADIUS - BALL_RADIUS

  if (dist > maxDist) {
    const angle = Math.atan2(ballY, ballX)

    // Check if near hole
    const angleDiff = Math.abs(normalizeAngle(angle - currentHoleAngle))
    const nearHole = angleDiff < HOLE_SIZE / 2

    // Ball escapes through hole
    if (nearHole && dist > maxDist - 5) {
      // Escape! Start falling phase
      isFalling = true
      ballTrail = [] // Clear trail for fresh absolute tracking

      // Give ball some outward velocity
      ballVX = Math.cos(angle) * 3
      ballVY = Math.sin(angle) * 3 + 2 // slight downward boost

      draw()
      animationId = requestAnimationFrame(gameLoop)
      return
    }

    // Inelastic bounce off sphere wall
    ballX = Math.cos(angle) * maxDist
    ballY = Math.sin(angle) * maxDist

    // Reflect velocity with energy loss
    const nx = Math.cos(angle)
    const ny = Math.sin(angle)
    const dot = ballVX * nx + ballVY * ny

    // Only bounce if moving outward
    if (dot > 0) {
      ballVX = (ballVX - 2 * dot * nx) * BOUNCE
      ballVY = (ballVY - 2 * dot * ny) * BOUNCE

      // Wall imparts some rotational velocity
      const tangentX = -ny
      const tangentY = nx
      const wallSpeed = sphereAngularVelocity * dist * 0.3
      ballVX += tangentX * wallSpeed
      ballVY += tangentY * wallSpeed

      // Add chaos at high speeds
      const chaosLevel = sphereAngularVelocity * 8
      ballVX += (Math.random() - 0.5) * chaosLevel
      ballVY += (Math.random() - 0.5) * chaosLevel
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

  // Reset after delay
  setTimeout(() => {
    gameState.value = 'idle'
    multiplier.value = 1.0
    draw()
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

  // === FLOOR (Green/Red halves) ===
  // Green left half (WIN)
  const floorGradientGreen = ctx.createLinearGradient(0, FLOOR_Y, 0, FLOOR_Y + FLOOR_HEIGHT)
  floorGradientGreen.addColorStop(0, 'rgba(34, 197, 94, 0.4)')
  floorGradientGreen.addColorStop(1, 'rgba(34, 197, 94, 0.2)')
  ctx.fillStyle = floorGradientGreen
  ctx.fillRect(0, FLOOR_Y, canvasWidth / 2, FLOOR_HEIGHT)

  // Red right half (LOSE)
  const floorGradientRed = ctx.createLinearGradient(0, FLOOR_Y, 0, FLOOR_Y + FLOOR_HEIGHT)
  floorGradientRed.addColorStop(0, 'rgba(239, 68, 68, 0.4)')
  floorGradientRed.addColorStop(1, 'rgba(239, 68, 68, 0.2)')
  ctx.fillStyle = floorGradientRed
  ctx.fillRect(canvasWidth / 2, FLOOR_Y, canvasWidth / 2, FLOOR_HEIGHT)

  // Floor divider line
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(canvasWidth / 2, FLOOR_Y)
  ctx.lineTo(canvasWidth / 2, FLOOR_Y + FLOOR_HEIGHT)
  ctx.stroke()

  // Floor top edge
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(0, FLOOR_Y)
  ctx.lineTo(canvasWidth, FLOOR_Y)
  ctx.stroke()

  // Floor labels
  ctx.font = 'bold 14px -apple-system, sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = landedSide === 'green' ? '#4ade80' : 'rgba(74, 222, 128, 0.6)'
  ctx.fillText('WIN', canvasWidth / 4, FLOOR_Y + FLOOR_HEIGHT / 2)
  ctx.fillStyle = landedSide === 'red' ? '#ef4444' : 'rgba(239, 68, 68, 0.6)'
  ctx.fillText('LOSE', canvasWidth * 3 / 4, FLOOR_Y + FLOOR_HEIGHT / 2)

  // === SPHERE ===
  const currentHoleAngle = holeAngle + sphereRotation

  // Outer glow
  const gradient = ctx.createRadialGradient(cx, cy, SPHERE_RADIUS - 20, cx, cy, SPHERE_RADIUS + 10)
  gradient.addColorStop(0, 'rgba(139, 92, 246, 0.0)')
  gradient.addColorStop(0.7, 'rgba(139, 92, 246, 0.15)')
  gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)')
  ctx.fillStyle = gradient
  ctx.beginPath()
  ctx.arc(cx, cy, SPHERE_RADIUS + 10, 0, Math.PI * 2)
  ctx.fill()

  // Sphere ring with hole
  ctx.strokeStyle = 'rgba(139, 92, 246, 0.6)'
  ctx.lineWidth = 8
  ctx.lineCap = 'round'

  const holeStart = currentHoleAngle - HOLE_SIZE / 2
  const holeEnd = currentHoleAngle + HOLE_SIZE / 2

  ctx.beginPath()
  ctx.arc(cx, cy, SPHERE_RADIUS, holeEnd, holeStart + Math.PI * 2)
  ctx.stroke()

  // Hole glow effect
  const holeX = cx + Math.cos(currentHoleAngle) * SPHERE_RADIUS
  const holeY = cy + Math.sin(currentHoleAngle) * SPHERE_RADIUS
  const holeGlow = ctx.createRadialGradient(holeX, holeY, 0, holeX, holeY, 35)
  const pulseAlpha = 0.3 + Math.sin(Date.now() / 200) * 0.15
  holeGlow.addColorStop(0, `rgba(251, 191, 36, ${pulseAlpha})`)
  holeGlow.addColorStop(1, 'rgba(251, 191, 36, 0)')
  ctx.fillStyle = holeGlow
  ctx.beginPath()
  ctx.arc(holeX, holeY, 35, 0, Math.PI * 2)
  ctx.fill()

  // Hole indicator arc
  ctx.strokeStyle = '#fbbf24'
  ctx.lineWidth = 4
  ctx.beginPath()
  ctx.arc(cx, cy, SPHERE_RADIUS + 6, holeStart, holeEnd)
  ctx.stroke()

  // Rotation arrows
  if (gameState.value === 'playing' && !isFalling) {
    const arrowCount = 4
    for (let i = 0; i < arrowCount; i++) {
      const arrowAngle = sphereRotation + (i * Math.PI * 2) / arrowCount
      const arrowX = cx + Math.cos(arrowAngle) * (SPHERE_RADIUS - 15)
      const arrowY = cy + Math.sin(arrowAngle) * (SPHERE_RADIUS - 15)

      ctx.save()
      ctx.translate(arrowX, arrowY)
      ctx.rotate(arrowAngle + Math.PI / 2)
      ctx.fillStyle = `rgba(139, 92, 246, ${0.3 + sphereAngularVelocity * 5})`
      ctx.beginPath()
      ctx.moveTo(0, -6)
      ctx.lineTo(4, 2)
      ctx.lineTo(-4, 2)
      ctx.closePath()
      ctx.fill()
      ctx.restore()
    }
  }

  // Inner sphere effect
  const innerGradient = ctx.createRadialGradient(cx - 30, cy - 30, 0, cx, cy, SPHERE_RADIUS)
  innerGradient.addColorStop(0, 'rgba(139, 92, 246, 0.1)')
  innerGradient.addColorStop(0.5, 'rgba(139, 92, 246, 0.03)')
  innerGradient.addColorStop(1, 'rgba(0, 0, 0, 0)')
  ctx.fillStyle = innerGradient
  ctx.beginPath()
  ctx.arc(cx, cy, SPHERE_RADIUS - 10, 0, Math.PI * 2)
  ctx.fill()

  // === BALL TRAIL ===
  if (ballTrail.length > 1 && gameState.value === 'playing') {
    for (let i = 1; i < ballTrail.length; i++) {
      const alpha = 1 - i / TRAIL_LENGTH
      const radius = BALL_RADIUS * (1 - i / TRAIL_LENGTH * 0.7)

      ctx.fillStyle = `rgba(34, 211, 238, ${alpha * 0.4})`
      ctx.beginPath()
      // Trail stored as absolute during falling, relative during inside sphere
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

  // Ball shadow/glow
  ctx.shadowColor = gameState.value === 'won' ? 'rgba(74, 222, 128, 0.6)' :
                    gameState.value === 'lost' ? 'rgba(239, 68, 68, 0.6)' :
                    'rgba(34, 211, 238, 0.6)'
  ctx.shadowBlur = 15

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

  // === IDLE STATE TEXT ===
  if (gameState.value === 'idle') {
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)'
    ctx.font = '13px -apple-system, sans-serif'
    ctx.fillText('Шарик вылетает через дырку', cx, cy - 10)
    ctx.fillText('Падает на зелёное = WIN', cx, cy + 10)
  }
}

onMounted(() => {
  draw()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
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
  top: 50%;
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
  font-size: 48px;
  font-weight: 700;
  text-shadow: 0 0 20px currentColor;
}

.result-text {
  font-size: 18px;
  font-weight: 600;
  margin-top: 8px;
}

.result-text.won {
  color: #4ade80;
}

.result-text.lost {
  color: #ef4444;
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
