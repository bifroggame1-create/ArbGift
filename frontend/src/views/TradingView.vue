<template>
  <div class="trading-view min-h-screen bg-[#0a0e27] pb-24 flex flex-col">
    <!-- Header -->
    <div class="px-4 pt-6 pb-4 flex items-center gap-4 bg-[#0e1d35] border-b border-white/5">
      <button
        @click="router.back()"
        class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all"
      >
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex-1">
        <div class="text-white text-xl font-bold">Trading</div>
        <div class="text-white/60 text-xs">Game #{{ currentGame?.game_number || '---' }}</div>
      </div>
      <div class="text-white/60 text-xs">
        {{ connectionStatus }}
      </div>
    </div>

    <!-- Chart Container -->
    <div class="flex-1 relative">
      <div ref="chartContainer" class="w-full h-full min-h-[300px]"></div>

      <!-- Multiplier Overlay -->
      <div class="absolute top-4 left-4 z-10">
        <div class="bg-black/60 backdrop-blur-sm rounded-xl px-4 py-2">
          <div class="text-white/60 text-xs">Current</div>
          <div class="text-3xl font-bold" :class="multiplierColor">
            {{ currentMultiplier.toFixed(2) }}x
          </div>
        </div>
      </div>

      <!-- Game Status Overlay -->
      <div v-if="gameStatus === 'pending'" class="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="text-center">
          <div class="text-white text-4xl font-bold mb-2">Starting...</div>
          <div class="text-white/60">Place your bets</div>
        </div>
      </div>

      <div v-if="gameStatus === 'crashed'" class="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="text-center">
          <div class="text-red-500 text-6xl font-bold mb-2">{{ crashPoint.toFixed(2) }}x</div>
          <div class="text-white/60">Crashed!</div>
          <div class="text-white/40 text-xs mt-2">Next game in {{ nextGameTimer }}s</div>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="px-4 py-4 bg-[#0e1d35] border-t border-white/5">
      <!-- Bet Amount Selector -->
      <div class="mb-4">
        <div class="text-white/60 text-sm mb-2">Bet Amount</div>
        <div class="flex gap-2">
          <button
            v-for="amount in betAmounts"
            :key="amount"
            @click="selectedBetAmount = amount"
            class="flex-1 py-3 rounded-lg font-bold transition-all"
            :class="selectedBetAmount === amount
              ? 'bg-blue-500 text-white'
              : 'bg-white/5 text-white/60 hover:bg-white/10'"
          >
            {{ amount }} 💎
          </button>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="grid grid-cols-2 gap-3">
        <!-- Place Bet Button -->
        <button
          v-if="!activeBet"
          @click="placeBet"
          :disabled="gameStatus !== 'pending' || isPlacingBet"
          class="py-4 rounded-xl font-bold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          :class="gameStatus === 'pending'
            ? 'bg-green-500 text-white hover:bg-green-600'
            : 'bg-white/10 text-white/40'"
        >
          {{ isPlacingBet ? 'Placing...' : 'Buy' }}
        </button>

        <!-- Cash Out Button -->
        <button
          v-else
          @click="cashOut"
          :disabled="gameStatus !== 'active' || isCashingOut"
          class="py-4 rounded-xl font-bold text-lg bg-yellow-500 text-white hover:bg-yellow-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isCashingOut ? 'Cashing...' : `Sell ${(selectedBetAmount * currentMultiplier).toFixed(2)} 💎` }}
        </button>

        <!-- Cancel Bet (during pending) -->
        <button
          v-if="activeBet && gameStatus === 'pending'"
          @click="cancelBet"
          class="py-4 rounded-xl font-bold text-lg bg-red-500 text-white hover:bg-red-600 transition-all"
        >
          Cancel
        </button>
      </div>

      <!-- Active Bet Info -->
      <div v-if="activeBet" class="mt-3 bg-white/5 rounded-lg p-3">
        <div class="flex items-center justify-between text-sm">
          <span class="text-white/60">Your Bet:</span>
          <span class="text-white font-bold">{{ activeBet.bet_amount }} 💎</span>
        </div>
        <div class="flex items-center justify-between text-sm mt-1">
          <span class="text-white/60">Potential Win:</span>
          <span class="text-green-400 font-bold">{{ (activeBet.bet_amount * currentMultiplier).toFixed(2) }} 💎</span>
        </div>
      </div>

      <!-- Hash Display -->
      <div class="mt-3 bg-black/20 rounded-lg p-2">
        <div class="text-white/40 text-xs text-center">
          Hash: {{ currentGame?.server_seed_hash?.substring(0, 20) || '...' }}...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { createChart, ColorType } from 'lightweight-charts'

