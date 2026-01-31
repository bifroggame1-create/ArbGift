<template>
  <div class="ball-escape-view min-h-screen flex flex-col" style="background: #000; padding-bottom: 16px;">
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

    <!-- Game Arena -->
    <div class="mx-3 mt-2 flex-1 flex items-center justify-center" style="min-height: 300px;">
      <div class="relative" style="width: 300px; height: 300px;">
        <canvas ref="gameCanvas" class="absolute inset-0 w-full h-full cursor-pointer"
          :width="300" :height="300" @click="onTap"></canvas>
      </div>
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
        <button @click="startGame" :disabled="gameState === 'playing' || balance < selectedBet"
          class="flex-1 py-3 rounded-xl font-bold text-sm text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style="background: linear-gradient(135deg, #22d3ee, #06b6d4);">
          {{ gameState === 'playing' ? 'Tap to escape!' : `Play ▼ ${selectedBet}` }}
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
import { escapePlay } from '../api/client'

const gameCanvas = useTemplateRef<HTMLCanvasElement>('gameCanvas')

const balance = ref(3.16)
const betAmounts = [1, 3, 10, 30, 50]
const selectedBet = ref(1)
const gameState = ref<'idle' | 'playing' | 'won' | 'lost'>('idle')
const currentHash = ref('502d...1c83')

const SIZE = 300
const CENTER = SIZE / 2
const RING_RADIUS = 105
const RING_WIDTH = 14
const CHAR_RADIUS = 22
const RING_CY = CENTER - 18 // ring center Y (shifted up to make room for bottom bars)

let animationId: number | null = null
let progress = 0
let multiplier = 1.0
let charAngle = -Math.PI / 2
let targetAngle = -Math.PI / 2
let resultTimeout: number | null = null
let nonce = Date.now()

function selectBet(amount: number) {
  if (gameState.value !== 'idle') return
  selectedBet.value = amount
}

function generateHash(): string {
  return Math.random().toString(36).substring(2, 6) + '...' + Math.random().toString(36).substring(2, 6)
}

function onTap() {
  if (gameState.value !== 'playing') return
  targetAngle = charAngle + (Math.random() - 0.3) * Math.PI * 0.8
}

async function startGame() {
  if (gameState.value === 'playing' || balance.value < selectedBet.value) return

  balance.value -= selectedBet.value
  gameState.value = 'playing'
  progress = 0
  multiplier = 1.0
  charAngle = -Math.PI / 2 + (Math.random() - 0.5) * 0.5
  targetAngle = charAngle

  let willEscape = Math.random() < 0.35
  let gameDuration = 3000 + Math.random() * 2000
  let serverMultiplier = 3.75

  try {
    nonce++
    const serverResult = await escapePlay({
      amount: selectedBet.value,
      client_seed: generateHash(),
      nonce,
      user_id: 'anonymous'
    })
    willEscape = serverResult.escaped
    gameDuration = serverResult.duration_ms
    serverMultiplier = serverResult.multiplier
    currentHash.value = serverResult.server_seed_hash
  } catch {
    currentHash.value = generateHash()
  }

  const startTime = Date.now()

  function gameLoop() {
    const elapsed = Date.now() - startTime
    progress = Math.min(elapsed / gameDuration, 1)
    multiplier = 1.0 + progress * (serverMultiplier - 1.0)

    charAngle += (targetAngle - charAngle) * 0.08
    charAngle += (Math.random() - 0.5) * 0.05

    if (progress >= 1) {
      multiplier = serverMultiplier
      if (willEscape) {
        charAngle = Math.PI + 0.4 + Math.random() * 0.3
        gameState.value = 'won'
        balance.value += selectedBet.value * serverMultiplier
      } else {
        charAngle = -0.1 - Math.random() * 0.3
        gameState.value = 'lost'
      }
      draw()
      resultTimeout = setTimeout(() => { gameState.value = 'idle'; progress = 0 }, 2000) as unknown as number
      return
    }

    draw()
    animationId = requestAnimationFrame(gameLoop)
  }

  animationId = requestAnimationFrame(gameLoop)
}

function draw() {
  const canvas = gameCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, SIZE, SIZE)
  ctx.fillStyle = '#0a0c14'
  ctx.fillRect(0, 0, SIZE, SIZE)

  // --- Bottom zone bars ---
  const barY = SIZE - 50
  const barH = 44
  const greenW = Math.floor(SIZE * 0.62)

  ctx.fillStyle = 'rgba(34, 197, 94, 0.2)'
  ctx.beginPath()
  ctx.roundRect(4, barY, greenW - 6, barH, [8, 0, 0, 8])
  ctx.fill()

  ctx.fillStyle = 'rgba(239, 68, 68, 0.2)'
  ctx.beginPath()
  ctx.roundRect(greenW + 2, barY, SIZE - greenW - 6, barH, [0, 8, 8, 0])
  ctx.fill()

  // Zone emojis
  ctx.font = '15px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  const barCY = barY + barH / 2
  ctx.fillText('🚀', 28, barCY)
  ctx.fillText('👑', greenW / 2, barCY)
  ctx.fillText('🎁', greenW - 22, barCY)
  ctx.fillText('💀', greenW + (SIZE - greenW) / 2, barCY)

  // --- Ring background ---
  ctx.beginPath()
  ctx.arc(CENTER, RING_CY, RING_RADIUS, 0, 2 * Math.PI)
  ctx.strokeStyle = 'rgba(255,255,255,0.07)'
  ctx.lineWidth = RING_WIDTH
  ctx.stroke()

  // --- Progress ring (MAGENTA) ---
  const progressAngle = -Math.PI / 2 + progress * 2 * Math.PI
  if (gameState.value === 'playing' || gameState.value === 'won' || gameState.value === 'lost') {
    ctx.shadowColor = 'rgba(217, 70, 239, 0.55)'
    ctx.shadowBlur = 18
    ctx.beginPath()
    ctx.arc(CENTER, RING_CY, RING_RADIUS, -Math.PI / 2, progressAngle)
    ctx.strokeStyle = '#d946ef'
    ctx.lineWidth = RING_WIDTH
    ctx.lineCap = 'round'
    ctx.stroke()
    ctx.shadowBlur = 0
  }

  // --- Character ---
  const cx = CENTER + Math.cos(charAngle) * (RING_RADIUS - RING_WIDTH * 0.3)
  const cy = RING_CY + Math.sin(charAngle) * (RING_RADIUS - RING_WIDTH * 0.3)

  ctx.shadowColor = gameState.value === 'won' ? 'rgba(34,197,94,0.5)' : 'rgba(217,70,239,0.4)'
  ctx.shadowBlur = 14

  // Body
  ctx.fillStyle = '#4ade80'
  ctx.beginPath()
  ctx.arc(cx, cy, CHAR_RADIUS * 0.65, 0, Math.PI * 2)
  ctx.fill()
  // Helmet
  ctx.fillStyle = '#60a5fa'
  ctx.beginPath()
  ctx.arc(cx, cy - 3, CHAR_RADIUS * 0.55, Math.PI, 0)
  ctx.fill()
  // Visor
  ctx.fillStyle = '#1e3a5f'
  ctx.beginPath()
  ctx.arc(cx, cy - 1, CHAR_RADIUS * 0.38, Math.PI + 0.25, -0.25)
  ctx.fill()
  // Eyes
  ctx.fillStyle = '#fff'
  ctx.beginPath()
  ctx.arc(cx - 4, cy + 2, 2.5, 0, Math.PI * 2)
  ctx.arc(cx + 4, cy + 2, 2.5, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#000'
  ctx.beginPath()
  ctx.arc(cx - 4, cy + 2.5, 1.2, 0, Math.PI * 2)
  ctx.arc(cx + 4, cy + 2.5, 1.2, 0, Math.PI * 2)
  ctx.fill()

  ctx.shadowBlur = 0

  // --- Center content ---
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  if (gameState.value === 'idle') {
    ctx.fillStyle = 'rgba(255,255,255,0.55)'
    ctx.font = 'bold 15px -apple-system, sans-serif'
    ctx.fillText('This is Preview', CENTER, RING_CY - 2)
    ctx.fillStyle = 'rgba(255,255,255,0.28)'
    ctx.font = '11px -apple-system, sans-serif'
    ctx.fillText('Tap button below to play', CENTER, RING_CY + 18)
  } else {
    const color = gameState.value === 'won' ? '#4ade80' : gameState.value === 'lost' ? '#ef4444' : '#4ade80'
    ctx.fillStyle = color
    ctx.font = 'bold 30px -apple-system, sans-serif'
    ctx.fillText(`${multiplier.toFixed(2)}x`, CENTER, RING_CY - 6)

    if (gameState.value === 'won') {
      ctx.fillStyle = '#4ade80'
      ctx.font = 'bold 14px -apple-system, sans-serif'
      ctx.fillText('Escaped!', CENTER, RING_CY + 22)
      ctx.fillStyle = 'rgba(255,255,255,0.5)'
      ctx.font = '11px -apple-system, sans-serif'
      ctx.fillText(`+${(selectedBet.value * multiplier).toFixed(2)} ▼`, CENTER, RING_CY + 40)
    } else if (gameState.value === 'lost') {
      ctx.fillStyle = '#ef4444'
      ctx.font = 'bold 14px -apple-system, sans-serif'
      ctx.fillText('Caught!', CENTER, RING_CY + 22)
      ctx.fillStyle = 'rgba(255,255,255,0.4)'
      ctx.font = '11px -apple-system, sans-serif'
      ctx.fillText(`-${selectedBet.value.toFixed(2)} ▼`, CENTER, RING_CY + 40)
    }
  }
}

onMounted(() => { draw() })

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (resultTimeout) clearTimeout(resultTimeout)
})
</script>
