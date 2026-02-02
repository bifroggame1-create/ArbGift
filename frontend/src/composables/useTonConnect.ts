/**
 * TON Connect integration composable
 *
 * Provides wallet connection for TON blockchain.
 */
import { ref, computed } from 'vue'

// TonConnect types (inline to avoid module resolution issues)
interface WalletAccount {
  address: string
  chain: string
}

interface WalletDevice {
  appName: string
  platform: string
}

interface ConnectedWallet {
  account: WalletAccount
  device: WalletDevice
  imageUrl?: string
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let tonConnectUI: any = null

// Reactive state
const wallet = ref<ConnectedWallet | null>(null)
const isConnected = ref(false)
const isConnecting = ref(false)

export function useTonConnect() {
  // Computed properties
  const address = computed(() => {
    if (!wallet.value) return null
    return wallet.value.account.address
  })

  const shortAddress = computed(() => {
    if (!address.value) return null
    const addr = address.value
    return `${addr.slice(0, 4)}...${addr.slice(-4)}`
  })

  const chain = computed(() => {
    if (!wallet.value) return null
    return wallet.value.account.chain
  })

  const walletInfo = computed(() => {
    if (!wallet.value) return null
    return {
      name: wallet.value.device.appName,
      icon: wallet.value.imageUrl,
      platform: wallet.value.device.platform,
    }
  })

  // Initialize TON Connect (async to handle dynamic import)
  const init = async (botUsername?: string) => {
    if (tonConnectUI) return tonConnectUI

    try {
      // Dynamic import for @tonconnect/ui
      const { TonConnectUI } = await import('@tonconnect/ui')
      const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const options: any = {
        manifestUrl,
        uiPreferences: {
          theme: 'DARK'
        }
      }
      tonConnectUI = new TonConnectUI(options)

      // Set TMA return URL if in Telegram Mini App
      if (window.Telegram?.WebApp) {
        const returnUrl = `https://t.me/${botUsername || 'giftmarket_bot'}/app`
        tonConnectUI.uiOptions = {
          twaReturnUrl: returnUrl
        }
        console.log('TonConnect initialized for TMA with return URL:', returnUrl)
      }

      // Subscribe to wallet changes
      tonConnectUI.onStatusChange((w: ConnectedWallet | null) => {
        wallet.value = w
        isConnected.value = !!w
        isConnecting.value = false
      })

      // Check if already connected
      if (tonConnectUI.wallet) {
        wallet.value = tonConnectUI.wallet
        isConnected.value = true
      }

      return tonConnectUI
    } catch (error) {
      console.warn('TonConnect UI not available:', error)
      return null
    }
  }

  // Connect wallet
  const connect = async () => {
    if (!tonConnectUI) {
      throw new Error('TonConnect not initialized')
    }

    isConnecting.value = true

    try {
      await tonConnectUI.openModal()
    } catch (error) {
      isConnecting.value = false
      throw error
    }
  }

  // Disconnect wallet
  const disconnect = async () => {
    if (!tonConnectUI) return

    await tonConnectUI.disconnect()
    wallet.value = null
    isConnected.value = false
  }

  // Send transaction
  const sendTransaction = async (params: {
    validUntil: number
    messages: Array<{
      address: string
      amount: string
      payload?: string
    }>
  }) => {
    if (!tonConnectUI || !isConnected.value) {
      throw new Error('Wallet not connected')
    }

    return await tonConnectUI.sendTransaction(params)
  }

  // Transfer NFT (gift)
  const transferNFT = async (params: {
    nftAddress: string
    toAddress: string
    amount?: string // usually 0.05 TON for gas
    forwardPayload?: string
  }) => {
    if (!tonConnectUI || !address.value) {
      throw new Error('Wallet not connected')
    }

    const { nftAddress, amount = '50000000', forwardPayload } = params

    // Build NFT transfer message
    const messages = [
      {
        address: nftAddress,
        amount,
        payload: forwardPayload,
      },
    ]

    return await sendTransaction({
      validUntil: Math.floor(Date.now() / 1000) + 600, // 10 min
      messages,
    })
  }

  // Get UI instance for custom operations
  const getUI = () => tonConnectUI

  return {
    // State
    wallet,
    isConnected,
    isConnecting,
    address,
    shortAddress,
    chain,
    walletInfo,

    // Methods
    init,
    connect,
    disconnect,
    sendTransaction,
    transferNFT,
    getUI,
  }
}
