<template>
  <!--
    PIXEL-PERFECT копия карточки из portals.tg
    CSS переменные: --background: #141414, --primary: #1689ff, --radius: 16px
  -->
  <div
    class="gift-card"
    :style="cardStyle"
    @click="handleClick"
  >
    <!-- Изображение гифта -->
    <div class="gift-card__image">
      <img
        v-if="gift.image_url"
        :src="gift.image_url"
        :alt="gift.name"
        loading="lazy"
      />
      <div v-else class="gift-card__placeholder">🎁</div>
    </div>

    <!-- Информация -->
    <div class="gift-card__info">
      <div class="gift-card__name">{{ gift.name }}</div>
      <div class="gift-card__serial">#{{ serialNumber }}</div>
    </div>

    <!-- Цена -->
    <button class="gift-card__price" @click.stop="handleBuy">
      <span>{{ formattedPrice }}</span>
      <svg class="gift-card__ton-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
      </svg>
    </button>

    <!-- Чекбокс для bulk buy (как в portals) -->
    <div v-if="selectable" class="gift-card__checkbox" :class="{ selected: isSelected }">
      <svg v-if="isSelected" viewBox="0 0 24 24" fill="currentColor">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Gift } from '../api/client'
import { useTelegram } from '../composables/useTelegram'

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

// Серийный номер из ID или адреса
const serialNumber = computed(() => {
  if (props.gift.tg_id) return props.gift.tg_id
  return props.gift.id
})

// Форматированная цена
const formattedPrice = computed(() => {
  const price = props.gift.min_price_ton || props.gift.price || 0
  return Number(price).toFixed(2).replace(/\.?0+$/, '')
})

// Цвет карточки на основе коллекции/редкости (как в portals)
const cardStyle = computed(() => {
  // Portals использует цвета фона на основе коллекции
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
  return { background: bg }
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
/*
  Portals.tg CSS Variables:
  --background: #141414
  --primary: #1689ff
  --secondary: #282727
  --radius: 16px
  --color-text: #fff
  --color-text-muted: #6d6d71
*/

.gift-card {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background: linear-gradient(180deg, #3A3A3A 0%, #282727 100%);
}

.gift-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.gift-card__image {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.gift-card__image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.gift-card__placeholder {
  font-size: 64px;
}

.gift-card__info {
  padding: 0 12px 8px;
  text-align: left;
}

.gift-card__name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  line-height: 1.2;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gift-card__serial {
  font-size: 12px;
  color: #6d6d71;
  font-weight: 400;
}

.gift-card__price {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin: 0 12px 12px;
  padding: 8px 16px;
  border-radius: 12px;
  border: none;
  background: #1689ff;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.gift-card__price:hover {
  background: #0070e0;
}

.gift-card__ton-icon {
  width: 14px;
  height: 14px;
}

.gift-card__checkbox {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.5);
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.gift-card__checkbox.selected {
  background: #1689ff;
  border-color: #1689ff;
}

.gift-card__checkbox svg {
  width: 16px;
  height: 16px;
  color: #fff;
}
</style>
