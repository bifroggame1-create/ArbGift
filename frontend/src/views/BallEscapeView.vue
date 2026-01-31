<template>
  <div class="ball-escape-view min-h-screen flex flex-col" style="background: #0a0c14;">
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

    <!-- Max Prize Badge -->
    <div class="flex justify-center px-4 py-1">
      <div class="bg-white/8 rounded-full px-4 py-1 flex items-center gap-2">
        <span class="text-white/60 text-xs">Max Prize</span>
        <span class="text-white font-bold text-sm">💎 30</span>
      </div>
    </div>

    <!-- Game Arena -->
    <div class="flex-1 flex items-center justify-center px-4" style="min-height: 320px;">
      <div class="relative" style="width: 280px; height: 280px;">
        <canvas
          ref="gameCanvas"
          class="absolute inset-0 w-full h-full cursor-pointer"
          :width="280"
          :height="280"
          @click="onTap"
        ></canvas>
      </div>
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
        <button class="flex items-center gap-1 px-3 py-2 rounded-lg bg-white/8 text-white/60 text-xs">💎 ☆</button>

        <button
          @click="startGame"
          :disabled="gameState === 'playing' || balance < selectedBet"
          class="flex-1 py-3 rounded-xl font-bold text-base transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style="background: linear-gradient(135deg, #22d3ee, #06b6d4);"
        >
          <span class="text-white">
            {{ gameState === 'playing' ? 'Tap to escape!' : `Play 💎 ${selectedBet}` }}
          </span>
        </button>

        <button class="flex items-center gap-1 px-3 py-2 rounded-lg bg-white/8 text-white/60 text-xs">+ Deposit</button>
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
import { escapePlay } from '../api/client'

const router = useRouter()
const gameCanvas = useTemplateRef<HTMLCanvasElement>('gameCanvas')

// State
const balance = ref(3.16)
const betAmounts = [1, 3, 10, 30, 50]
const selectedBet = ref(1)
const gameState = ref<'idle' | 'playing' | 'won' | 'lost'>('idle')
const currentHash = ref('502d...1c83')

// Game constants
const SIZE = 280
const CENTER = SIZE / 2
const RING_RADIUS = 115
const RING_WIDTH = 12
const CHAR_RADIUS = 28

// Game state
let animationId: number | null = null
let progress = 0 // 0 to 1 (how far around the ring)
let multiplier = 1.0
let charAngle = -Math.PI / 2 // character position on ring (radians)
let targetAngle = -Math.PI / 2
let resultTimeout: number | null = null

const GREEN_START = Math.PI
const RED_START = 0

function selectBet(amount: number) {
  if (gameState.value !== 'idle') return
  selectedBet.value = amount
}

function generateHash(): string {
  return Math.random().toString(36).substring(2, 6) + '...' + Math.random().toString(36).substring(2, 6)
}

function onTap() {
  if (gameState.value !== 'playing') return

  // Move character to a random position on ring
  targetAngle = charAngle + (Math.random() - 0.3) * Math.PI * 0.8
}

let nonce = Date.now()

async function startGame() {
  if (gameState.value === 'playing' || balance.value < selectedBet.value) return

  balance.value -= selectedBet.value
  gameState.value = 'playing'
  progress = 0
  multiplier = 1.0
  charAngle = -Math.PI / 2 + (Math.random() - 0.5) * 0.5
  targetAngle = charAngle

  // Get server-determined result (kept hidden until animation ends)
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
    multiplier = 1.0 + progress * 2.75 // grows from 1.0x to 3.75x

    // Character movement — drifts randomly
    charAngle += (targetAngle - charAngle) * 0.08
    charAngle += (Math.random() - 0.5) * 0.05

    // If game ending, determine escape
    if (progress >= 1) {
      multiplier = serverMultiplier
      if (willEscape) {
        // Character escapes to green zone
        charAngle = GREEN_START + Math.PI * 0.3 + Math.random() * 0.5
        gameState.value = 'won'
        balance.value += selectedBet.value * serverMultiplier
      } else {
        // Character caught in red zone
        charAngle = RED_START + Math.PI * 0.3 + Math.random() * 0.3
        gameState.value = 'lost'
      }

      draw()

      resultTimeout = setTimeout(() => {
        gameState.value = 'idle'
        progress = 0
      }, 2000) as unknown as number
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

  // Background
  ctx.fillStyle = '#0a0c14'
  ctx.fillRect(0, 0, SIZE, SIZE)

  // --- Green zone arc (bottom half = safe) ---
  ctx.beginPath()
  ctx.arc(CENTER, CENTER, RING_RADIUS + RING_WIDTH * 0.7, Math.PI, 2 * Math.PI)
  ctx.arc(CENTER, CENTER, RING_RADIUS - RING_WIDTH * 0.7, 2 * Math.PI, Math.PI, true)
  ctx.closePath()
  ctx.fillStyle = 'rgba(34, 197, 94, 0.25)'
  ctx.fill()

  // --- Red zone arc (top half = danger) ---
  ctx.beginPath()
  ctx.arc(CENTER, CENTER, RING_RADIUS + RING_WIDTH * 0.7, 0, Math.PI)
  ctx.arc(CENTER, CENTER, RING_RADIUS - RING_WIDTH * 0.7, Math.PI, 0, true)
  ctx.closePath()
  ctx.fillStyle = 'rgba(239, 68, 68, 0.25)'
  ctx.fill()

  // Zone emojis
  ctx.font = '18px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  // Green zone emojis
  ctx.fillText('🍬', CENTER - 55, CENTER + 75)
  ctx.fillText('👑', CENTER + 55, CENTER + 75)
  // Red zone emojis
  ctx.fillText('💀', CENTER - 40, CENTER - 75)
  ctx.fillText('💀', CENTER + 40, CENTER - 75)

  // --- Progress ring (purple glow) ---
  const progressAngle = -Math.PI / 2 + progress * 2 * Math.PI

  // Ring background (dark)
  ctx.beginPath()
  ctx.arc(CENTER, CENTER, RING_RADIUS, 0, 2 * Math.PI)
  ctx.strokeStyle = 'rgba(255,255,255,0.08)'
  ctx.lineWidth = RING_WIDTH
  ctx.stroke()

  // Progress arc (purple glow)
  if (gameState.value === 'playing' || gameState.value === 'won' || gameState.value === 'lost') {
    ctx.shadowColor = 'rgba(168, 85, 247, 0.6)'
    ctx.shadowBlur = 15

    ctx.beginPath()
    ctx.arc(CENTER, CENTER, RING_RADIUS, -Math.PI / 2, progressAngle)
    ctx.strokeStyle = '#a855f7'
    ctx.lineWidth = RING_WIDTH
    ctx.lineCap = 'round'
    ctx.stroke()
    ctx.shadowBlur = 0
  }

  // --- Character (creature with helmet) ---
  const cx = CENTER + Math.cos(charAngle) * (RING_RADIUS - RING_WIDTH * 0.5)
  const cy = CENTER + Math.sin(charAngle) * (RING_RADIUS - RING_WIDTH * 0.5)

  // Character glow
  ctx.shadowColor = gameState.value === 'won' ? 'rgba(34,197,94,0.5)' : 'rgba(168,85,247,0.4)'
  ctx.shadowBlur = 12

  // Body (green blob)
  ctx.fillStyle = '#4ade80'
  ctx.beginPath()
  ctx.arc(cx, cy, CHAR_RADIUS * 0.6, 0, Math.PI * 2)
  ctx.fill()

  // Helmet (blue dome)
  ctx.fillStyle = '#60a5fa'
  ctx.beginPath()
  ctx.arc(cx, cy - 4, CHAR_RADIUS * 0.5, Math.PI, 0)
  ctx.fill()

  // Visor (darker blue)
  ctx.fillStyle = '#1e3a5f'
  ctx.beginPath()
  ctx.arc(cx, cy - 2, CHAR_RADIUS * 0.35, Math.PI + 0.2, -0.2)
  ctx.fill()

  ctx.shadowBlur = 0

  // --- Center multiplier text ---
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  if (gameState.value === 'idle') {
    ctx.fillStyle = 'rgba(255,255,255,0.7)'
    ctx.font = 'bold 16px -apple-system, sans-serif'
    ctx.fillText('Tap to play', CENTER, CENTER - 8)
    ctx.fillStyle = 'rgba(255,255,255,0.35)'
    ctx.font = '12px -apple-system, sans-serif'
    ctx.fillText('Press Play below', CENTER, CENTER + 14)
  } else {
    // Multiplier
    const color = gameState.value === 'won' ? '#4ade80' : gameState.value === 'lost' ? '#ef4444' : '#a855f7'
    ctx.fillStyle = color
    ctx.font = 'bold 30px -apple-system, sans-serif'
    ctx.fillText(`${multiplier.toFixed(2)}x`, CENTER, CENTER - 4)

    if (gameState.value === 'won') {
      ctx.fillStyle = '#4ade80'
      ctx.font = 'bold 16px -apple-system, sans-serif'
      ctx.fillText('Escaped!', CENTER, CENTER + 26)
      ctx.fillStyle = 'rgba(255,255,255,0.6)'
      ctx.font = '12px -apple-system, sans-serif'
      ctx.fillText(`+${(selectedBet.value * multiplier).toFixed(2)} 💎`, CENTER, CENTER + 46)
    } else if (gameState.value === 'lost') {
      ctx.fillStyle = '#ef4444'
      ctx.font = 'bold 16px -apple-system, sans-serif'
      ctx.fillText('Caught!', CENTER, CENTER + 26)
      ctx.fillStyle = 'rgba(255,255,255,0.5)'
      ctx.font = '12px -apple-system, sans-serif'
      ctx.fillText(`-${selectedBet.value.toFixed(2)} 💎`, CENTER, CENTER + 46)
    }
  }
}

onMounted(() => {
  draw()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (resultTimeout) clearTimeout(resultTimeout)
})
</script>
