/**
 * Telegram WebApp integration composable
 */
import { ref } from 'vue'

export function useTelegram() {
  const webApp = ref<any>(null)
  const user = ref<any>(null)
  const isReady = ref(false)

  const initWebApp = () => {
    if (window.Telegram?.WebApp) {
      webApp.value = window.Telegram.WebApp
      user.value = webApp.value.initDataUnsafe?.user

      // Apply Telegram theme
      document.documentElement.style.setProperty(
        '--tg-theme-bg-color',
        webApp.value.backgroundColor || '#030712'
      )
      document.documentElement.style.setProperty(
        '--tg-theme-text-color',
        webApp.value.textColor || '#ffffff'
      )

      isReady.value = true
    }
  }

  const ready = () => {
    webApp.value?.ready()
  }

  const expand = () => {
    webApp.value?.expand()
  }

  const close = () => {
    webApp.value?.close()
  }

  const setHeaderColor = (color: string) => {
    webApp.value?.setHeaderColor(color)
  }

  const setBackgroundColor = (color: string) => {
    webApp.value?.setBackgroundColor(color)
  }

  const showBackButton = () => {
    webApp.value?.BackButton.show()
  }

  const hideBackButton = () => {
    webApp.value?.BackButton.hide()
  }

  const onBackButtonClick = (callback: () => void) => {
    webApp.value?.BackButton.onClick(callback)
  }

  const hapticImpact = (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
    webApp.value?.HapticFeedback.impactOccurred(style)
  }

  const hapticNotification = (type: 'error' | 'success' | 'warning' = 'success') => {
    webApp.value?.HapticFeedback.notificationOccurred(type)
  }

  const hapticSelection = () => {
    webApp.value?.HapticFeedback.selectionChanged()
  }

  const showAlert = (message: string) => {
    webApp.value?.showAlert(message)
  }

  const showConfirm = (message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      webApp.value?.showConfirm(message, (confirmed: boolean) => {
        resolve(confirmed)
      })
    })
  }

  const openLink = (url: string, options?: { try_instant_view?: boolean }) => {
    webApp.value?.openLink(url, options)
  }

  const openTelegramLink = (url: string) => {
    webApp.value?.openTelegramLink(url)
  }

  return {
    webApp,
    user,
    isReady,
    initWebApp,
    ready,
    expand,
    close,
    setHeaderColor,
    setBackgroundColor,
    showBackButton,
    hideBackButton,
    onBackButtonClick,
    hapticImpact,
    hapticNotification,
    hapticSelection,
    showAlert,
    showConfirm,
    openLink,
    openTelegramLink,
  }
}
