<template>
  <div
    class="gift-card-wrapper"
    :class="{ 'selected': isSelected }"
    @click="handleClick"
  >
    <!-- Card with dynamic background color -->
    <div
      class="gift-card"
      :style="cardStyle"
    >
      <!-- 3D Model / Icon -->
      <div class="gift-model">
        <img
          v-if="gift.image_url"
          :src="gift.image_url"
          :alt="gift.name"
          class="model-image"
          loading="lazy"
        />
        <div v-else class="model-placeholder">
          🎁
        </div>
      </div>

      <!-- Selection Checkmark Overlay -->
      <div v-if="isSelected && selectable" class="selection-overlay">
        <div class="checkmark">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </div>

      <!-- Rarity Badge (Top Right) -->
      <div v-if="rarityBadge" class="rarity-badge" :class="`rarity-${rarity.toLowerCase()}`">
        {{ rarityBadge }}
      </div>
    </div>

    <!-- Gift Info -->
    <div class="gift-info">
      <div class="gift-name">{{ gift.name }}</div>
      <div class="gift-serial">{{ serialNumber }}</div>
    </div>

    <!-- Price Badge -->
    <div class="price-badge">
      <span class="price-value">{{ formattedPrice }}</span>
      <span class="price-icon">💎</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import type { Gift } from '../api/client'

interface Props {
  gift: Gift
  isSelected?: boolean
  selectable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  selectable: false,
})

const emit = defineEmits(['click', 'select'])

const { hapticImpact } = useTelegram()

// Rarity computation
const rarity = computed(() => {
  // Try to determine rarity from gift attributes
  const r = props.gift.rarity || 'common'
  return String(r).toLowerCase()
})

type RarityType = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary' | 'mythic'

const rarityConfig: Record<RarityType, { gradient: string; badge: string | null }> = {
  common: {
    gradient: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
    badge: null,
  },
  uncommon: {
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    badge: 'Uncommon',
  },
  rare: {
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    badge: 'Rare',
  },
  epic: {
    gradient: 'linear-gradient(135deg, #a855f7 0%, #9333ea 100%)',
    badge: 'Epic',
  },
  legendary: {
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    badge: 'Legendary',
  },
  mythic: {
    gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
    badge: 'Mythic',
  },
}

const cardStyle = computed(() => {
  const config = rarityConfig[rarity.value as RarityType] || rarityConfig.common
  return {
    background: config.gradient
  }
})

const rarityBadge = computed(() => {
  const config = rarityConfig[rarity.value as RarityType] || rarityConfig.common
  return config.badge
})

const serialNumber = computed(() => {
  // Extract serial from address or use ID
  if (props.gift.address) {
    // Get last 6 chars of address as serial
    const addr = props.gift.address
    return `#${addr.slice(-6).toUpperCase()}`
  }
  return `#${String(props.gift.id).padStart(6, '0')}`
})

const formattedPrice = computed(() => {
  const price = props.gift.min_price_ton || 0
  return parseFloat(String(price)).toFixed(2)
})

const handleClick = () => {
  hapticImpact('light')
  emit('click', props.gift)
  if (props.selectable) {
    emit('select', props.gift)
  }
}
</script>

<style scoped>
.gift-card-wrapper {
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease;
  user-select: none;
}

.gift-card-wrapper:hover {
  transform: translateY(-4px);
}

.gift-card-wrapper:active {
  transform: scale(0.97);
}

.gift-card-wrapper.selected {
  animation: pulse-selection 0.3s ease;
}

@keyframes pulse-selection {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(0.95); }
}

.gift-card {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.gift-model {
  width: 70%;
  height: 70%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.model-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

.model-placeholder {
  font-size: 4rem;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

.selection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(16, 185, 129, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  z-index: 10;
  animation: fade-in 0.2s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.checkmark {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #10b981;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.rarity-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  backdrop-filter: blur(8px);
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.rarity-uncommon {
  background: rgba(16, 185, 129, 0.3);
  color: #d1fae5;
  border: 1px solid rgba(16, 185, 129, 0.5);
}

.rarity-rare {
  background: rgba(59, 130, 246, 0.3);
  color: #dbeafe;
  border: 1px solid rgba(59, 130, 246, 0.5);
}

.rarity-epic {
  background: rgba(168, 85, 247, 0.3);
  color: #f3e8ff;
  border: 1px solid rgba(168, 85, 247, 0.5);
}

.rarity-legendary {
  background: rgba(245, 158, 11, 0.3);
  color: #fef3c7;
  border: 1px solid rgba(245, 158, 11, 0.5);
}

.rarity-mythic {
  background: rgba(236, 72, 153, 0.3);
  color: #fce7f3;
  border: 1px solid rgba(236, 72, 153, 0.5);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0%, 100% { box-shadow: 0 0 10px rgba(236, 72, 153, 0.5); }
  50% { box-shadow: 0 0 20px rgba(236, 72, 153, 0.8); }
}

.gift-info {
  margin-top: 8px;
  text-align: center;
}

.gift-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gift-serial {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'Monaco', 'Courier New', monospace;
}

.price-badge {
  margin-top: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  padding: 6px 12px;
  border-radius: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.price-value {
  color: white;
  font-size: 13px;
}

.price-icon {
  font-size: 11px;
}
</style>
