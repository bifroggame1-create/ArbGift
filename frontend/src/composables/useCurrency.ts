/**
 * Global currency state composable
 * Manages TON / Stars / Gift currency selection for all games
 */
import { ref, computed } from 'vue'

export type Currency = 'ton' | 'stars'

const selectedCurrency = ref<Currency>('ton')
const balanceTon = ref(3.66)
const balanceStars = ref(1250)

export function useCurrency() {
  const toggleCurrency = () => {
    selectedCurrency.value = selectedCurrency.value === 'ton' ? 'stars' : 'ton'
  }

  const setCurrency = (currency: Currency) => {
    selectedCurrency.value = currency
  }

  const currentBalance = computed(() => {
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

  return {
    selectedCurrency,
    balanceTon,
    balanceStars,
    currentBalance,
    currencyLabel,
    toggleCurrency,
    setCurrency,
    formatAmount,
  }
}
