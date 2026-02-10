<template>
  <div class="stars-view">
    <!-- Header -->
    <header class="stars-header">
      <button class="back-btn" @click="router.back()">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <div class="header-title">
        <img src="/icons/stars.png" alt="Stars" class="header-icon" width="24" height="24" />
        Покупка Stars
      </div>
      <div class="header-spacer"></div>
    </header>

    <div class="stars-content">
      <!-- Promo Banner -->
      <div class="promo-banner">
        <div class="promo-icon">
          <img src="/images/starBonus-banner.svg" alt="Stars" class="promo-icon-img" />
        </div>
        <div class="promo-text">
          <h2>Telegram Stars</h2>
          <p>Мгновенная доставка на ваш аккаунт</p>
        </div>
      </div>

      <!-- Username Input -->
      <div class="input-section">
        <label class="input-label">Telegram username</label>
        <div class="username-input-wrapper">
          <span class="at-symbol">@</span>
          <input
            type="text"
            v-model="usernameInput"
            placeholder="username"
            class="username-input"
          />
        </div>
        <p class="input-hint">Stars будут отправлены на этот аккаунт</p>
      </div>

      <!-- Amount Input -->
      <div class="amount-section">
        <label class="input-label">Количество Stars ({{ MIN_STARS }} - {{ MAX_STARS.toLocaleString() }})</label>
        <div class="amount-input-wrapper">
          <input
            type="text"
            inputmode="numeric"
            :value="starsAmount"
            @input="handleAmountInput"
            @blur="handleAmountBlur"
            class="amount-input"
          />
          <span class="amount-price">≈ {{ formatPrice(calculatePrice(starsAmount)) }} ₽</span>
        </div>

        <!-- Range Slider -->
        <div class="range-slider-wrapper">
          <input
            type="range"
            :value="starsAmount"
            @input="handleSliderInput"
            :min="MIN_STARS"
            :max="MAX_STARS"
            :step="10"
            class="range-slider"
            :style="sliderStyle"
          />
          <div class="range-labels">
            <span>{{ MIN_STARS }}</span>
            <span>{{ MAX_STARS.toLocaleString() }}</span>
          </div>
        </div>

        <!-- Quick Amounts -->
        <div class="quick-amounts">
          <button
            v-for="amount in quickAmounts"
            :key="amount"
            :class="['quick-btn', { active: starsAmount === amount }]"
            @click="setAmount(amount)"
          >
            {{ amount.toLocaleString() }}
          </button>
        </div>
      </div>

      <!-- How It Works -->
      <div class="how-it-works">
        <h3 class="section-title">Как это работает</h3>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <p class="step-title">Выберите количество Stars</p>
              <p class="step-desc">От {{ MIN_STARS }} до {{ MAX_STARS.toLocaleString() }} Stars</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <p class="step-title">Выберите метод оплаты</p>
              <p class="step-desc">Telegram Stars или другие способы</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <p class="step-title">Получите Stars</p>
              <p class="step-desc">Мгновенная доставка на ваш аккаунт</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Buy Button -->
      <button
        class="buy-btn"
        :disabled="isProcessing || !usernameInput.trim()"
        @click="handlePurchase"
      >
        <template v-if="isProcessing">
          <div class="spinner"></div>
          <span>Создание...</span>
        </template>
        <template v-else>
          <img src="/icons/stars.png" alt="Stars" width="20" height="20" class="btn-star-icon" />
          <span>Купить {{ starsAmount.toLocaleString() }} Stars</span>
          <span class="btn-price">• {{ formatPrice(calculatePrice(starsAmount)) }} ₽</span>
        </template>
      </button>

      <!-- Features -->
      <div class="features-grid">
        <div class="feature">
          <span class="feature-icon">⚡</span>
          <span class="feature-text">Мгновенно</span>
        </div>
        <div class="feature">
          <span class="feature-icon">🔒</span>
          <span class="feature-text">Безопасно</span>
        </div>
        <div class="feature">
          <span class="feature-icon">✓</span>
          <span class="feature-text">Гарантия</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '../composables/useTelegram'

const router = useRouter()
const { user, hapticImpact } = useTelegram()

// Constants
const MIN_STARS = 50
const MAX_STARS = 20000
const RATE_PER_STAR = 1.8 // 1 Star ≈ 1.8 RUB

// State
const usernameInput = ref(user.value?.username?.replace('@', '') || '')
const starsAmount = ref(100)
const isProcessing = ref(false)

const quickAmounts = [100, 500, 1000, 5000]

// Computed
const sliderStyle = computed(() => {
  const percentage = ((starsAmount.value - MIN_STARS) / (MAX_STARS - MIN_STARS)) * 100
  return {
    background: `linear-gradient(to right, #a855f7 0%, #a855f7 ${percentage}%, #3a3a3c ${percentage}%, #3a3a3c 100%)`
  }
})

// Methods
const calculatePrice = (amount: number): number => {
  return Math.ceil(amount * RATE_PER_STAR)
}

