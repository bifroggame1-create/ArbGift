<template>
  <div class="gonka-view min-h-screen flex flex-col" style="background: #000; padding-bottom: 16px;">
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

    <!-- Lite / Hard Toggle -->
    <div class="flex justify-center gap-1 px-4 py-2">
      <button
        @click="setMode('lite')"
        class="px-6 py-1.5 rounded-full text-sm font-bold transition-all"
        :class="mode === 'lite' ? 'bg-white text-black' : 'bg-white/10 text-white/60'"
      >Lite</button>
      <button
        @click="setMode('hard')"
        class="px-6 py-1.5 rounded-full text-sm font-bold transition-all flex items-center gap-1"
        :class="mode === 'hard' ? 'bg-white text-black' : 'bg-white/10 text-white/60'"
      >💀 Hard</button>
    </div>

    <!-- 3x3 Multiplier Grid -->
    <div class="px-3 flex-1" style="max-height: 340px;">
      <div class="grid grid-cols-3 gap-2 h-full">
        <div
          v-for="(cell, idx) in gridCells"
          :key="idx"
          class="relative rounded-xl flex flex-col items-center justify-center transition-all"
          :style="{ background: cell.bgColor, boxShadow: highlightedCell === idx ? `0 0 16px ${cell.circleColor}66` : 'none' }"
        >
          <!-- Prize badge top-right -->
          <div class="absolute top-1.5 right-1.5 text-xs font-bold" :style="{ color: cell.circleColor }">
            +{{ cell.prize }} 💎
          </div>

          <!-- Circle with multiplier -->
          <div
            class="w-14 h-14 rounded-full flex items-center justify-center"
            :style="{ background: `radial-gradient(circle at 35% 35%, ${cell.circleHighlight}, ${cell.circleColor})` }"
          >
            <span class="text-white font-bold text-lg" style="text-shadow: 0 1px 3px rgba(0,0,0,0.5);">
              X{{ cell.multiplier }}
            </span>
          </div>

          <!-- Balls count -->
          <div class="text-white/50 text-xs mt-1.5">{{ cell.balls }} Balls</div>
        </div>
      </div>
    </div>

    <!-- Game Animation Area (shown while playing) -->
    <div v-if="isPlaying" class="mx-3 rounded-xl overflow-hidden" style="height: 180px; background: #0d1525;">
      <canvas ref="gameCanvas" class="w-full h-full" :width="360" :height="180"></canvas>
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
          {{ isPlaying ? 'Playing...' : `Play ▼ ${selectedBet}` }}
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
import { ref, onUnmounted, useTemplateRef, computed } from 'vue'
import { gonkaPlay } from '../api/client'

const gameCanvas = useTemplateRef<HTMLCanvasElement>('gameCanvas')

// State
const balance = ref(4.16)
const betAmounts = [1, 3, 10, 30, 50]
const selectedBet = ref(1)
const isPlaying = ref(false)
const mode = ref<'lite' | 'hard'>('lite')
const currentHash = ref('5b18...bb33')
const highlightedCell = ref(-1)

// Grid data — matches myballs.io exactly
// Row 0: high multiplier (red/orange), 6 balls each
// Row 1: mid multiplier (green), 8-12 balls
// Row 2: low multiplier (dark green), 11-28 balls
const GRID_DATA = {
  lite: [
    // Row 0
    { multiplier: 2, balls: 6, prize: '2', circleColor: '#ef4444', circleHighlight: '#f87171', bgColor: 'rgba(239,68,68,0.12)' },
    { multiplier: 1.7, balls: 6, prize: '1.7', circleColor: '#f97316', circleHighlight: '#fb923c', bgColor: 'rgba(249,115,22,0.12)' },
    { multiplier: 1.5, balls: 6, prize: '1.5', circleColor: '#eab308', circleHighlight: '#facc15', bgColor: 'rgba(234,179,8,0.12)' },
    // Row 1
    { multiplier: 1.2, balls: 8, prize: '1.2', circleColor: '#22c55e', circleHighlight: '#4ade80', bgColor: 'rgba(34,197,94,0.12)' },
    { multiplier: 1, balls: 12, prize: '1', circleColor: '#16a34a', circleHighlight: '#4ade80', bgColor: 'rgba(22,163,74,0.12)' },
    { multiplier: 0.8, balls: 12, prize: '0.8', circleColor: '#15803d', circleHighlight: '#22c55e', bgColor: 'rgba(21,128,61,0.12)' },
    // Row 2
    { multiplier: 0.5, balls: 11, prize: '0.5', circleColor: '#166534', circleHighlight: '#16a34a', bgColor: 'rgba(22,101,52,0.12)' },
    { multiplier: 0.3, balls: 11, prize: '0.3', circleColor: '#14532d', circleHighlight: '#166534', bgColor: 'rgba(20,83,45,0.12)' },
    { multiplier: 0.1, balls: 28, prize: '0.1', circleColor: '#052e16', circleHighlight: '#14532d', bgColor: 'rgba(5,46,22,0.15)' },
  ],
  hard: [
    { multiplier: 3, balls: 4, prize: '3', circleColor: '#dc2626', circleHighlight: '#ef4444', bgColor: 'rgba(220,38,38,0.12)' },
    { multiplier: 2.5, balls: 4, prize: '2.5', circleColor: '#ea580c', circleHighlight: '#f97316', bgColor: 'rgba(234,88,12,0.12)' },
    { multiplier: 2, balls: 4, prize: '2', circleColor: '#ca8a04', circleHighlight: '#eab308', bgColor: 'rgba(202,138,4,0.12)' },
    { multiplier: 1.5, balls: 6, prize: '1.5', circleColor: '#16a34a', circleHighlight: '#4ade80', bgColor: 'rgba(22,163,74,0.12)' },
    { multiplier: 1, balls: 10, prize: '1', circleColor: '#15803d', circleHighlight: '#22c55e', bgColor: 'rgba(21,128,61,0.12)' },
    { multiplier: 0.5, balls: 14, prize: '0.5', circleColor: '#166534', circleHighlight: '#16a34a', bgColor: 'rgba(22,101,52,0.12)' },
    { multiplier: 0.3, balls: 18, prize: '0.3', circleColor: '#14532d', circleHighlight: '#166534', bgColor: 'rgba(20,83,45,0.12)' },
    { multiplier: 0.1, balls: 24, prize: '0.1', circleColor: '#052e16', circleHighlight: '#14532d', bgColor: 'rgba(5,46,22,0.15)' },
    { multiplier: 0.05, balls: 40, prize: '0.05', circleColor: '#052e16', circleHighlight: '#14532d', bgColor: 'rgba(5,46,22,0.18)' },
  ]
}

