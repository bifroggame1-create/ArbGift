<template>
  <div class="plinko-view min-h-screen flex flex-col" style="background: linear-gradient(180deg, #0d1f2d 0%, #0a2a3a 50%, #072630 100%);">
    <!-- Top Bar -->
    <div class="flex items-center justify-between px-4 pt-3 pb-2">
      <button @click="router.back()" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex items-center gap-2">
        <span class="text-white/50 text-xs">💎</span>
        <span class="text-white font-bold text-sm">{{ balance.toFixed(2) }}</span>
      </div>
      <button class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white text-lg">+</button>
    </div>

    <!-- Game Canvas Area -->
    <div class="flex-1 relative mx-3 rounded-2xl overflow-hidden" style="background: linear-gradient(180deg, #0f2a3d 0%, #0a2535 100%); min-height: 340px;">
      <canvas
        ref="gameCanvas"
        class="w-full h-full"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>
    </div>

    <!-- Bottom Controls -->
    <div class="px-4 py-3">
      <!-- Bet Amounts -->
      <div class="flex gap-2 mb-3">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          @click="selectBet(amount)"
          class="flex-1 py-2 rounded-lg text-sm font-bold transition-all"
          :class="selectedBet === amount
            ? 'bg-cyan-500 text-white'
            : 'bg-white/8 text-white/60 hover:bg-white/12'"
        >
          {{ amount }} 💎
        </button>
      </div>

      <!-- Action Row -->
      <div class="flex items-center gap-2">
        <!-- Swap -->
        <button class="flex items-center gap-1 px-3 py-2 rounded-lg bg-white/8 text-white/60 text-xs">
          💎 ☆
        </button>

        <!-- Play Button -->
        <button
          @click="playGame"
          :disabled="isPlaying || balance < selectedBet"
          class="flex-1 py-3 rounded-xl font-bold text-base transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style="background: linear-gradient(135deg, #22d3ee, #06b6d4);"
        >
          <span class="text-white">Play 💎 {{ selectedBet }}</span>
        </button>

        <!-- Deposit -->
        <button class="flex items-center gap-1 px-3 py-2 rounded-lg bg-white/8 text-white/60 text-xs">
          + Deposit
        </button>
      </div>

      <!-- Hash -->
      <div class="text-center mt-2">
        <span class="text-white/30 text-xs">⏱ Hash: {{ currentHash }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { plinkoPlay } from '../api/client'

const router = useRouter()
const gameCanvas = useTemplateRef<HTMLCanvasElement>('gameCanvas')

// State
const balance = ref(5.16)
const betAmounts = [1, 3, 10, 30, 50]
const selectedBet = ref(1)
const isPlaying = ref(false)
const currentHash = ref('624a...a8fa')

// Canvas dimensions
const canvasWidth = 380
const canvasHeight = 340

// Peg grid config — matches myballs.io exactly
const ROWS = 14
const PEG_RADIUS = 4
const BALL_RADIUS = 6

// Slot multipliers (left to right, 9 slots)
// 💀  🎁  2.0x  0.7x  0.6x  0.7x  2.0x  🎁  💀
const SLOT_LABELS = ['💀', '🎁', '2.0x', '0.7x', '0.6x', '0.7x', '2.0x', '🎁', '💀']
const SLOT_MULTIPLIERS = [0, 0, 2.0, 0.7, 0.6, 0.7, 2.0, 0, 0]
const SLOT_COLORS = ['#ef4444', '#f59e0b', '#22d3ee', '#a78bfa', '#6366f1', '#a78bfa', '#22d3ee', '#f59e0b', '#ef4444']

// Ball animation
let animationId: number | null = null
let ball: { x: number; y: number; vx: number; vy: number } | null = null
let pegPositions: { x: number; y: number; row: number }[] = []
let slotPositions: { x: number; y: number; width: number }[] = []
let ballPath: { x: number; y: number }[] = []
let targetSlot = -1
let animPhase = 0 // 0=idle, 1=dropping, 2=result

// Result popup
let resultMultiplier = 0
let resultTimeout: number | null = null

function selectBet(amount: number) {
  if (!isPlaying.value) selectedBet.value = amount
}

function generateHash(): string {
  return Math.random().toString(36).substring(2, 6) + '...' + Math.random().toString(36).substring(2, 6)
}

let nonce = Date.now()

function computePegLayout() {
  pegPositions = []
  const startY = 50
  const rowHeight = (canvasHeight - startY - 60) / ROWS
  const centerX = canvasWidth / 2

  for (let row = 0; row < ROWS; row++) {
    const numPegs = row + 3 // starts at 3, goes up to ROWS+2
    const spread = (numPegs - 1) * 14
    const startX = centerX - spread / 2

    for (let col = 0; col < numPegs; col++) {
      pegPositions.push({
        x: startX + col * 14,
        y: startY + row * rowHeight,
        row
      })
    }
  }

  // Slot positions at the bottom
  const numSlots = 9
  const slotWidth = canvasWidth / numSlots
  slotPositions = []
  for (let i = 0; i < numSlots; i++) {
    slotPositions.push({
      x: i * slotWidth,
      y: canvasHeight - 55,
      width: slotWidth
    })
  }
}

// Generate ball path from top to target slot
function generateBallPath(slot: number): { x: number; y: number }[] {
  const path: { x: number; y: number }[] = []
  const startY = 30
  const centerX = canvasWidth / 2

  // Start position (drop box)
  let x = centerX + (Math.random() - 0.5) * 8
  path.push({ x, y: startY })

  // Map slot to target X (center of slot)
  const slotWidth = canvasWidth / 9
  const targetX = slot * slotWidth + slotWidth / 2

  // Generate path through pegs
  const rowHeight = (canvasHeight - 50 - 60) / ROWS
  for (let row = 0; row < ROWS; row++) {
    const progress = (row + 1) / ROWS
    // Gradually steer toward target
    const currentTarget = centerX + (targetX - centerX) * progress
    const jitter = (Math.random() - 0.5) * 10 * (1 - progress)
    x = currentTarget + jitter
    x = Math.max(20, Math.min(canvasWidth - 20, x))

    path.push({ x, y: 50 + row * rowHeight + rowHeight / 2 })
  }

  // Final landing
  path.push({ x: targetX, y: canvasHeight - 65 })

  return path
}

async function playGame() {
  if (isPlaying.value || balance.value < selectedBet.value) return

  isPlaying.value = true
  balance.value -= selectedBet.value

  let serverResult: any = null
  try {
    nonce++
    serverResult = await plinkoPlay({
      amount: selectedBet.value,
      client_seed: generateHash(),
      nonce,
      user_id: 'anonymous'
    })
    targetSlot = serverResult.landing_slot
    currentHash.value = serverResult.server_seed_hash
    resultMultiplier = serverResult.multiplier
  } catch {
    // Fallback: client-side weighted drop if backend unavailable
    const weights = [0.02, 0.03, 0.1, 0.15, 0.2, 0.15, 0.1, 0.03, 0.02]
    let r = Math.random()
    targetSlot = 4
    for (let i = 0; i < weights.length; i++) { r -= weights[i]; if (r <= 0) { targetSlot = i; break } }
    currentHash.value = generateHash()
    resultMultiplier = SLOT_MULTIPLIERS[targetSlot]
  }

  ballPath = generateBallPath(targetSlot)

  // Animate ball
  animPhase = 1

  const startTime = Date.now()
  const totalDuration = 2200 // ms total drop time

  function animateDrop() {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / totalDuration, 1)

    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    const pathPos = eased * (ballPath.length - 1)
    const idx = Math.floor(pathPos)
    const frac = pathPos - idx

    if (idx < ballPath.length - 1) {
      ball = {
        x: ballPath[idx].x + (ballPath[idx + 1].x - ballPath[idx].x) * frac,
        y: ballPath[idx].y + (ballPath[idx + 1].y - ballPath[idx].y) * frac,
        vx: 0, vy: 0
      }
    } else {
      ball = { ...ballPath[ballPath.length - 1], vx: 0, vy: 0 }
    }

    draw()

    if (progress < 1) {
      animationId = requestAnimationFrame(animateDrop)
    } else {
      // Show result
      animPhase = 2
      showResult()
    }
  }

  animationId = requestAnimationFrame(animateDrop)
}

function showResult() {
  const payout = selectedBet.value * resultMultiplier
  balance.value += payout
  draw() // redraw with result overlay

  // Reset after 1.5s
  resultTimeout = setTimeout(() => {
    ball = null
    animPhase = 0
    isPlaying.value = false
    draw()
  }, 1500) as unknown as number
}

function draw() {
  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvasWidth, canvasHeight)

  // Background
  const bgGrad = ctx.createLinearGradient(0, 0, 0, canvasHeight)
  bgGrad.addColorStop(0, '#0f2a3d')
  bgGrad.addColorStop(1, '#0a2535')
  ctx.fillStyle = bgGrad
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  // Drop box (blue rectangle at top)
  ctx.fillStyle = '#3b82f6'
  ctx.beginPath()
  ctx.roundRect(canvasWidth / 2 - 28, 8, 56, 30, 4)
  ctx.fill()
  // Lighter top stripe
  ctx.fillStyle = '#60a5fa'
  ctx.beginPath()
  ctx.roundRect(canvasWidth / 2 - 28, 8, 56, 8, [4, 4, 0, 0])
  ctx.fill()

  // Pegs
  pegPositions.forEach((peg) => {
    // Glow
    ctx.shadowColor = peg.row < 3 ? 'rgba(139, 92, 246, 0.4)' : 'rgba(34, 211, 238, 0.3)'
    ctx.shadowBlur = 6

    // Color gradient: purple at top, cyan at bottom
    const t = peg.row / ROWS
    const r = Math.round(139 + (34 - 139) * t)
    const g = Math.round(92 + (211 - 92) * t)
    const b = Math.round(246 + (238 - 246) * t)
    ctx.fillStyle = `rgb(${r},${g},${b})`

    ctx.beginPath()
    ctx.arc(peg.x, peg.y, PEG_RADIUS, 0, Math.PI * 2)
    ctx.fill()
  })
  ctx.shadowBlur = 0

  // Slot zones at bottom
  const slotY = canvasHeight - 52
  const slotH = 48

  slotPositions.forEach((slot, i) => {
    // Background color per slot
    ctx.fillStyle = i === 0 || i === 8 ? 'rgba(239,68,68,0.25)'
      : i === 1 || i === 7 ? 'rgba(245,158,11,0.2)'
      : i === 2 || i === 6 ? 'rgba(34,211,238,0.2)'
      : 'rgba(99,102,241,0.15)'

    ctx.fillRect(slot.x + 1, slotY, slot.width - 2, slotH)

    // Slot label
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 11px -apple-system, sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(SLOT_LABELS[i], slot.x + slot.width / 2, slotY + slotH / 2 - 4)

    // Highlight active slot during result
    if (animPhase === 2 && i === targetSlot) {
      ctx.strokeStyle = SLOT_COLORS[i]
      ctx.lineWidth = 2
      ctx.strokeRect(slot.x + 1, slotY, slot.width - 2, slotH)

      // Glow
      ctx.shadowColor = SLOT_COLORS[i]
      ctx.shadowBlur = 12
      ctx.strokeRect(slot.x + 1, slotY, slot.width - 2, slotH)
      ctx.shadowBlur = 0
    }
  })

  // Ball
  if (ball) {
    // Glow
    ctx.shadowColor = 'rgba(250, 204, 21, 0.6)'
    ctx.shadowBlur = 10

    ctx.fillStyle = '#facc15'
    ctx.beginPath()
    ctx.arc(ball.x, ball.y, BALL_RADIUS, 0, Math.PI * 2)
    ctx.fill()

    ctx.shadowBlur = 0

    // Highlight
    ctx.fillStyle = 'rgba(255,255,255,0.4)'
    ctx.beginPath()
    ctx.arc(ball.x - 2, ball.y - 2, BALL_RADIUS * 0.4, 0, Math.PI * 2)
    ctx.fill()
  }

  // Result overlay
  if (animPhase === 2) {
    const mult = SLOT_MULTIPLIERS[targetSlot]
    const label = SLOT_LABELS[targetSlot]

    if (mult > 0) {
      // Win
      ctx.fillStyle = 'rgba(0,0,0,0.5)'
      ctx.fillRect(0, canvasHeight / 2 - 50, canvasWidth, 100)

      ctx.fillStyle = '#22d3ee'
      ctx.font = 'bold 32px -apple-system, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(`${label}`, canvasWidth / 2, canvasHeight / 2 - 12)

      ctx.fillStyle = '#fff'
      ctx.font = '14px -apple-system, sans-serif'
      ctx.fillText(`+${(selectedBet.value * mult).toFixed(2)} 💎`, canvasWidth / 2, canvasHeight / 2 + 18)
    } else {
      // Loss
      ctx.fillStyle = 'rgba(0,0,0,0.5)'
      ctx.fillRect(0, canvasHeight / 2 - 50, canvasWidth, 100)

      ctx.fillStyle = '#ef4444'
      ctx.font = 'bold 32px -apple-system, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(label, canvasWidth / 2, canvasHeight / 2 - 12)

      ctx.fillStyle = 'rgba(255,255,255,0.6)'
      ctx.font = '14px -apple-system, sans-serif'
      ctx.fillText(`-${selectedBet.value.toFixed(2)} 💎`, canvasWidth / 2, canvasHeight / 2 + 18)
    }
  }
}

onMounted(() => {
  computePegLayout()
  draw()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (resultTimeout) clearTimeout(resultTimeout)
})
</script>
