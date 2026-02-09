<template>
  <div ref="container" class="lottie-gift" :style="{ width: size + 'px', height: size + 'px' }">
    <!-- Lottie renders into this div; fallback to img if lottie fails -->
    <img
      v-if="showFallback && fallbackSrc"
      :src="fallbackSrc"
      :alt="alt"
      class="lottie-gift__fallback"
      loading="lazy"
      draggable="false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import type { AnimationItem } from 'lottie-web'

// Lazy-load lottie-web to keep initial bundle small
let lottieModule: typeof import('lottie-web') | null = null
const getLottie = async () => {
  if (!lottieModule) {
    lottieModule = await import('lottie-web')
  }
  return lottieModule.default
}

const props = withDefaults(defineProps<{
  /** Full URL to .lottie.json file (e.g. nft.fragment.com/gift/hexpot-10348.lottie.json) */
  src: string
  /** Fallback image URL (.webp / .jpg) if lottie fails to load */
  fallbackSrc?: string
  alt?: string
  size?: number
  /** Auto-play on mount */
  autoplay?: boolean
  /** Loop animation */
  loop?: boolean
}>(), {
  alt: 'Gift',
  size: 100,
  autoplay: true,
  loop: true,
})

const container = ref<HTMLDivElement | null>(null)
const showFallback = ref(false)
let animation: AnimationItem | null = null

async function loadAnimation() {
  if (!container.value || !props.src) {
    showFallback.value = true
    return
  }

  // Destroy previous animation if exists
  if (animation) {
    animation.destroy()
    animation = null
  }

  showFallback.value = false

  try {
    const lottie = await getLottie()
    // Check container still exists after async load
    if (!container.value) return

    animation = lottie.loadAnimation({
      container: container.value,
      renderer: 'svg',
      loop: props.loop,
      autoplay: props.autoplay,
      path: props.src,
    })

    animation.addEventListener('data_failed', () => {
      showFallback.value = true
      animation?.destroy()
      animation = null
    })

    animation.addEventListener('error', () => {
      showFallback.value = true
      animation?.destroy()
      animation = null
    })
  } catch {
    showFallback.value = true
  }
}

watch(() => props.src, () => {
  loadAnimation()
})

onMounted(() => {
  loadAnimation()
})

onUnmounted(() => {
  if (animation) {
    animation.destroy()
    animation = null
  }
})
</script>

<style scoped>
.lottie-gift {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.lottie-gift :deep(svg) {
  width: 100% !important;
  height: 100% !important;
}

.lottie-gift__fallback {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.35));
}
</style>