const gridCells = computed(() => GRID_DATA[mode.value])

function setMode(m: 'lite' | 'hard') {
  if (!isPlaying.value) mode.value = m
}

function selectBet(amount: number) {
  if (!isPlaying.value) selectedBet.value = amount
}

function generateHash(): string {
  return Math.random().toString(36).substring(2, 6) + '...' + Math.random().toString(36).substring(2, 6)
}

let nonce = Date.now()

// Animation
let animationId: number | null = null
let balls: { x: number; y: number; vx: number; vy: number }[] = []

async function playGame() {
  if (isPlaying.value || balance.value < selectedBet.value) return

  isPlaying.value = true
  balance.value -= selectedBet.value
  highlightedCell.value = -1

  let resultCell = 4 // fallback center
  try {
    nonce++
    const serverResult = await gonkaPlay({
      amount: selectedBet.value,
      mode: mode.value,
      client_seed: generateHash(),
      nonce,
      user_id: 'anonymous'
    })
    resultCell = serverResult.cell_index
    currentHash.value = serverResult.server_seed_hash
  } catch {
    // Fallback: client-side weighted drop
    const cells = gridCells.value
    const totalBalls = cells.reduce((sum, c) => sum + c.balls, 0)
    let r = Math.random() * totalBalls
    for (let i = 0; i < cells.length; i++) { r -= cells[i].balls; if (r <= 0) { resultCell = i; break } }
    currentHash.value = generateHash()
  }

  // Wait for canvas to render
  await new Promise(r => setTimeout(r, 50))

  // Animate balls falling
  balls = []
  const numBalls = gridCells.value[resultCell].balls
  for (let i = 0; i < Math.min(numBalls, 8); i++) {
    balls.push({
      x: 60 + Math.random() * 240,
      y: -10 - i * 20,
      vx: (Math.random() - 0.5) * 2,
      vy: 1 + Math.random() * 0.5
    })
  }

  const startTime = Date.now()
  const duration = 2000

  function animate() {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    // Update balls
    balls.forEach(b => {
      b.vy += 0.15 // gravity
      b.y += b.vy
      b.x += b.vx

      // Bounce off walls
      if (b.x < 15) { b.x = 15; b.vx = Math.abs(b.vx) * 0.8 }
      if (b.x > 345) { b.x = 345; b.vx = -Math.abs(b.vx) * 0.8 }

      // Bounce off floor
      if (b.y > 165) { b.y = 165; b.vy = -b.vy * 0.6; b.vx += (Math.random() - 0.5) * 1 }
    })

    drawGame()

    if (progress < 1) {
      animationId = requestAnimationFrame(animate)
    } else {
      // Show result
      highlightedCell.value = resultCell
      const mult = gridCells.value[resultCell].multiplier
      balance.value += selectedBet.value * mult

      setTimeout(() => {
        isPlaying.value = false
        highlightedCell.value = -1
        balls = []
      }, 1500)
    }
  }

  animationId = requestAnimationFrame(animate)
}

function drawGame() {
  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, 360, 180)

  // Background
  ctx.fillStyle = '#0d1525'
  ctx.fillRect(0, 0, 360, 180)

  // Walls (blue glowing)
  const wallGrad = ctx.createLinearGradient(0, 0, 0, 180)
  wallGrad.addColorStop(0, '#1e3a5f')
  wallGrad.addColorStop(1, '#0f2d4a')
  ctx.fillStyle = wallGrad

  // Left wall
  ctx.fillRect(0, 0, 12, 180)
  // Right wall
  ctx.fillRect(348, 0, 12, 180)

  // Floor with checker pattern
  ctx.fillStyle = '#1a2a3a'
  ctx.fillRect(12, 170, 336, 10)

  // Balls
  balls.forEach(b => {
    ctx.shadowColor = 'rgba(34, 211, 238, 0.5)'
    ctx.shadowBlur = 6
    ctx.fillStyle = '#22d3ee'
    ctx.beginPath()
    ctx.arc(b.x, b.y, 6, 0, Math.PI * 2)
    ctx.fill()
    ctx.shadowBlur = 0
  })
}

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>
