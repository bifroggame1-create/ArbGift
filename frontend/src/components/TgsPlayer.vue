<template>
  <div ref="container" class="tgs-player" :style="{ width: size + 'px', height: size + 'px' }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import type { AnimationItem } from 'lottie-web'

let lottieModule: typeof import('lottie-web') | null = null
const getLottie = async () => {
  if (!lottieModule) {
    lottieModule = await import('lottie-web')
  }
  return lottieModule.default
}

const props = withDefaults(defineProps<{
  src: string
  size?: number
  autoplay?: boolean
  loop?: boolean
}>(), {
  size: 100,
  autoplay: true,
  loop: true,
})

const container = ref<HTMLDivElement | null>(null)
let animation: AnimationItem | null = null

async function decompressTgs(url: string): Promise<object> {
  const response = await fetch(url)
  const blob = await response.blob()
  const ds = new DecompressionStream('gzip')
  const decompressed = blob.stream().pipeThrough(ds)
  const text = await new Response(decompressed).text()
  return JSON.parse(text)
}

async function loadAnimation() {
  if (!container.value || !props.src) return

  if (animation) {
    animation.destroy()
    animation = null
  }

  try {
    const [lottie, animationData] = await Promise.all([
      getLottie(),
      decompressTgs(props.src),
    ])

    if (!container.value) return

    animation = lottie.loadAnimation({
      container: container.value,
      renderer: 'svg',
      loop: props.loop,
      autoplay: props.autoplay,
      animationData,
    })
  } catch (e) {
    console.warn('TgsPlayer: failed to load', props.src, e)
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
.tgs-player {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.tgs-player :deep(svg) {
  width: 100% !important;
  height: 100% !important;
}
</style>
