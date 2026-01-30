<template>
  <div class="probability-wheel-container">
    <svg
      class="probability-wheel"
      :class="{ spinning: isSpinning }"
      :style="wheelStyle"
      viewBox="0 0 200 200"
      width="280"
      height="280"
    >
      <!-- Success sector (green/purple gradient) -->
      <defs>
        <linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#34d399;stop-opacity:1" />
        </linearGradient>

        <linearGradient id="failGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#ef4444;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#dc2626;stop-opacity:1" />
        </linearGradient>

        <!-- Glow filter -->
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      <!-- Success sector -->
      <path
        :d="successSectorPath"
        fill="url(#successGradient)"
        stroke="#fff"
        stroke-width="2"
        filter="url(#glow)"
      />

      <!-- Fail sector -->
      <path
        :d="failSectorPath"
        fill="url(#failGradient)"
        stroke="#fff"
        stroke-width="2"
        filter="url(#glow)"
      />

      <!-- Center circle (decorative) -->
      <circle
        cx="100"
        cy="100"
        r="35"
        fill="#1f2937"
        stroke="#fff"
        stroke-width="2"
      />

      <!-- Center icon -->
      <text
        x="100"
        y="110"
        text-anchor="middle"
        font-size="24"
        fill="#fff"
      >
        ⚡
      </text>

      <!-- Tick marks -->
      <g v-for="i in 12" :key="i" :transform="`rotate(${i * 30} 100 100)`">
        <line
          x1="100"
          y1="15"
          x2="100"
          y2="25"
          stroke="#fff"
          stroke-width="2"
          opacity="0.5"
        />
      </g>
    </svg>

    <!-- Fixed Needle (pointer) at top -->
    <div class="needle-container">
      <div class="needle">
        <svg width="40" height="60" viewBox="0 0 40 60">
          <defs>
            <linearGradient id="needleGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style="stop-color:#fbbf24;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#f59e0b;stop-opacity:1" />
            </linearGradient>
          </defs>
          <polygon
            points="20,50 25,10 20,0 15,10"
            fill="url(#needleGradient)"
            stroke="#fff"
            stroke-width="1"
          />
          <circle cx="20" cy="50" r="6" fill="#fbbf24" stroke="#fff" stroke-width="2" />
        </svg>
      </div>
    </div>

    <!-- Outer decorative ring -->
    <div class="outer-ring"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  probability: number
  isSpinning: boolean
  resultAngle: number
}

const props = defineProps<Props>()

const wheelStyle = computed(() => {
  if (!props.isSpinning) return {}

  return {
    transform: `rotate(${props.resultAngle}deg)`,
  }
})

const successSectorPath = computed(() => {
  // Calculate SVG path for success sector
  const angle = props.probability * 360
  const endX = 100 + 70 * Math.cos((angle - 90) * Math.PI / 180)
  const endY = 100 + 70 * Math.sin((angle - 90) * Math.PI / 180)
  const largeArc = angle > 180 ? 1 : 0

  return `M 100,100 L 100,30 A 70,70 0 ${largeArc},1 ${endX},${endY} Z`
})

const failSectorPath = computed(() => {
  const angle = props.probability * 360
  const startX = 100 + 70 * Math.cos((angle - 90) * Math.PI / 180)
  const startY = 100 + 70 * Math.sin((angle - 90) * Math.PI / 180)
  const largeArc = (360 - angle) > 180 ? 1 : 0

  return `M 100,100 L ${startX},${startY} A 70,70 0 ${largeArc},1 100,30 Z`
})
</script>

<style scoped>
.probability-wheel-container {
  position: relative;
  width: 280px;
  height: 280px;
  margin: 0 auto;
}

.probability-wheel {
  transform-origin: center;
  transition: none;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.3));
}

.probability-wheel.spinning {
  transition: transform 3000ms cubic-bezier(0.25, 0.1, 0.25, 1);
}

.needle-container {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.4));
  animation: needle-pulse 2s ease-in-out infinite;
}

@keyframes needle-pulse {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(2px); }
}

.needle svg {
  display: block;
}

.outer-ring {
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border: 4px solid transparent;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(236, 72, 153, 0.3));
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  padding: 4px;
  animation: ring-rotate 10s linear infinite;
}

@keyframes ring-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
