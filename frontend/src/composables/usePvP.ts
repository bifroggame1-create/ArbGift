/**
 * PvP Game composable — реалтайм рулетка на гифтах.
 */
import { ref, computed, onUnmounted } from 'vue'
import {
  pvpCreateRoom,
  pvpPlaceBet,
  pvpGetRoom,
  pvpListRooms,
  pvpGetInventory,
  type PvPRoomState,
  type PvPRoom,
  type PvPSpinResult,
  type InventoryNFT,
} from '@/api/client'

const PVP_WS_BASE = import.meta.env.VITE_PVP_WS_URL || import.meta.env.VITE_PVP_URL?.replace('http', 'ws') || 'ws://localhost:8009'

export function usePvP() {
  // State
  const rooms = ref<PvPRoom[]>([])
  const currentRoom = ref<PvPRoomState | null>(null)
  const inventory = ref<InventoryNFT[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const countdownRemaining = ref(0)
  const spinResult = ref<PvPSpinResult | null>(null)

  // WebSocket
  let ws: WebSocket | null = null
  let countdownInterval: ReturnType<typeof setInterval> | null = null

  // Events emitted via callbacks
  const onBetPlaced = ref<((data: any) => void) | null>(null)
  const onCountdownStart = ref<((seconds: number) => void) | null>(null)
  const onSpinStart = ref<(() => void) | null>(null)
  const onSpinResult = ref<((result: PvPSpinResult) => void) | null>(null)

  // Computed
  const isConnected = computed(() => ws?.readyState === WebSocket.OPEN)

  // ─── WebSocket ───────────────────────────────────────────────────

  const connectWS = (roomCode: string) => {
    disconnectWS()

    ws = new WebSocket(`${PVP_WS_BASE}/ws/pvp/${roomCode}`)

    ws.onopen = () => {
      // Send pings to keep alive
      const pingInterval = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) {
          ws.send('ping')
        } else {
          clearInterval(pingInterval)
        }
      }, 30000)
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        handleMessage(msg, roomCode)
      } catch { /* ignore non-JSON */ }
    }

    ws.onerror = () => {
      error.value = 'WebSocket connection error'
    }

    ws.onclose = () => {
      // Auto-reconnect after 3 seconds
      setTimeout(() => {
        if (currentRoom.value && currentRoom.value.status !== 'finished') {
          connectWS(roomCode)
        }
      }, 3000)
    }
  }

  const disconnectWS = () => {
    if (ws) {
      ws.onclose = null // prevent auto-reconnect
      ws.close()
      ws = null
    }
    if (countdownInterval) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
  }

  const handleMessage = (msg: { type: string; data: any }, roomCode: string) => {
    switch (msg.type) {
      case 'bet_placed':
        if (currentRoom.value) {
          currentRoom.value.total_pool_ton = msg.data.total_pool_ton
          currentRoom.value.total_bets = msg.data.total_bets
          currentRoom.value.total_players = msg.data.total_players
          // Refresh full state
          fetchRoom(roomCode)
        }
        onBetPlaced.value?.(msg.data)
        break

      case 'countdown_start':
        if (currentRoom.value) {
          currentRoom.value.status = 'countdown'
        }
        countdownRemaining.value = msg.data.countdown_seconds
        startCountdownTimer()
        onCountdownStart.value?.(msg.data.countdown_seconds)
        break

      case 'countdown_update':
        countdownRemaining.value = msg.data.remaining_seconds
        break

      case 'spin_start':
        if (currentRoom.value) {
          currentRoom.value.status = 'spinning'
        }
        if (countdownInterval) {
          clearInterval(countdownInterval)
          countdownInterval = null
        }
        onSpinStart.value?.()
        break

      case 'spin_result':
        if (currentRoom.value) {
          currentRoom.value.status = 'finished'
        }
        spinResult.value = msg.data as PvPSpinResult
        onSpinResult.value?.(msg.data)
        break

      case 'room_cancelled':
        if (currentRoom.value) {
          currentRoom.value.status = 'cancelled'
        }
        break
    }
  }

  const startCountdownTimer = () => {
    if (countdownInterval) clearInterval(countdownInterval)
    countdownInterval = setInterval(() => {
      if (countdownRemaining.value > 0) {
        countdownRemaining.value--
      } else {
        if (countdownInterval) clearInterval(countdownInterval)
      }
    }, 1000)
  }

  // ─── API Calls ───────────────────────────────────────────────────

  const fetchRooms = async (status?: string) => {
    loading.value = true
    error.value = null
    try {
      const data = await pvpListRooms(status)
      rooms.value = data.rooms
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch rooms'
    } finally {
      loading.value = false
    }
  }

  const fetchRoom = async (roomCode: string) => {
    loading.value = true
    error.value = null
    try {
      currentRoom.value = await pvpGetRoom(roomCode)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch room'
    } finally {
      loading.value = false
    }
  }

  const createRoom = async (params: {
    room_type?: string
    min_bet_ton?: number
    max_players?: number
  }) => {
    loading.value = true
    error.value = null
    try {
      const data = await pvpCreateRoom(params)
      return data
    } catch (e: any) {
      error.value = e.message || 'Failed to create room'
      return null
    } finally {
      loading.value = false
    }
  }

  const placeBet = async (
    roomCode: string,
    betData: {
      user_id: number
      user_telegram_id: number
      user_name: string
      user_avatar?: string
      gift_address: string
      gift_name: string
      gift_image_url?: string
      gift_value_ton: number
    },
    walletAddress?: string,
  ) => {
    loading.value = true
    error.value = null
    try {
      const result = await pvpPlaceBet(roomCode, betData, walletAddress)
      return result
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Failed to place bet'
      return null
    } finally {
      loading.value = false
    }
  }

  const fetchInventory = async (walletAddress: string) => {
    loading.value = true
    error.value = null
    try {
      inventory.value = await pvpGetInventory(walletAddress)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch inventory'
    } finally {
      loading.value = false
    }
  }

  // Cleanup on unmount
  onUnmounted(() => {
    disconnectWS()
  })

  return {
    // State
    rooms,
    currentRoom,
    inventory,
    loading,
    error,
    countdownRemaining,
    spinResult,
    isConnected,

    // Events
    onBetPlaced,
    onCountdownStart,
    onSpinStart,
    onSpinResult,

    // Methods
    connectWS,
    disconnectWS,
    fetchRooms,
    fetchRoom,
    createRoom,
    placeBet,
    fetchInventory,
  }
}
