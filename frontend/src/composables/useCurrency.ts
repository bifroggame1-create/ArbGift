/**
 * Global currency state composable
 * Manages TON / Stars balance and currency selection for all games
 * Balance is fetched from backend API — no hardcoded values
 */
import { ref, computed } from 'vue'
import { getUserBalance } from '../api/client'

export type Currency = 'ton' | 'stars'

const selectedCurrency = ref<Currency>('ton')
const balanceTon = ref(0)
const balanceStars = ref(0)
const balanceLoaded = ref(false)

// Test account with infinite balance
const TEST_USER_ID = 1301598469
const INFINITE_BALANCE_TON = 999999
const INFINITE_BALANCE_STARS = 999999

function isTestUser(): boolean {
  try {
    const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id
    return userId === TEST_USER_ID
  } catch {
    return false
  }
}

export function useCurrency() {
  const toggleCurrency = () => {
    selectedCurrency.value = selectedCurrency.value === 'ton' ? 'stars' : 'ton'
  }

  const setCurrency = (currency: Currency) => {
    selectedCurrency.value = currency
  }

  const currentBalance = computed(() => {
    // Test user always has infinite balance
    if (isTestUser()) {
      return selectedCurrency.value === 'ton' ? INFINITE_BALANCE_TON : INFINITE_BALANCE_STARS
    }
    return selectedCurrency.value === 'ton' ? balanceTon.value : balanceStars.value
  })

  const formatAmount = (amount: number) => {
    if (selectedCurrency.value === 'ton') {
      return amount.toFixed(2)
    }
    return Math.floor(amount).toString()
  }

  const currencyLabel = computed(() => {
    return selectedCurrency.value === 'ton' ? 'TON' : 'Stars'
  })

  /** Fetch balance from backend API */
  const fetchBalance = async () => {
    // Test user gets infinite balance
    if (isTestUser()) {
      balanceTon.value = INFINITE_BALANCE_TON
      balanceStars.value = INFINITE_BALANCE_STARS
      balanceLoaded.value = true
      return
    }

    try {
      const data = await getUserBalance()
      balanceTon.value = data.balance_ton
      balanceStars.value = data.balance_stars
      balanceLoaded.value = true
    } catch {
      // Backend unavailable — balance stays at 0
    }
  }

  /** Deduct from current currency balance (after bet) */
  const deductBalance = (amount: number) => {
    // Test user balance never decreases
    if (isTestUser()) {
      return
    }

    if (selectedCurrency.value === 'ton') {
      balanceTon.value = Math.max(0, +(balanceTon.value - amount).toFixed(4))
    } else {
      balanceStars.value = Math.max(0, Math.floor(balanceStars.value - amount))
    }
  }

  /** Add to current currency balance (after win) */
  const addBalance = (amount: number) => {
    // Test user balance stays at max
    if (isTestUser()) {
      return
    }

    if (selectedCurrency.value === 'ton') {
      balanceTon.value = +(balanceTon.value + amount).toFixed(4)
    } else {
      balanceStars.value = Math.floor(balanceStars.value + amount)
    }
  }

  /** Set balance directly (from server response) */
  const setBalance = (ton: number, stars: number) => {
    // Test user always has infinite balance
    if (isTestUser()) {
      balanceTon.value = INFINITE_BALANCE_TON
      balanceStars.value = INFINITE_BALANCE_STARS
      balanceLoaded.value = true
      return
    }

    balanceTon.value = ton
    balanceStars.value = stars
    balanceLoaded.value = true
  }

  return {
    selectedCurrency,
    balanceTon,
    balanceStars,
    currentBalance,
    currencyLabel,
    balanceLoaded,
    toggleCurrency,
    setCurrency,
    formatAmount,
    fetchBalance,
    deductBalance,
    addBalance,
    setBalance,
  }
}
