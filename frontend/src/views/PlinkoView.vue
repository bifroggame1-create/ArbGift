<template>
  <div class="plinko-view min-h-screen flex flex-col" style="background: #000; padding-bottom: 16px;">
    <div class="px-3 pt-3 flex flex-col gap-2">
      <!-- Tournament Banner -->
      <div class="rounded-xl px-4 py-2.5 flex items-center justify-between"
        style="background: linear-gradient(135deg, #ca8a04 0%, #22c55e 60%, #4ade80 100%);">
        <span class="text-white font-bold text-sm">Giftomania</span>
        <span class="text-white/70 text-xs font-mono">3:04:57:06</span>
      </div>
      <!-- Header Row -->
      <div class="flex items-center justify-between">
        <div class="flex gap-2">
          <button class="w-9 h-9 rounded-xl flex items-center justify-center" style="background: rgba(255,255,255,0.06);">
            <svg class="w-4 h-4" fill="none" stroke="rgba(255,255,255,0.45)" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="1.5"/>
              <path d="M16 2v4M8 2v4M3 10h18" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
          <div class="flex items-center gap-1 rounded-full px-3 py-1" style="background: rgba(255,255,255,0.08);">
            <span class="text-white/50 text-xs">Max Prize</span>
            <span class="text-white/40 text-xs">▼</span>
            <span class="text-white font-bold text-sm">30</span>
          </div>
        </div>
        <div class="flex items-center gap-1.5">
          <button class="flex items-center gap-1.5 rounded-full px-3 py-1.5" style="background: rgba(255,255,255,0.08);">
            <span class="text-white/45 text-xs">▼</span>
            <span class="text-white font-bold text-sm">{{ balance.toFixed(2) }}</span>
          </button>
          <button class="w-7 h-7 rounded-full flex items-center justify-center text-white/50 text-sm" style="background: rgba(255,255,255,0.12);">+</button>
        </div>
      </div>
    </div>

    <!-- Game Canvas Area -->
    <div class="mx-3 mt-2 flex-1 flex items-center justify-center" style="min-height: 360px;">
      <canvas
        ref="gameCanvas"
        class="w-full"
        style="max-width: 380px;"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>
    </div>

    <!-- Bottom Controls -->
    <div class="px-3 py-3">
      <div class="flex gap-2 mb-3">
        <button v-for="amount in betAmounts" :key="amount" @click="selectBet(amount)"
          class="flex-1 py-2 rounded-lg font-bold flex items-center justify-center gap-1 transition-all"
          :style="selectedBet === amount
            ? { background: 'rgba(34,211,238,0.2)', border: '1px solid rgba(34,211,238,0.4)' }
            : { background: 'rgba(255,255,255,0.06)', border: '1px solid transparent' }">
          <span class="text-white/75 text-sm">{{ amount }}</span>
          <span class="text-white/30 text-xs">▼</span>
        </button>
      </div>
      <div class="flex items-center gap-2">
        <button class="flex flex-col items-center gap-0.5">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: rgba(255,255,255,0.06);">
            <div class="w-5 h-5 rounded-full flex items-center justify-center" style="background: #3b82f6;">
              <span class="text-white text-xs font-bold">▼</span>
            </div>
          </div>
          <span class="text-white/35 text-xs">Swap ☆</span>
        </button>
        <button @click="playGame" :disabled="isPlaying || balance < selectedBet"
          class="flex-1 py-3 rounded-xl font-bold text-sm text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style="background: linear-gradient(135deg, #22d3ee, #06b6d4);">
          {{ isPlaying ? 'Dropping...' : `Play ▼ ${selectedBet}` }}
        </button>
        <button class="flex flex-col items-center gap-0.5">
          <div class="w-10 h-10 rounded-full flex items-center justify-center text-white/50 text-lg" style="background: rgba(255,255,255,0.10);">+</div>
          <span class="text-white/35 text-xs">Deposit</span>
        </button>
      </div>
      <div class="text-center mt-2">
        <span class="text-white/20 text-xs">⏱ Hash: {{ currentHash }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, useTemplateRef } from 'vue'
import { plinkoPlay } from '../api/client'

const gameCanvas = useTemplateRef<HTMLCanvasElement>('gameCanvas')

const balance = ref(5.16)
const betAmounts = [1, 3, 10, 30, 50]
const selectedBet = ref(1)
const isPlaying = ref(false)
const currentHash = ref('624a...a8fa')

const canvasWidth = 380
const canvasHeight = 360

// Peg grid
const ROWS = 12
const PEG_RADIUS = 4.5
const BALL_RADIUS = 7
const GRAVITY = 0.38
const BOUNCE_DAMPING = 0.42

const SLOT_LABELS = ['💀', '🎁', '2.0x', '0.7x', '0.6x', '0.7x', '2.0x', '🎁', '💀']
const SLOT_MULTIPLIERS = [0, 0, 2.0, 0.7, 0.6, 0.7, 2.0, 0, 0]
const SLOT_COLORS = ['#ef4444', '#f59e0b', '#22d3ee', '#a78bfa', '#6366f1', '#a78bfa', '#22d3ee', '#f59e0b', '#ef4444']

// Layout constants
const TOP_Y = 52
const BOTTOM_Y = canvasHeight - 58
const ROW_HEIGHT = (BOTTOM_Y - TOP_Y) / ROWS
const COL_SPACING = 18
const NUM_SLOTS = 9
const SLOT_WIDTH = canvasWidth / NUM_SLOTS

// Peg positions per row
interface PegPos { x: number; y: number }
let pegRows: PegPos[][] = []

function computeLayout() {
  pegRows = []
  const centerX = canvasWidth / 2
  for (let row = 0; row < ROWS; row++) {
    const numPegs = row + 3
    const rowPegs: PegPos[] = []
    const totalSpan = (numPegs - 1) * COL_SPACING
    const startX = centerX - totalSpan / 2
    for (let col = 0; col < numPegs; col++) {
      rowPegs.push({ x: startX + col * COL_SPACING, y: TOP_Y + row * ROW_HEIGHT })
    }
    pegRows.push(rowPegs)
  }
}

// Physics ball state
let ball: { x: number; y: number; vx: number; vy: number } | null = null
let targetSlot = 4
let rowTargets: number[] = [] // X target per row for steering
let lastBounceRow = -1
let animPhase = 0 // 0=idle, 1=dropping, 2=result
let animationId: number | null = null
let resultTimeout: number | null = null
let nonce = Date.now()

function selectBet(amount: number) {
  if (!isPlaying.value) selectedBet.value = amount
}

function generateHash(): string {
  return Math.random().toString(36).substring(2, 6) + '...' + Math.random().toString(36).substring(2, 6)
}

// Pre-compute row-by-row X targets guiding ball toward final slot
function computeRowTargets(slot: number) {
  const centerX = canvasWidth / 2
  const targetX = slot * SLOT_WIDTH + SLOT_WIDTH / 2
  rowTargets = []
  for (let row = 0; row < ROWS; row++) {
    const t = (row + 1) / ROWS
    // ease-in so steering is subtle at top, stronger near bottom
    const eased = t * t
    rowTargets.push(centerX + (targetX - centerX) * eased)
  }
}

async function playGame() {
  if (isPlaying.value || balance.value < selectedBet.value) return
  isPlaying.value = true
  balance.value -= selectedBet.value

  // Call server
  try {
    nonce++
    const serverResult = await plinkoPlay({
      amount: selectedBet.value,
      client_seed: generateHash(),
      nonce,
      user_id: 'anonymous'
    })
    targetSlot = serverResult.landing_slot
    currentHash.value = serverResult.server_seed_hash
  } catch {
    // Fallback client-side
    const weights = [0.02, 0.03, 0.1, 0.15, 0.2, 0.15, 0.1, 0.03, 0.02]
    let r = Math.random()
    targetSlot = 4
    for (let i = 0; i < weights.length; i++) { r -= weights[i]; if (r <= 0) { targetSlot = i; break } }
    currentHash.value = generateHash()
  }

  computeRowTargets(targetSlot)

  // Spawn ball at drop box
  const startX = canvasWidth / 2 + (Math.random() - 0.5) * 6
  ball = { x: startX, y: TOP_Y - 18, vx: (Math.random() - 0.5) * 0.6, vy: 1.5 }
  lastBounceRow = -1
  animPhase = 1
  animationId = requestAnimationFrame(physicsLoop)
}

function physicsLoop() {
  if (!ball) return

  // Gravity
  ball.vy += GRAVITY
  ball.x += ball.vx
  ball.y += ball.vy

  // Determine which row we're in
  const rowIdx = Math.floor((ball.y - TOP_Y) / ROW_HEIGHT)

  // Peg collision — check current and nearby rows
  for (let r = Math.max(0, rowIdx - 1); r <= Math.min(ROWS - 1, rowIdx + 1); r++) {
    const pegs = pegRows[r]
    if (!pegs) continue
    for (const peg of pegs) {
      const dx = ball.x - peg.x
      const dy = ball.y - peg.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      const minDist = PEG_RADIUS + BALL_RADIUS
      if (dist < minDist && dist > 0) {
        // Push ball out
        const nx = dx / dist
        const ny = dy / dist
        ball.x = peg.x + nx * minDist
        ball.y = peg.y + ny * minDist

        // Reflect velocity + dampen
        const dot = ball.vx * nx + ball.vy * ny
        ball.vx -= 2 * dot * nx
        ball.vy -= 2 * dot * ny
        ball.vx *= BOUNCE_DAMPING
        ball.vy *= BOUNCE_DAMPING

        // After bounce, add some speed back (gravity feel)
        ball.vy += 0.8
      }
    }
  }

  // Steering: if we just passed into a new row, nudge toward target
  if (rowIdx >= 0 && rowIdx < ROWS && rowIdx !== lastBounceRow) {
    lastBounceRow = rowIdx
    const target = rowTargets[rowIdx]
    const diff = target - ball.x
    // Gentle horizontal nudge
    ball.vx += diff * 0.12
    // Add small random jitter for realism
    ball.vx += (Math.random() - 0.5) * 0.6
  }

  // Clamp X
  if (ball.x < BALL_RADIUS) { ball.x = BALL_RADIUS; ball.vx = Math.abs(ball.vx) * 0.5 }
  if (ball.x > canvasWidth - BALL_RADIUS) { ball.x = canvasWidth - BALL_RADIUS; ball.vx = -Math.abs(ball.vx) * 0.5 }

  // Check if ball reached bottom
  if (ball.y > BOTTOM_Y) {
    ball.y = BOTTOM_Y
    ball.vy = 0
    ball.vx = 0
    // Snap to target slot center
    ball.x = targetSlot * SLOT_WIDTH + SLOT_WIDTH / 2
    animPhase = 2
    draw()
    showResult()
    return
  }

  draw()
  animationId = requestAnimationFrame(physicsLoop)
}

function showResult() {
  const mult = SLOT_MULTIPLIERS[targetSlot]
  if (mult > 0) {
    balance.value += selectedBet.value * mult
  }
  resultTimeout = setTimeout(() => {
    ball = null
    animPhase = 0
    isPlaying.value = false
    draw()
  }, 1800) as unknown as number
}

function draw() {
  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvasWidth, canvasHeight)

  // Background
  ctx.fillStyle = '#0a0c14'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  // Drop box (top center)
  ctx.fillStyle = '#1e3a5f'
  ctx.beginPath()
  ctx.roundRect(canvasWidth / 2 - 30, 6, 60, 28, 5)
  ctx.fill()
  ctx.fillStyle = '#3b82f6'
  ctx.beginPath()
  ctx.roundRect(canvasWidth / 2 - 30, 6, 60, 10, [5, 5, 0, 0])
  ctx.fill()
  // Arrow down
  ctx.fillStyle = 'rgba(255,255,255,0.5)'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('▼', canvasWidth / 2, 24)

  // Pegs
  pegRows.forEach((row, rowIdx) => {
    const t = rowIdx / ROWS
    const r = Math.round(139 + (34 - 139) * t)
    const g = Math.round(92 + (211 - 92) * t)
    const b = Math.round(246 + (238 - 246) * t)
    const color = `rgb(${r},${g},${b})`

    row.forEach(peg => {
      ctx.shadowColor = color + '66'
      ctx.shadowBlur = 5
      ctx.fillStyle = color
      ctx.beginPath()
      ctx.arc(peg.x, peg.y, PEG_RADIUS, 0, Math.PI * 2)
      ctx.fill()
    })
  })
  ctx.shadowBlur = 0

  // Slot zones
  const slotY = canvasHeight - 56
  const slotH = 52
  for (let i = 0; i < NUM_SLOTS; i++) {
    const x = i * SLOT_WIDTH
    const isActive = animPhase === 2 && i === targetSlot

    // Background
    ctx.fillStyle = i === 0 || i === 8 ? 'rgba(239,68,68,0.22)'
      : i === 1 || i === 7 ? 'rgba(245,158,11,0.18)'
      : i === 2 || i === 6 ? 'rgba(34,211,238,0.18)'
      : 'rgba(99,102,241,0.14)'

    ctx.beginPath()
    if (i === 0) {
      ctx.roundRect(x + 1, slotY, SLOT_WIDTH - 2, slotH, [6, 0, 0, 6])
    } else if (i === NUM_SLOTS - 1) {
      ctx.roundRect(x + 1, slotY, SLOT_WIDTH - 2, slotH, [0, 6, 6, 0])
    } else {
      ctx.fillRect(x + 1, slotY, SLOT_WIDTH - 2, slotH)
      ctx.beginPath() // reset path for non-rounded
    }
    ctx.fill()

    // Active highlight
    if (isActive) {
      ctx.shadowColor = SLOT_COLORS[i]
      ctx.shadowBlur = 14
      ctx.strokeStyle = SLOT_COLORS[i]
      ctx.lineWidth = 2
      ctx.strokeRect(x + 1, slotY, SLOT_WIDTH - 2, slotH)
      ctx.shadowBlur = 0
    }

    // Label
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 11px -apple-system, sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(SLOT_LABELS[i], x + SLOT_WIDTH / 2, slotY + slotH / 2)
  }

  // Ball
  if (ball) {
    ctx.shadowColor = 'rgba(250, 204, 21, 0.7)'
    ctx.shadowBlur = 12
    ctx.fillStyle = '#facc15'
    ctx.beginPath()
    ctx.arc(ball.x, ball.y, BALL_RADIUS, 0, Math.PI * 2)
    ctx.fill()
    ctx.shadowBlur = 0

    // Specular highlight
    ctx.fillStyle = 'rgba(255,255,255,0.45)'
    ctx.beginPath()
    ctx.arc(ball.x - 2.5, ball.y - 2.5, BALL_RADIUS * 0.38, 0, Math.PI * 2)
    ctx.fill()
  }

  // Result overlay
  if (animPhase === 2) {
    const mult = SLOT_MULTIPLIERS[targetSlot]
    const label = SLOT_LABELS[targetSlot]

    ctx.fillStyle = 'rgba(0,0,0,0.55)'
    ctx.fillRect(0, canvasHeight / 2 - 48, canvasWidth, 96)

    if (mult > 0) {
      ctx.fillStyle = '#22d3ee'
      ctx.font = 'bold 34px -apple-system, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(label, canvasWidth / 2, canvasHeight / 2 - 10)

      ctx.fillStyle = 'rgba(255,255,255,0.7)'
      ctx.font = '14px -apple-system, sans-serif'
      ctx.fillText(`+${(selectedBet.value * mult).toFixed(2)}`, canvasWidth / 2, canvasHeight / 2 + 18)
    } else {
      ctx.fillStyle = '#ef4444'
      ctx.font = 'bold 34px -apple-system, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(label, canvasWidth / 2, canvasHeight / 2 - 10)

      ctx.fillStyle = 'rgba(255,255,255,0.5)'
      ctx.font = '14px -apple-system, sans-serif'
      ctx.fillText(`-${selectedBet.value.toFixed(2)}`, canvasWidth / 2, canvasHeight / 2 + 18)
    }
  }
}

onMounted(() => {
  computeLayout()
  draw()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (resultTimeout) clearTimeout(resultTimeout)
})
</script>