const formatPrice = (price: number): string => {
  return price.toLocaleString('ru-RU')
}

const setAmount = (amount: number) => {
  starsAmount.value = amount
  hapticImpact('light')
}

const handleAmountInput = (e: Event) => {
  const value = (e.target as HTMLInputElement).value.replace(/[^0-9]/g, '')
  if (value) {
    const num = parseInt(value)
    starsAmount.value = Math.max(MIN_STARS, Math.min(MAX_STARS, num))
  }
}

const handleAmountBlur = (e: Event) => {
  const value = parseInt((e.target as HTMLInputElement).value) || MIN_STARS
  starsAmount.value = Math.max(MIN_STARS, Math.min(MAX_STARS, value))
}

const handleSliderInput = (e: Event) => {
  starsAmount.value = parseInt((e.target as HTMLInputElement).value)
  hapticImpact('light')
}

const handlePurchase = async () => {
  if (!usernameInput.value.trim()) {
    alert('Введите Telegram username')
    return
  }

  isProcessing.value = true
  hapticImpact('medium')

  try {
    const username = usernameInput.value.startsWith('@')
      ? usernameInput.value
      : `@${usernameInput.value}`

    // Create Stars invoice via backend API
    const response = await fetch('/api/v1/stars/invoice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: user.value?.id,
        username: username,
        amount: starsAmount.value,
        price: calculatePrice(starsAmount.value)
      })
    })

    if (!response.ok) throw new Error('Failed to create invoice')

    const data = await response.json()

    // Open Telegram Stars payment via WebApp
    if (window.Telegram?.WebApp?.openInvoice) {
      window.Telegram.WebApp.openInvoice(data.invoice_url, (status: string) => {
        if (status === 'paid') {
          hapticImpact('heavy')
          alert('Оплата прошла успешно! Stars будут доставлены в ближайшее время.')
          router.push('/profile')
        }
      })
    } else {
      // Fallback for web
      window.open(data.invoice_url, '_blank')
    }
  } catch (e) {
    console.error('Stars purchase failed:', e)
    alert('Произошла ошибка при создании заказа')
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.stars-view {
  min-height: 100vh;
  background: #000;
  color: #fff;
  padding-bottom: 100px;
}

/* Header */
.stars-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  position: sticky;
  top: 0;
  background: #000;
  z-index: 100;
  border-bottom: 1px solid #1c1c1e;
}

.back-btn {
  width: 40px;
  height: 40px;
  background: #1c1c1e;
  border: none;
  border-radius: 12px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
}

.header-icon {
  object-fit: contain;
}

.header-spacer {
  width: 40px;
}

/* Content */
.stars-content {
  padding: 16px;
}

/* Promo Banner */
.promo-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.promo-icon-img {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.promo-text h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
}

.promo-text p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* Input Section */
.input-section {
  margin-bottom: 24px;
}

.input-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
  padding-left: 4px;
}

.username-input-wrapper {
  display: flex;
  align-items: center;
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  border-radius: 14px;
  overflow: hidden;
}

.at-symbol {
  padding: 14px 0 14px 14px;
  color: #6b7280;
  font-size: 15px;
}

.username-input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 14px 14px 14px 4px;
  color: #fff;
  font-size: 15px;
  outline: none;
}

.username-input::placeholder {
  color: #6b7280;
}

.input-hint {
  font-size: 12px;
  color: #6b7280;
  margin: 8px 0 0;
  padding-left: 4px;
}

/* Amount Section */
.amount-section {
  margin-bottom: 24px;
}

.amount-input-wrapper {
  display: flex;
  align-items: center;
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 16px;
}

.amount-input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 14px;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  outline: none;
}

.amount-price {
  padding-right: 14px;
  font-size: 13px;
  color: #6b7280;
}

/* Range Slider */
.range-slider-wrapper {
  margin-bottom: 16px;
}

.range-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  appearance: none;
  cursor: pointer;
}

.range-slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #a855f7;
  box-shadow: 0 2px 8px rgba(168, 85, 247, 0.5);
}

.range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 11px;
  color: #6b7280;
}

/* Quick Amounts */
.quick-amounts {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.quick-btn {
  padding: 10px;
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.quick-btn.active {
  background: #a855f7;
  border-color: #a855f7;
}

/* How It Works */
.how-it-works {
  background: #1c1c1e;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 16px;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step {
  display: flex;
  gap: 12px;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 2px;
}

.step-desc {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

/* Features */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.feature {
  background: #1c1c1e;
  border-radius: 12px;
  padding: 14px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.feature-icon {
  font-size: 24px;
}

.feature-text {
  font-size: 12px;
  color: #6b7280;
}

/* Buy Button (inline) */
.buy-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  border: none;
  border-radius: 14px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  transition: opacity 0.2s;
  margin-bottom: 24px;
}

.buy-btn:disabled {
  opacity: 0.5;
}

.btn-star-icon {
  object-fit: contain;
}

.btn-price {
  font-size: 14px;
  font-weight: 500;
  opacity: 0.8;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
