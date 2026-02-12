<template>
  <div ref="containerRef" class="plinko-board-container">
    <div ref="pixiRef" class="pixi-canvas"></div>
    <!-- Multiplier slots rendered below canvas -->
    <div class="multiplier-row">
      <div
        v-for="(mult, i) in multipliers"
        :key="i"
        :class="['mult-slot', getMultClass(mult)]"
        :style="{ width: slotWidth + 'px' }"
      >
        {{ formatMult(mult) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ref, onMounted, onUnmounted, watch, nextTick,
  type PropType,
} from 'vue'
import * as PIXI from 'pixi.js'
import Matter from 'matter-js'

const props = defineProps({
  rowCount: { type: Number as PropType<8 | 12 | 16>, default: 12 },
  riskLevel: { type: String as PropType<'low' | 'medium' | 'high'>, default: 'medium' },
  multipliers: { type: Array as PropType<number[]>, default: () => [] },
})

const emit = defineEmits<{
  landed: [slotIndex: number, dropIndex: number]
  allLanded: []
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const pixiRef = ref<HTMLDivElement | null>(null)

// Layout
const BOARD_PADDING = 20
const BALL_RADIUS = 6
let boardWidth = 360
let boardHeight = 420
const slotWidth = ref(30)

// PixiJS
let app: PIXI.Application | null = null
let pegGraphics: PIXI.Graphics[] = []
let activeBalls: {
  body: Matter.Body
  graphic: PIXI.Graphics
  trail: PIXI.Graphics[]
  pathIndex: number
  path: number[][]
  dropIndex: number
  landed: boolean
}[] = []

// Matter.js
let mEngine: Matter.Engine | null = null
let mRunner: Matter.Runner | null = null
let pegBodies: Matter.Body[] = []
let wallBodies: Matter.Body[] = []

// Peg layout cache
let pegPositions: { x: number; y: number }[] = []
let pegGlowTimers: Map<number, number> = new Map()

// ===== LAYOUT COMPUTATION =====

function computeLayout() {
  if (!containerRef.value) return
  boardWidth = containerRef.value.clientWidth
  boardHeight = Math.min(boardWidth * 1.15, 480)

  const rows = props.rowCount
  const numSlots = rows + 1
  slotWidth.value = Math.floor((boardWidth - BOARD_PADDING * 2) / numSlots)
}

function computePegPositions() {
  pegPositions = []
  const rows = props.rowCount
  const startY = 40
  const endY = boardHeight - 20
  const spacingY = (endY - startY) / rows

  for (let row = 0; row < rows; row++) {
    const pegsInRow = row + 3 // 3 pegs in first row, increasing
    const totalWidth = boardWidth - BOARD_PADDING * 2
    const spacingX = totalWidth / (pegsInRow + 1)

    for (let col = 0; col < pegsInRow; col++) {
      const x = BOARD_PADDING + spacingX * (col + 1)
      const y = startY + spacingY * row
      pegPositions.push({ x, y })
    }
  }
}

// ===== PIXI SETUP =====

async function initPixi() {
  if (!pixiRef.value) return

  app = new PIXI.Application()
  await app.init({
    width: boardWidth,
    height: boardHeight,
    backgroundAlpha: 0,
    antialias: true,
    resolution: Math.min(window.devicePixelRatio, 2),
    autoDensity: true,
  })

  pixiRef.value.appendChild(app.canvas as HTMLCanvasElement)

  drawPegs()
  app.ticker.add(renderLoop)
}

function drawPegs() {
  if (!app) return

  // Clear old pegs
  for (const g of pegGraphics) {
    g.destroy()
  }
  pegGraphics = []

  const pegRadius = props.rowCount <= 8 ? 5 : props.rowCount <= 12 ? 4 : 3.5

  for (let i = 0; i < pegPositions.length; i++) {
    const { x, y } = pegPositions[i]
    const g = new PIXI.Graphics()
    g.circle(0, 0, pegRadius)
    g.fill({ color: 0x3E1E54 })
    g.position.set(x, y)
    app!.stage.addChild(g)
    pegGraphics.push(g)
  }
}

// ===== MATTER.JS SETUP =====

function initMatter() {
  mEngine = Matter.Engine.create({
    gravity: { x: 0, y: 0.8, scale: 0.001 },
  })

  // Create peg bodies (static)
  pegBodies = []
  const pegRadius = props.rowCount <= 8 ? 5 : props.rowCount <= 12 ? 4 : 3.5

  for (const { x, y } of pegPositions) {
    const peg = Matter.Bodies.circle(x, y, pegRadius + 1, {
      isStatic: true,
      restitution: 0.5,
      friction: 0.1,
      label: 'peg',
    })
    pegBodies.push(peg)
  }

  // Walls
  const wallThickness = 10
  const leftWall = Matter.Bodies.rectangle(
    -wallThickness / 2, boardHeight / 2,
    wallThickness, boardHeight * 2,
    { isStatic: true, restitution: 0.3 }
  )
  const rightWall = Matter.Bodies.rectangle(
    boardWidth + wallThickness / 2, boardHeight / 2,
    wallThickness, boardHeight * 2,
    { isStatic: true, restitution: 0.3 }
  )
  wallBodies = [leftWall, rightWall]

  Matter.Composite.add(mEngine.world, [...pegBodies, ...wallBodies])

  // Collision events for peg glow
  Matter.Events.on(mEngine, 'collisionStart', (event) => {
    for (const pair of event.pairs) {
      const pegIndex = pegBodies.indexOf(pair.bodyA)
      const pegIndex2 = pegBodies.indexOf(pair.bodyB)
      const idx = pegIndex >= 0 ? pegIndex : pegIndex2
      if (idx >= 0) {
        pegGlowTimers.set(idx, 12) // 12 frames of glow
      }
    }
  })

  // Create runner (manual stepping)
  mRunner = Matter.Runner.create({ delta: 1000 / 60 })
}

// ===== BALL DROP =====

function dropBall(path: number[][], dropIndex: number) {
  if (!app || !mEngine) return

  // Start position: top center
  const startX = boardWidth / 2
  const startY = 10

  const body = Matter.Bodies.circle(startX, startY, BALL_RADIUS, {
    restitution: 0.4,
    friction: 0.05,
    density: 0.002,
    label: 'ball',
  })
  Matter.Composite.add(mEngine.world, body)

  const graphic = new PIXI.Graphics()
  graphic.circle(0, 0, BALL_RADIUS)
  graphic.fill({ color: 0xFDFDFD })
  graphic.position.set(startX, startY)
  app.stage.addChild(graphic)

  activeBalls.push({
    body,
    graphic,
    trail: [],
    pathIndex: 0,
    path,
    dropIndex,
    landed: false,
  })
}

// ===== RENDER LOOP =====

function renderLoop() {
  if (!mEngine) return

  // Step physics
  Matter.Engine.update(mEngine, 1000 / 60)

  // Update peg glow
  for (const [idx, frames] of pegGlowTimers.entries()) {
    if (frames > 0) {
      const g = pegGraphics[idx]
      if (g) {
        const intensity = frames / 12
        const color = lerpColor(0x3E1E54, 0x6B2FBE, intensity)
        g.clear()
        const pegRadius = props.rowCount <= 8 ? 5 : props.rowCount <= 12 ? 4 : 3.5
        // Glow circle (larger, semi-transparent)
        g.circle(0, 0, pegRadius + 3 * intensity)
        g.fill({ color: 0x6B2FBE, alpha: 0.3 * intensity })
        // Core circle
        g.circle(0, 0, pegRadius)
        g.fill({ color })
      }
      pegGlowTimers.set(idx, frames - 1)
    } else {
      pegGlowTimers.delete(idx)
      const g = pegGraphics[idx]
      if (g) {
        const pegRadius = props.rowCount <= 8 ? 5 : props.rowCount <= 12 ? 4 : 3.5
        g.clear()
        g.circle(0, 0, pegRadius)
        g.fill({ color: 0x3E1E54 })
      }
    }
  }

  // Update balls
  let allLanded = true
  for (const ball of activeBalls) {
    if (ball.landed) continue
    allLanded = false

    // Sync graphic to physics body
    ball.graphic.position.set(ball.body.position.x, ball.body.position.y)

    // Steering toward server-determined path
    if (ball.path.length > 0 && ball.pathIndex < ball.path.length) {
      const progress = ball.body.position.y / boardHeight
      const targetIndex = Math.min(
        Math.floor(progress * ball.path.length),
        ball.path.length - 1
      )

      if (targetIndex > ball.pathIndex) {
        ball.pathIndex = targetIndex
      }

      const targetX = ball.path[ball.pathIndex][0] * boardWidth
      const dx = targetX - ball.body.position.x
      const steerForce = dx * 0.00015
      Matter.Body.applyForce(ball.body, ball.body.position, { x: steerForce, y: 0 })
    }

    // Trail particle
    if (app && Math.random() > 0.5) {
      const trail = new PIXI.Graphics()
      trail.circle(0, 0, 2 + Math.random() * 2)
      trail.fill({ color: 0x6B2FBE, alpha: 0.5 })
      trail.position.set(
        ball.body.position.x + (Math.random() - 0.5) * 4,
        ball.body.position.y + (Math.random() - 0.5) * 4,
      )
      app.stage.addChild(trail)
      ball.trail.push(trail)
    }

    // Fade trail
    for (let i = ball.trail.length - 1; i >= 0; i--) {
      const t = ball.trail[i]
      t.alpha -= 0.05
      if (t.alpha <= 0) {
        t.destroy()
        ball.trail.splice(i, 1)
      }
    }

    // Check if landed (past bottom)
    if (ball.body.position.y >= boardHeight - 10) {
      ball.landed = true
      // Determine landing slot
      const numSlots = props.rowCount + 1
      const slotWidth = (boardWidth - BOARD_PADDING * 2) / numSlots
      const relX = ball.body.position.x - BOARD_PADDING
      let slotIndex = Math.floor(relX / slotWidth)
      slotIndex = Math.max(0, Math.min(numSlots - 1, slotIndex))

      // Use server-determined slot from path
      const serverSlot = ball.path.length > 0
        ? Math.floor(ball.path[ball.path.length - 1][0] * numSlots)
        : slotIndex
      const finalSlot = Math.max(0, Math.min(numSlots - 1, serverSlot))

      emit('landed', finalSlot, ball.dropIndex)

      // Landing burst particles
      spawnBurst(ball.body.position.x, ball.body.position.y)

      // Remove physics body
      Matter.Composite.remove(mEngine!.world, ball.body)

      // Fade out ball graphic
      const fadeOut = () => {
        ball.graphic.alpha -= 0.1
        if (ball.graphic.alpha <= 0) {
          ball.graphic.destroy()
          for (const t of ball.trail) t.destroy()
          ball.trail = []
        } else {
          requestAnimationFrame(fadeOut)
        }
      }
      fadeOut()
    }
  }

  // Clean up fully landed balls
  activeBalls = activeBalls.filter(b => !b.landed || b.graphic.alpha > 0)

  // Emit allLanded when all balls done
  if (allLanded && activeBalls.length === 0 && activeBalls.length === 0) {
    // Small debounce to avoid multiple emits
    emit('allLanded')
  }
}

function spawnBurst(x: number, y: number) {
  if (!app) return
  for (let i = 0; i < 8; i++) {
    const particle = new PIXI.Graphics()
    const size = 2 + Math.random() * 3
    particle.circle(0, 0, size)
    particle.fill({ color: 0x6B2FBE, alpha: 0.8 })
    particle.position.set(x, y)

    const vx = (Math.random() - 0.5) * 6
    const vy = -Math.random() * 4 - 2

    app.stage.addChild(particle)

    let life = 20
    const animate = () => {
      particle.position.x += vx
      particle.position.y += vy + (20 - life) * 0.1
      particle.alpha -= 0.05
      life--
      if (life <= 0 || particle.alpha <= 0) {
        particle.destroy()
      } else {
        requestAnimationFrame(animate)
      }
    }
    animate()
  }
}

// ===== UTILITIES =====

function lerpColor(a: number, b: number, t: number): number {
  const ar = (a >> 16) & 0xFF
  const ag = (a >> 8) & 0xFF
  const ab = a & 0xFF
  const br = (b >> 16) & 0xFF
  const bg = (b >> 8) & 0xFF
  const bb = b & 0xFF
  const r = Math.round(ar + (br - ar) * t)
  const g = Math.round(ag + (bg - ag) * t)
  const blue = Math.round(ab + (bb - ab) * t)
  return (r << 16) | (g << 8) | blue
}

function getMultClass(mult: number): string {
  if (mult >= 100) return 'extreme'
  if (mult >= 10) return 'high'
  if (mult >= 2) return 'medium'
  if (mult >= 1) return 'low'
  return 'center'
}

function formatMult(mult: number): string {
  if (mult >= 1000) return mult.toFixed(0) + 'x'
  if (mult >= 100) return mult.toFixed(0) + 'x'
  if (mult >= 10) return mult.toFixed(1) + 'x'
  return mult.toFixed(1) + 'x'
}

// ===== LIFECYCLE =====

async function rebuild() {
  // Cleanup
  cleanup()
  await nextTick()

  computeLayout()
  computePegPositions()
  initMatter()
  await initPixi()
}

function cleanup() {
  // Clean up balls
  for (const ball of activeBalls) {
    ball.graphic.destroy()
    for (const t of ball.trail) t.destroy()
  }
  activeBalls = []

  // Destroy PixiJS
  if (app) {
    app.destroy(true, { children: true })
    app = null
  }
  pegGraphics = []

  // Destroy Matter.js
  if (mEngine) {
    Matter.Engine.clear(mEngine)
    mEngine = null
  }
  if (mRunner) {
    Matter.Runner.stop(mRunner)
    mRunner = null
  }

  pegBodies = []
  wallBodies = []
  pegGlowTimers.clear()
}

onMounted(async () => {
  computeLayout()
  computePegPositions()
  initMatter()
  await initPixi()

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  cleanup()
})

let resizeTimer: ReturnType<typeof setTimeout> | null = null
function handleResize() {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => rebuild(), 200)
}

watch(() => props.rowCount, () => rebuild())

// Expose dropBall for parent
defineExpose({ dropBall })
</script>

<style scoped>
.plinko-board-container {
  width: 100%;
  position: relative;
}

.pixi-canvas {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.pixi-canvas canvas {
  display: block;
  width: 100% !important;
  height: auto !important;
}

.multiplier-row {
  display: flex;
  justify-content: center;
  gap: 2px;
  padding: 6px 8px 0;
}
</style>
