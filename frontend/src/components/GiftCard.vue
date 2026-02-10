<template>
  <div
    class="gift-card"
    :style="cardStyle"
    @click="handleClick"
  >
    <!-- Image area with backdrop gradient -->
    <div class="gift-card__image">
      <LottieGift
        v-if="lottieUrl"
        :src="lottieUrl"
        :fallback-src="gift.image_url"
        :alt="gift.name"
        :size="imageSize"
        class="gift-card__lottie"
      />
      <img
        v-else-if="gift.image_url && !imgError"
        :src="gift.image_url"
        :alt="gift.name"
        loading="lazy"
        draggable="false"
        @error="imgError = true"
      />
      <div v-else class="gift-card__placeholder">
        <span class="gift-card__placeholder-emoji">🎁</span>
      </div>

      <!-- Market source badge -->
      <div v-if="gift.lowest_price_market" class="gift-card__source">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M2 12h20"/>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>
      </div>

      <!-- Selection checkbox -->
      <div
        v-if="selectable"
        class="gift-card__checkbox"
        :class="{ 'gift-card__checkbox--selected': isSelected }"
      >
        <svg v-if="isSelected" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
        </svg>
      </div>
    </div>

    <!-- Info: name + serial on one line -->
    <div class="gift-card__meta">
      <span class="gift-card__name">{{ gift.name }}</span>
      <span class="gift-card__serial">#{{ serialNumber }}</span>
    </div>

    <!-- Price row: price pill + cart button -->
    <div class="gift-card__actions">
      <button v-if="formattedPrice" class="gift-card__price" @click.stop="handleBuy">
        <svg class="gift-card__ton" width="12" height="12" viewBox="0 0 16 16" fill="none">
          <path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z" fill="currentColor"/>
        </svg>
        <span>{{ formattedPrice }}</span>
      </button>
      <button class="gift-card__cart" @click.stop="handleBuy">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
          <path d="M3 6h18"/>
          <path d="M16 10a4 4 0 0 1-8 0"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Gift } from '../api/client'
import { useTelegram } from '../composables/useTelegram'
import { getBackdropGradient } from '../utils/backdropColors'
import LottieGift from './LottieGift.vue'

const props = defineProps<{
  gift: Gift
  selectable?: boolean
  isSelected?: boolean
}>()

const emit = defineEmits<{
  click: [gift: Gift]
  buy: [gift: Gift]
  select: [gift: Gift]
}>()

const { hapticImpact } = useTelegram()

const imgError = ref(false)

// Animation URL — from backend fields
const lottieUrl = computed(() => {
  if (props.gift.animation_url) return props.gift.animation_url
  if (props.gift.lottie_url) return props.gift.lottie_url
  const img = props.gift.image_url
  if (img && img.includes('nft.fragment.com/gift/')) {
    return img.replace(/\.(webp|jpg|png|medium\.jpg|large\.jpg|small\.jpg)$/i, '.lottie.json')
  }
  return null
})

// Image size for lottie — 2-column grid now
const imageSize = computed(() => {
  return Math.round(Math.min(window.innerWidth / 2 - 20, 180))
})

// Serial number
const serialNumber = computed(() => {
  if (props.gift.tg_id) return props.gift.tg_id
  if (props.gift.index) return props.gift.index
  return props.gift.id
})

// Formatted price
const formattedPrice = computed(() => {
  const price = props.gift.lowest_price_ton || props.gift.min_price_ton || props.gift.price || 0
  const num = Number(price)
  if (num <= 0) return null
  return num.toFixed(2).replace(/\.?0+$/, '')
})

// Card backdrop gradient
const cardStyle = computed(() => {
  return { '--card-bg': getBackdropGradient(props.gift.backdrop) }
})

const handleClick = () => {
  hapticImpact('light')
  if (props.selectable) {
    emit('select', props.gift)
  } else {
    emit('click', props.gift)
  }
}

const handleBuy = () => {
  hapticImpact('medium')
  emit('buy', props.gift)
}
</script>

<style scoped>
.gift-card {
  --card-bg: linear-gradient(180deg, #3A3A3A 0%, #282727 100%);
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  overflow: hidden;
  background: #1a1a1a;
  -webkit-tap-highlight-color: transparent;
}

/* ---- Image area ---- */
.gift-card__image {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-bg);
  overflow: hidden;
}

.gift-card__lottie {
  width: 75%;
  height: 75%;
  filter: drop-shadow(0 4px 16px rgba(0, 0, 0, 0.4));
}

.gift-card__image img {
  width: 75%;
  height: 75%;
  object-fit: contain;
  filter: drop-shadow(0 4px 16px rgba(0, 0, 0, 0.4));
}

.gift-card__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.gift-card__placeholder-emoji {
  font-size: 48px;
  opacity: 0.35;
}

/* Market source badge (globe icon) */
.gift-card__source {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

/* ---- Meta: name + serial ---- */
.gift-card__meta {
  display: flex;
  align-items: baseline;
  gap: 6px;
  padding: 10px 10px 4px;
  min-height: 0;
}

.gift-card__name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 1;
  min-width: 0;
}

.gift-card__serial {
  font-size: 12px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.2;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ---- Actions: price + cart ---- */
.gift-card__actions {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px 10px;
}

.gift-card__price {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  flex: 1;
  padding: 8px 12px;
  border-radius: 10px;
  border: none;
  background: #2681FF;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.15s;
}

.gift-card__price:active {
  background: #1a6ae0;
}

.gift-card__ton {
  flex-shrink: 0;
  opacity: 0.85;
}

.gift-card__cart {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.15s, color 0.15s;
}

.gift-card__cart:active {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* ---- Selection checkbox ---- */
.gift-card__checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.45);
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.gift-card__checkbox--selected {
  background: #2681FF;
  border-color: #2681FF;
}

.gift-card__checkbox svg {
  color: #fff;
}
</style>
