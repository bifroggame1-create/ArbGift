<template>
  <div class="trading-view min-h-screen flex flex-col" style="background: #000; padding-bottom: 16px;">
    <div class="px-3 pt-3 flex flex-col gap-2">
      <!-- Tournament Banner -->
      <div class="rounded-xl px-4 py-2.5 flex items-center justify-between"
        style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #60a5fa 100%);">
        <span class="text-white font-bold text-sm">Trading Mega Tournament</span>
        <span class="text-white/70 text-xs font-mono">16:04:57:44</span>
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
          <button class="w-9 h-9 rounded-xl flex items-center justify-center" style="background: rgba(255,255,255,0.06);">
            <svg class="w-4 h-4" fill="none" stroke="rgba(255,255,255,0.45)" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
          </button>
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

    <!-- Chart Card -->
    <div class="mx-3 mt-2 rounded-2xl overflow-hidden relative" style="background: #0f172a; height: 240px;">
      <div class="absolute top-3 left-3 z-10 flex items-center gap-1.5">
        <div class="w-2 h-2 rounded-full" :style="{ background: connectionStatus === 'Connected' ? '#4ade80' : 'rgba(255,255,255,0.25)' }"></div>
        <span class="text-xs" :style="{ color: connectionStatus === 'Connected' ? 'rgba(74,222,128,0.7)' : 'rgba(255,255,255,0.25)' }">{{ connectionStatus }}</span>
      </div>

      <!-- Active game multiplier overlay -->
      <div v-if="gameStatus === 'active'" class="absolute top-1/2 left-1/2 z-5 pointer-events-none" style="transform: translate(-50%, -50%);">
        <div class="text-5xl font-bold text-center" :style="{ color: currentMultiplier >= 2 ? '#4ade80' : '#60a5fa' }">
          {{ currentMultiplier.toFixed(2) }}x
        </div>
      </div>

      <!-- Crashed overlay -->
      <div v-if="gameStatus === 'crashed'" class="absolute inset-0 flex flex-col items-center justify-center z-10" style="background: rgba(0,0,0,0.65); backdrop-filter: blur(2px);">
        <div class="text-red-500 text-6xl font-bold">{{ crashPoint.toFixed(2) }}x</div>
        <div class="text-white/40 text-sm mt-1">Crashed!</div>
        <div class="text-white/25 text-xs mt-1.5">Next game in {{ nextGameTimer }}s</div>
      </div>

      <div ref="chartContainer" class="w-full h-full"></div>
    </div>

    <!-- Traders Card -->
    <div class="mx-3 mt-2 rounded-xl px-4 py-3" style="background: #0f172a;">
      <div class="flex items-center gap-2">
        <span class="text-white font-bold text-sm">Traders</span>
        <span class="text-white/25 text-sm">({{ traderCount }})</span>
      </div>
      <div class="flex items-center justify-between mt-1.5">
        <span class="text-white/25 text-xs">Game #{{ gameNumber }}</span>
        <div class="flex items-center gap-1">
          <span class="text-white/20 text-xs">⏱</span>
          <span class="text-white/25 text-xs">Hash: {{ currentHash }}</span>
        </div>
      </div>
    </div>

    <!-- Bottom Controls -->
    <div class="px-3 pt-3">
      <!-- Bet pills -->
      <div class="flex gap-2 mb-3">
        <button
          v-for="amount in betAmounts"
          :key="amount"
          @click="selectedBetAmount = amount"
          class="flex-1 py-2 rounded-lg font-bold flex items-center justify-center gap-1 transition-all"
          :style="selectedBetAmount === amount
            ? { background: 'rgba(59,130,246,0.18)', border: '1px solid rgba(59,130,246,0.35)' }
            : { background: 'rgba(255,255,255,0.06)', border: '1px solid transparent' }"
        >
          <span class="text-white/75 text-sm">{{ amount }}</span>
          <span class="text-white/30 text-xs">▼</span>
        </button>
      </div>

      <!-- Action Row -->
      <div class="flex items-center gap-2">
        <!-- Swap -->
        <button class="flex flex-col items-center gap-0.5">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: rgba(255,255,255,0.06);">
            <div class="w-5 h-5 rounded-full flex items-center justify-center" style="background: #3b82f6;">
              <span class="text-white text-xs font-bold">▼</span>
            </div>
          </div>
          <span class="text-white/35 text-xs">Swap ☆</span>
        </button>

        <!-- Buy / Sell stack -->
        <div class="flex-1 flex flex-col gap-1.5">
          <button
            @click="placeBet"
            :disabled="gameStatus !== 'pending' || isPlacingBet"
            class="w-full py-3 rounded-xl font-bold text-sm text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style="background: linear-gradient(135deg, #16a34a, #22c55e);"
          >
            {{ isPlacingBet ? 'Placing...' : `Buy ${selectedBetAmount} TON` }}
          </button>
          <button
            @click="cashOut"
            :disabled="!activeBet || gameStatus !== 'active' || isCashingOut"
            class="w-full py-2 rounded-xl font-bold text-xs transition-all disabled:opacity-25 disabled:cursor-not-allowed"
            style="background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.45);"
          >
            {{ isCashingOut ? 'Cashing...' : activeBet ? `Sell ${(activeBet.bet_amount * currentMultiplier).toFixed(2)} TON` : 'Sell 100%' }}
          </button>
        </div>

        <!-- Deposit -->
        <button class="flex flex-col items-center gap-0.5">
          <div class="w-10 h-10 rounded-full flex items-center justify-center text-white/50 text-lg" style="background: rgba(255,255,255,0.10);">+</div>
          <span class="text-white/35 text-xs">Deposit</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { createChart, ColorType } from 'lightweight-charts'

// State
const balance = ref(4.16)
const currentMultiplier = ref(1.00)
const gameStatus = ref<'pending' | 'active' | 'crashed'>('pending')
const crashPoint = ref(0)
const nextGameTimer = ref(5)
const gameNumber = ref(28392)
const traderCount = ref(0)
const currentHash = ref('3d07...f8da')

// Bet state
const betAmounts = [0.5, 1, 5, 10]
const selectedBetAmount = ref(0.5)
const activeBet = ref<any>(null)
const isPlacingBet = ref(false)
const isCashingOut = ref(false)

// WebSocket
const ws = ref<WebSocket | null>(null)
const connectionStatus = ref('Connecting...')

// Chart
const chartContainer = ref<HTMLElement | null>(null)
let chart: any = null
let lineSeries: any = null
const chartData: { time: number; value: number }[] = []

const initChart = () => {
  if (!chartContainer.value) return

  chart = createChart(chartContainer.value, {
    layout: {
      background: { type: ColorType.Solid, color: 'transparent' },
      textColor: 'rgba(255,255,255,0.3)',
    },
    grid: {
      vertLines: { color: 'rgba(255,255,255,0.04)' },
      horzLines: { color: 'rgba(255,255,255,0.06)' },
    },
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    rightPriceScale: {
      borderColor: 'transparent',
      textColor: 'rgba(255,255,255,0.3)',
    },
    timeScale: {
      visible: false,
    },
  })

  lineSeries = chart.addLineSeries({
    color: '#3b82f6',
    lineWidth: 2.5,
    crosshairMarkerVisible: false,
  })

  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth,
      height: chartContainer.value.clientHeight,
    })
  }
}

