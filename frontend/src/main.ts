import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// Telegram WebApp initialization
declare global {
  interface Window {
    Telegram: {
      WebApp: TelegramWebApp
    }
  }

  interface TelegramWebApp {
    initData: string
    initDataUnsafe: {
      query_id?: string
      user?: {
        id: number
        first_name: string
        last_name?: string
        username?: string
        language_code?: string
        is_premium?: boolean
        photo_url?: string
      }
      auth_date: number
      hash: string
      start_param?: string
    }
    version: string
    platform: string
    colorScheme: 'light' | 'dark'
    themeParams: {
      bg_color?: string
      text_color?: string
      hint_color?: string
      link_color?: string
      button_color?: string
      button_text_color?: string
      secondary_bg_color?: string
      header_bg_color?: string
      accent_text_color?: string
      section_bg_color?: string
      section_header_text_color?: string
      subtitle_text_color?: string
      destructive_text_color?: string
    }
    isExpanded: boolean
    viewportHeight: number
    viewportStableHeight: number
    headerColor: string
    backgroundColor: string
    isClosingConfirmationEnabled: boolean
    BackButton: {
      isVisible: boolean
      show(): void
      hide(): void
      onClick(callback: () => void): void
      offClick(callback: () => void): void
    }
    MainButton: {
      text: string
      color: string
      textColor: string
      isVisible: boolean
      isActive: boolean
      isProgressVisible: boolean
      setText(text: string): void
      onClick(callback: () => void): void
      offClick(callback: () => void): void
      show(): void
      hide(): void
      enable(): void
      disable(): void
      showProgress(leaveActive?: boolean): void
      hideProgress(): void
    }
    HapticFeedback: {
      impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void
      notificationOccurred(type: 'error' | 'success' | 'warning'): void
      selectionChanged(): void
    }
    ready(): void
    expand(): void
    close(): void
    enableClosingConfirmation(): void
    disableClosingConfirmation(): void
    setHeaderColor(color: string): void
    setBackgroundColor(color: string): void
    openLink(url: string, options?: { try_instant_view?: boolean }): void
    openTelegramLink(url: string): void
    showPopup(params: {
      title?: string
      message: string
      buttons?: Array<{
        id?: string
        type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive'
        text?: string
      }>
    }, callback?: (buttonId: string) => void): void
    showAlert(message: string, callback?: () => void): void
    showConfirm(message: string, callback?: (confirmed: boolean) => void): void
    sendData(data: string): void
    requestWriteAccess(callback?: (granted: boolean) => void): void
    requestContact(callback?: (granted: boolean) => void): void
  }
}

// Initialize Telegram WebApp
const initTelegramWebApp = () => {
  const tg = window.Telegram?.WebApp

  if (tg) {
    // Tell Telegram that the app is ready
    tg.ready()

    // Expand the app to full height
    tg.expand()

    // Set header color to match theme
    if (tg.themeParams.header_bg_color) {
      tg.setHeaderColor(tg.themeParams.header_bg_color)
    }

    // Set background color
    if (tg.themeParams.bg_color) {
      tg.setBackgroundColor(tg.themeParams.bg_color)
    }

    // Enable closing confirmation for better UX
    tg.enableClosingConfirmation()

    console.log('Telegram WebApp initialized:', {
      version: tg.version,
      platform: tg.platform,
      colorScheme: tg.colorScheme,
      user: tg.initDataUnsafe.user
    })
  } else {
    console.warn('Telegram WebApp not available, running in standalone mode')
  }
}

// Create and mount app
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize Telegram before mounting
initTelegramWebApp()

// Mount app
app.mount('#app')
