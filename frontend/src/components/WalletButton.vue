<template>
  <button
    class="wallet-btn"
    :class="{ connected: isConnected }"
    @click="handleClick"
    :disabled="isConnecting"
  >
    <div class="wallet-content">
      <!-- Wallet icon -->
      <div class="wallet-icon">
        <img
          v-if="walletInfo?.icon"
          :src="walletInfo.icon"
          :alt="walletInfo.name"
          class="wallet-logo"
        />
        <svg
          v-else
          class="default-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
      </div>

      <!-- Button text -->
      <span class="wallet-text">
        <template v-if="isConnecting">
          Connecting...
        </template>
        <template v-else-if="isConnected">
          {{ shortAddress }}
        </template>
        <template v-else>
          Connect
        </template>
      </span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTonConnect } from '../composables/useTonConnect'
import { useTelegram } from '../composables/useTelegram'

const {
  isConnected,
  isConnecting,
  shortAddress,
  walletInfo,
  init,
  connect,
  disconnect,
} = useTonConnect()

const { hapticImpact } = useTelegram()

onMounted(() => {
  // Initialize with bot username
  init('giftmarket_bot')
})

const handleClick = async () => {
  hapticImpact('light')

  if (isConnected.value) {
    await disconnect()
  } else {
    await connect()
  }
}
</script>

<style scoped>
.wallet-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #1689ff 0%, #0066cc 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;
}

.wallet-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 137, 255, 0.4);
}

.wallet-btn:active {
  transform: translateY(0);
}

.wallet-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.wallet-btn.connected {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.wallet-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wallet-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wallet-logo {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  object-fit: cover;
}

.default-icon {
  width: 16px;
  height: 16px;
}

.wallet-text {
  white-space: nowrap;
}
</style>
