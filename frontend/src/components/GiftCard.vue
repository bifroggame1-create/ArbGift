<template>
  <div
    class="gift-card gift-card-appear base-active-btn"
    :style="cardStyle"
    @click="handleClick"
  >
    <!-- Image area: square, backdrop-colored background -->
    <div class="gift-card__image">
      <!-- Lottie animation from Fragment CDN -->
      <LottieGift
        v-if="lottieUrl"
        :src="lottieUrl"
        :fallback-src="gift.image_url"
        :alt="gift.name"
        :size="imageSize"
        class="gift-card__lottie"
      />
      <!-- Static image fallback -->
      <img
        v-else-if="gift.image_url"
        :src="gift.image_url"
        :alt="gift.name"
        loading="lazy"
        draggable="false"
      />
      <div v-else class="gift-card__placeholder">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <path
            d="M38.17 3.01H9.827C4.615 3.01 1.312 8.636 3.934 13.18L21.427 43.5C22.569 45.48 25.43 45.48 26.571 43.5L44.068 13.18C46.686 8.644 43.383 3.01 38.175 3.01H38.17ZM21.413 34.408L17.603 27.035L8.411 10.594C7.805 9.542 8.554 8.194 9.823 8.194H21.41V34.412L21.413 34.408ZM39.58 10.591L30.391 27.039L26.582 34.408V8.19H38.168C39.437 8.19 40.187 9.539 39.58 10.591Z"
            fill="rgba(255,255,255,0.15)"
          />
        </svg>
      </div>
    </div>

    <!-- Info section -->
    <div class="gift-card__info">
      <div class="gift-card__name">{{ gift.name }}</div>
      <div class="gift-card__serial">#{{ serialNumber }}</div>

      <!-- Price pill -->
      <button class="gift-card__price" @click.stop="handleBuy">
        <svg
          class="gift-card__ton-icon"
          width="12"
          height="12"
          viewBox="0 0 16 16"
          fill="none"
        >
          <path
            d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z"
            fill="currentColor"
          />
        </svg>
        <span>{{ formattedPrice }}</span>
      </button>
    </div>

    <!-- Selection checkbox (bulk buy mode) -->
    <div
      v-if="selectable"
      class="gift-card__checkbox"
      :class="{ 'gift-card__checkbox--selected': isSelected }"
    >
      <svg
        v-if="isSelected"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Gift } from '../api/client'
import { useTelegram } from '../composables/useTelegram'
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

// Lottie animation URL — from backend or derived from image_url (Fragment CDN pattern)
const lottieUrl = computed(() => {
  // Direct lottie_url from API
  if (props.gift.lottie_url) return props.gift.lottie_url
  // Derive from Fragment CDN image URL:  *.webp → *.lottie.json
  const img = props.gift.image_url
  if (img && img.includes('nft.fragment.com/gift/')) {
    return img.replace(/\.(webp|jpg|png|medium\.jpg|large\.jpg|small\.jpg)$/i, '.lottie.json')
  }
  return null
})

// Card image size for lottie (responsive)
const imageSize = computed(() => {
  // Grid cards are ~1/3 viewport, image area is square aspect-ratio
  return Math.round(Math.min(window.innerWidth / 3 - 16, 140))
})

// Serial number from tg_id or id
const serialNumber = computed(() => {
  if (props.gift.tg_id) return props.gift.tg_id
  return props.gift.id
})

// Formatted price
const formattedPrice = computed(() => {
  const price = props.gift.min_price_ton || props.gift.price || 0
  return Number(price).toFixed(2).replace(/\.?0+$/, '')
})

// Card style based on collection/rarity (backdrop gradient)
const cardStyle = computed(() => {
  const bgColors: Record<string, string> = {
    'Instant Ramen': 'linear-gradient(180deg, #E8D5B7 0%, #C4A77D 100%)',
    'Lol Pop': 'linear-gradient(180deg, #A8D8FF 0%, #5BA3D9 100%)',
    'Hypno Lollipop': 'linear-gradient(180deg, #D4B8E8 0%, #9B6DC6 100%)',
    'Eternal Candle': 'linear-gradient(180deg, #4A4A4A 0%, #2A2A2A 100%)',
    'Bling Binky': 'linear-gradient(180deg, #FFD700 0%, #FFA500 100%)',
    'Pet Snake': 'linear-gradient(180deg, #90EE90 0%, #228B22 100%)',
    'Happy Brownie': 'linear-gradient(180deg, #D2B48C 0%, #8B4513 100%)',
    'Fresh Socks': 'linear-gradient(180deg, #F5DEB3 0%, #DEB887 100%)',
    'Ice Cream': 'linear-gradient(180deg, #FFB6C1 0%, #FF69B4 100%)',
    'default': 'linear-gradient(180deg, #3A3A3A 0%, #282727 100%)',
  }

  const bg = bgColors[props.gift.name] || bgColors['default']
  return { '--card-bg': bg }
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
  cursor: pointer;
  background: var(--mb-bg, #0C0C0C);
  transition:
    filter var(--mb-duration-fast, 0.16s) ease,
    transform var(--mb-duration-normal, 0.22s) var(--mb-ease-spring, cubic-bezier(0.34, 1.56, 0.64, 1));
  will-change: transform;
}

.gift-card:hover {
  filter: brightness(1.08);
  transform: scale(1.02);
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
  width: 80%;
  height: 80%;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.35));
  transition: transform 0.22s ease;
}

.gift-card:hover .gift-card__lottie {
  transform: scale(1.04);
}

.gift-card__image img {
  width: 80%;
  height: 80%;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.35));
  transition: transform 0.22s ease;
}

.gift-card:hover .gift-card__image img {
  transform: scale(1.04);
}

.gift-card__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

/* ---- Info section ---- */
.gift-card__info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px;
}

.gift-card__name {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gift-card__serial {
  font-size: 11px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.3;
  margin-bottom: 6px;
}

/* ---- Price pill ---- */
.gift-card__price {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background: var(--mb-primary, #34CDEF);
  color: #fff;
  font-family: var(--mb-font, 'SF Pro Text', sans-serif);
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: background 0.16s ease;
  -webkit-tap-highlight-color: transparent;
}

.gift-card__price:active {
  background: #2ab8d6;
}

.gift-card__ton-icon {
  flex-shrink: 0;
}

/* ---- Selection checkbox ---- */
.gift-card__checkbox {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.45);
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background var(--mb-duration-fast, 0.16s) ease,
    border-color var(--mb-duration-fast, 0.16s) ease;
}

.gift-card__checkbox--selected {
  background: var(--mb-primary, #34CDEF);
  border-color: var(--mb-primary, #34CDEF);
}

.gift-card__checkbox svg {
  color: #fff;
}
</style>