const connectWebSocket = () => {
  ws.value = new WebSocket('ws://localhost:8006/api/trading/ws')

  ws.value.onopen = () => {
    connectionStatus.value = 'Connected'
  }

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'game_update') {
      gameNumber.value = data.game_number
      currentMultiplier.value = data.multiplier
      gameStatus.value = data.status
      if (data.server_seed_hash) currentHash.value = data.server_seed_hash

      const timestamp = Math.floor(Date.now() / 1000)
      chartData.push({ time: timestamp, value: data.multiplier })

      if (lineSeries && chartData.length > 0) {
        lineSeries.setData([...chartData])
      }

      if (lineSeries) {
        lineSeries.applyOptions({ color: data.multiplier >= 2 ? '#10B981' : '#3B82F6' })
      }
    }

    if (data.type === 'game_crashed') {
      gameStatus.value = 'crashed'
      crashPoint.value = data.crash_point
      currentMultiplier.value = data.crash_point

      if (activeBet.value) activeBet.value = null

      nextGameTimer.value = 5
      const interval = setInterval(() => {
        nextGameTimer.value--
        if (nextGameTimer.value <= 0) {
          clearInterval(interval)
          chartData.length = 0
          gameStatus.value = 'pending'
        }
      }, 1000)
    }
  }

  ws.value.onerror = () => { connectionStatus.value = 'Error' }
  ws.value.onclose = () => {
    connectionStatus.value = 'Disconnected'
    setTimeout(connectWebSocket, 3000)
  }
}

const placeBet = async () => {
  isPlacingBet.value = true
  try {
    const response = await fetch('http://localhost:8006/api/trading/bet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_number: gameNumber.value,
        bet_amount: selectedBetAmount.value,
      }),
    })
    if (response.ok) {
      activeBet.value = await response.json()
      balance.value -= selectedBetAmount.value
    }
  } catch (e) {
    console.error('Bet error:', e)
  } finally {
    isPlacingBet.value = false
  }
}

const cashOut = async () => {
  if (!activeBet.value) return
  isCashingOut.value = true
  try {
    const response = await fetch('http://localhost:8006/api/trading/cashout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bet_id: activeBet.value.id }),
    })
    if (response.ok) {
      const result = await response.json()
      balance.value += result.payout || (activeBet.value.bet_amount * currentMultiplier.value)
      activeBet.value = null
    }
  } catch (e) {
    console.error('Cashout error:', e)
  } finally {
    isCashingOut.value = false
  }
}

onMounted(async () => {
  await nextTick()
  initChart()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws.value) ws.value.close()
  if (chart) chart.remove()
  window.removeEventListener('resize', handleResize)
})
</script>