const router = useRouter()

// Game state
const currentGame = ref<any>(null)
const currentMultiplier = ref(1.00)
const gameStatus = ref<'pending' | 'active' | 'crashed'>('pending')
const crashPoint = ref(0)
const nextGameTimer = ref(3)

// Bet state
const betAmounts = [0.5, 1, 5, 10]
const selectedBetAmount = ref(1)
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
const chartData = ref<any[]>([])

const multiplierColor = computed(() => {
  if (gameStatus.value === 'crashed') return 'text-red-500'
  if (currentMultiplier.value >= 2) return 'text-green-400'
  return 'text-blue-400'
})

// Initialize chart
const initChart = () => {
  if (!chartContainer.value) return

  chart = createChart(chartContainer.value, {
    layout: {
      background: { type: ColorType.Solid, color: 'transparent' },
      textColor: '#9CA3AF',
    },
    grid: {
      vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
      horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    rightPriceScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    timeScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
      timeVisible: true,
      secondsVisible: true,
    },
  })

  lineSeries = chart.addLineSeries({
    color: '#3B82F6',
    lineWidth: 3,
  })

  // Handle resize
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

// WebSocket connection
const connectWebSocket = () => {
  ws.value = new WebSocket('ws://localhost:8006/api/trading/ws')

  ws.value.onopen = () => {
    connectionStatus.value = 'Connected'
    console.log('WebSocket connected')
  }

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log('WS message:', data)

    if (data.type === 'game_update') {
      currentGame.value = { game_number: data.game_number, server_seed_hash: data.server_seed_hash || '' }
      currentMultiplier.value = data.multiplier
      gameStatus.value = data.status

      // Update chart
      const timestamp = Math.floor(Date.now() / 1000)
      chartData.value.push({ time: timestamp, value: data.multiplier })

      if (lineSeries && chartData.value.length > 0) {
        lineSeries.setData(chartData.value)
      }

      // Change line color based on multiplier
      if (lineSeries) {
        const color = data.multiplier >= 2 ? '#10B981' : '#3B82F6'
        lineSeries.applyOptions({ color })
      }
    }

    if (data.type === 'game_crashed') {
      gameStatus.value = 'crashed'
      crashPoint.value = data.crash_point
      currentMultiplier.value = data.crash_point

      // Clear active bet if lost
      if (activeBet.value) {
        activeBet.value = null
      }

      // Start countdown
      nextGameTimer.value = 3
      const interval = setInterval(() => {
        nextGameTimer.value--
        if (nextGameTimer.value <= 0) {
          clearInterval(interval)
          // Clear chart data for new game
          chartData.value = []
        }
      }, 1000)
    }

    if (data.type === 'cash_out' && data.user_id === 'current_user') {
      // Handle successful cash out
      activeBet.value = null
      isCashingOut.value = false
    }
  }

  ws.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    connectionStatus.value = 'Error'
  }

  ws.value.onclose = () => {
    connectionStatus.value = 'Disconnected'
    console.log('WebSocket disconnected')
    // Attempt reconnect
    setTimeout(connectWebSocket, 3000)
  }
}

// API calls
const placeBet = async () => {
  isPlacingBet.value = true
  try {
    const response = await fetch('http://localhost:8006/api/trading/bet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_number: currentGame.value?.game_number,
        bet_amount: selectedBetAmount.value,
      }),
    })

    if (response.ok) {
      const bet = await response.json()
      activeBet.value = bet
    }
  } catch (error) {
    console.error('Error placing bet:', error)
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
      body: JSON.stringify({
        bet_id: activeBet.value.id,
      }),
    })

    if (response.ok) {
      const result = await response.json()
      console.log('Cash out successful:', result)
      activeBet.value = null
    }
  } catch (error) {
    console.error('Error cashing out:', error)
  } finally {
    isCashingOut.value = false
  }
}

const cancelBet = () => {
  activeBet.value = null
}

onMounted(async () => {
  await nextTick()
  initChart()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
  if (chart) {
    chart.remove()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.trading-view {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
