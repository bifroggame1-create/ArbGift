<template>
  <div ref="containerRef" class="plinko-board-container">
    <div ref="pixiRef" class="pixi-canvas"></div>
    <!-- Multiplier slots below canvas -->
    <div class="multiplier-row">
      <div
        v-for="(mult, i) in multipliers"
        :key="i"
        :class="['mult-slot', getMultClass(mult)]"
      >
        {{ formatMult(mult) }}
      </div>
    </div>
    <!-- Gift prizes row -->
    <div class="gift-row">
      <div v-for="(_m, i) in multipliers" :key="'g'+i" class="gift-cell">
        <video
          class="gift-video"
          :src="`/gifts/gift-${(i % 13) + 1}.webm`"
          autoplay
          loop
          muted
          playsinline
        />
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

// ===== CONSTANTS =====
const BALL_RADIUS = 6
const PEG_RADIUS = 5.5
const BOARD_PADDING_X = 20
const TOP_PADDING = 20
const BOTTOM_PADDING = 8

// ===== STATE =====
let boardWidth = 360
let boardHeight = 340
let pegSpacingX = 26
let pegSpacingY = 26

let app: PIXI.Application | null = null
let pegGraphics: PIXI.Graphics[] = []
let mEngine: Matter.Engine | null = null
let pegBodies: Matter.Body[] = []
let pegPositions: { x: number; y: number }[] = []
let pegGlowTimers: Map<number, number> = new Map()
let hasEmittedAllLanded = false

interface ActiveBall {
  body: Matter.Body
  graphic: PIXI.Graphics
  trail: PIXI.Graphics[]
  path: number[][]
  dropIndex: number
  landed: boolean
  targetSlot: number
  frameCount: number
}
let activeBalls: ActiveBall[] = []

// ===== PYRAMID PEG LAYOUT =====
// Classic Plinko: row 0 has 3 pegs, row 1 has 4, ..., row N-1 has N+2
// Pegs in odd rows offset by half spacing horizontally
// Number of slots at bottom = rowCount + 1

function computeLayout() {
  if (!containerRef.value) return
  boardWidth = containerRef.value.clientWidth
  const rows = props.rowCount

  // Compute spacing based on board width and bottom row (widest)
  const bottomPegs = rows + 2
  pegSpacingX = (boardWidth - BOARD_PADDING_X * 2) / (bottomPegs - 1)
  pegSpacingY = Math.min(pegSpacingX * 0.85, 28) // compact vertical spacing
  boardHeight = TOP_PADDING + (rows - 1) * pegSpacingY + BOTTOM_PADDING + 16
}

function computePegPositions() {
  pegPositions = []
  const rows = props.rowCount

  for (let row = 0; row < rows; row++) {
    const pegsInRow = row + 3 // 3, 4, 5, ..., rows+2
    const rowWidth = (pegsInRow - 1) * pegSpacingX
    const startX = (boardWidth - rowWidth) / 2
    const y = TOP_PADDING + row * pegSpacingY

    for (let col = 0; col < pegsInRow; col++) {
      pegPositions.push({
        x: startX + col * pegSpacingX,
        y,
      })
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
  for (const g of pegGraphics) g.destroy()
  pegGraphics = []

  for (const { x, y } of pegPositions) {
    const g = new PIXI.Graphics()
    // Outer glow ring
    g.circle(0, 0, PEG_RADIUS + 2)
    g.fill({ color: 0x6B2FBE, alpha: 0.15 })
    // Main peg
    g.circle(0, 0, PEG_RADIUS)
    g.fill({ color: 0x5A2D7A })
    // Inner highlight
    g.circle(-1, -1, PEG_RADIUS * 0.4)
    g.fill({ color: 0x8B5CF6, alpha: 0.3 })
    g.position.set(x, y)
    app.stage.addChild(g)
    pegGraphics.push(g)
  }
}

// ===== MATTER.JS SETUP =====

function initMatter() {
  mEngine = Matter.Engine.create({
    gravity: { x: 0, y: 1.2, scale: 0.001 },
  })

  // Peg bodies (static circles, slightly larger than visual for reliable bouncing)
  pegBodies = []
  for (const { x, y } of pegPositions) {
    const peg = Matter.Bodies.circle(x, y, PEG_RADIUS * 0.75, {
      isStatic: true,
      restitution: 0.6,
      friction: 0.05,
      label: 'peg',
    })
    pegBodies.push(peg)
  }

  // Left & right walls
  const wallT = 10
  const leftWall = Matter.Bodies.rectangle(
    -wallT / 2, boardHeight / 2, wallT, boardHeight * 2,
    { isStatic: true, restitution: 0.3 }
  )
  const rightWall = Matter.Bodies.rectangle(
    boardWidth + wallT / 2, boardHeight / 2, wallT, boardHeight * 2,
    { isStatic: true, restitution: 0.3 }
  )

  // Floor to catch balls
  const floor = Matter.Bodies.rectangle(
    boardWidth / 2, boardHeight + 10, boardWidth * 2, 20,
    { isStatic: true, label: 'floor' }
  )

  Matter.Composite.add(mEngine.world, [...pegBodies, leftWall, rightWall, floor])

  // Peg glow on collision
  Matter.Events.on(mEngine, 'collisionStart', (event) => {
    for (const pair of event.pairs) {
      const idx1 = pegBodies.indexOf(pair.bodyA)
      const idx2 = pegBodies.indexOf(pair.bodyB)
      const idx = idx1 >= 0 ? idx1 : idx2
      if (idx >= 0) {
        pegGlowTimers.set(idx, 10)
      }
    }
  })
}

// ===== BALL DROP =====

function dropBall(path: number[][], dropIndex: number) {
  if (!app || !mEngine) return

  // Determine target slot from path endpoint
  const numSlots = props.rowCount + 1
  let targetSlot = 0
  if (path.length > 0) {
    const lastX = path[path.length - 1][0]
    targetSlot = Math.round(lastX * (numSlots - 1))
    targetSlot = Math.max(0, Math.min(numSlots - 1, targetSlot))
  }

  // Drop from top center with slight random offset
  const startX = boardWidth / 2 + (Math.random() - 0.5) * 4
  const startY = 5

  const body = Matter.Bodies.circle(startX, startY, BALL_RADIUS * 0.65, {
    restitution: 0.5,
    friction: 0.02,
    density: 0.003,
    frictionAir: 0.015,
    label: 'ball',
  })

  // Small initial downward velocity
  Matter.Body.setVelocity(body, { x: 0, y: 1 })
  Matter.Composite.add(mEngine.world, body)

  const graphic = new PIXI.Graphics()
  // Ball glow
  graphic.circle(0, 0, BALL_RADIUS + 4)
  graphic.fill({ color: 0x6B2FBE, alpha: 0.2 })
  // Ball body
  graphic.circle(0, 0, BALL_RADIUS)
  graphic.fill({ color: 0xFDFDFD })
  // Inner highlight
  graphic.circle(-1.5, -1.5, BALL_RADIUS * 0.35)
  graphic.fill({ color: 0xFFFFFF, alpha: 0.6 })
  graphic.position.set(startX, startY)
  app.stage.addChild(graphic)

  hasEmittedAllLanded = false

  activeBalls.push({
    body,
    graphic,
    trail: [],
    path,
    dropIndex,
    landed: false,
    targetSlot,
    frameCount: 0,
  })
}

// ===== RENDER LOOP =====

function renderLoop() {
  if (!mEngine) return

  // Step physics (run 2 sub-steps for stability)
  Matter.Engine.update(mEngine, 1000 / 60)

  // Update peg glow
  updatePegGlow()

  // Update balls
  let anyActive = false
  for (const ball of activeBalls) {
    if (ball.landed) continue
    anyActive = true
    ball.frameCount++

    // Sync PixiJS to Matter.js position
    ball.graphic.position.set(ball.body.position.x, ball.body.position.y)

    // Gentle steering toward target slot (only in lower half)
    const progress = ball.body.position.y / boardHeight
    if (progress > 0.5) {
      const numSlots = props.rowCount + 1
      const bottomRowWidth = (numSlots) * pegSpacingX
      const slotStartX = (boardWidth - bottomRowWidth) / 2
      const targetX = slotStartX + (ball.targetSlot + 0.5) * (bottomRowWidth / numSlots)

      const dx = targetX - ball.body.position.x
      const strength = 0.00004 * (progress - 0.5) * 2 // ramp up gently
      Matter.Body.applyForce(ball.body, ball.body.position, { x: dx * strength, y: 0 })
    }

    // Speed limiter — prevent ball from going too fast horizontally
    const vel = ball.body.velocity
    const maxVx = 4
    if (Math.abs(vel.x) > maxVx) {
      Matter.Body.setVelocity(ball.body, { x: Math.sign(vel.x) * maxVx, y: vel.y })
    }

    // Trail particles (sparse)
    if (app && Math.random() > 0.7) {
      const trail = new PIXI.Graphics()
      trail.circle(0, 0, 1.5 + Math.random() * 1.5)
      trail.fill({ color: 0x6B2FBE, alpha: 0.4 })
      trail.position.set(ball.body.position.x, ball.body.position.y)
      app.stage.addChild(trail)
      ball.trail.push(trail)
    }

    // Fade trail
    for (let i = ball.trail.length - 1; i >= 0; i--) {
      const t = ball.trail[i]
      t.alpha -= 0.04
      if (t.alpha <= 0) {
        t.destroy()
        ball.trail.splice(i, 1)
      }
    }

    // Check if ball reached bottom (or timeout after 10s = 600 frames)
    if (ball.body.position.y >= boardHeight - 5 || ball.frameCount > 600) {
      ball.landed = true

      // Determine actual landing slot from X position
      const numSlots = props.rowCount + 1
      const bottomRowWidth = numSlots * pegSpacingX
      const slotStartX = (boardWidth - bottomRowWidth) / 2
      const relX = ball.body.position.x - slotStartX
      let slotIndex = Math.floor(relX / (bottomRowWidth / numSlots))
      slotIndex = Math.max(0, Math.min(numSlots - 1, slotIndex))

      // Prefer server-determined slot
      const finalSlot = ball.targetSlot
      emit('landed', finalSlot, ball.dropIndex)

      spawnBurst(ball.body.position.x, ball.body.position.y)
      Matter.Composite.remove(mEngine!.world, ball.body)

      // Fade out
      const fadeOut = () => {
        ball.graphic.alpha -= 0.15
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

  // Clean up done balls
  activeBalls = activeBalls.filter(b => !b.landed || b.graphic.alpha > 0)

  // Emit allLanded
  if (!anyActive && activeBalls.length === 0 && !hasEmittedAllLanded) {
    hasEmittedAllLanded = true
    emit('allLanded')
  }
}

function updatePegGlow() {
  for (const [idx, frames] of pegGlowTimers.entries()) {
    const g = pegGraphics[idx]
    if (!g) { pegGlowTimers.delete(idx); continue }

    if (frames > 0) {
      const t = frames / 10
      g.clear()
      // Animated glow ring
      g.circle(0, 0, PEG_RADIUS + 3 * t)
      g.fill({ color: 0x8B5CF6, alpha: 0.3 * t })
      // Core peg (lit up)
      g.circle(0, 0, PEG_RADIUS)
      g.fill({ color: lerpColor(0x5A2D7A, 0xA78BFA, t) })
      // Inner highlight
      g.circle(-1, -1, PEG_RADIUS * 0.4)
      g.fill({ color: 0xC4B5FD, alpha: 0.4 * t })
      pegGlowTimers.set(idx, frames - 1)
    } else {
      pegGlowTimers.delete(idx)
      g.clear()
      g.circle(0, 0, PEG_RADIUS + 2)
      g.fill({ color: 0x6B2FBE, alpha: 0.15 })
      g.circle(0, 0, PEG_RADIUS)
      g.fill({ color: 0x5A2D7A })
      g.circle(-1, -1, PEG_RADIUS * 0.4)
      g.fill({ color: 0x8B5CF6, alpha: 0.3 })
    }
  }
}

function spawnBurst(x: number, y: number) {
  if (!app) return
  for (let i = 0; i < 6; i++) {
    const p = new PIXI.Graphics()
    p.circle(0, 0, 2 + Math.random() * 2)
    p.fill({ color: 0x6B2FBE, alpha: 0.7 })
    p.position.set(x, y)
    app.stage.addChild(p)

    const vx = (Math.random() - 0.5) * 5
    const vy = -Math.random() * 3 - 1
    let life = 15
    const anim = () => {
      p.position.x += vx
      p.position.y += vy + (15 - life) * 0.15
      p.alpha -= 0.06
      life--
      if (life <= 0 || p.alpha <= 0) p.destroy()
      else requestAnimationFrame(anim)
    }
    anim()
  }
}

// ===== UTILITIES =====

function lerpColor(a: number, b: number, t: number): number {
  const ar = (a >> 16) & 0xFF, ag = (a >> 8) & 0xFF, ab = a & 0xFF
  const br = (b >> 16) & 0xFF, bg = (b >> 8) & 0xFF, bb = b & 0xFF
  return (Math.round(ar + (br - ar) * t) << 16)
       | (Math.round(ag + (bg - ag) * t) << 8)
       | Math.round(ab + (bb - ab) * t)
}

function getMultClass(mult: number): string {
  if (mult >= 100) return 'extreme'
  if (mult >= 10) return 'high'
  if (mult >= 2) return 'medium'
  if (mult >= 1) return 'low'
  return 'center'
}

function formatMult(mult: number): string {
  if (mult >= 100) return mult.toFixed(0) + 'x'
  if (mult >= 10) return mult.toFixed(1) + 'x'
  return mult.toFixed(1) + 'x'
}

// ===== LIFECYCLE =====

async function rebuild() {
  cleanup()
  await nextTick()
  computeLayout()
  computePegPositions()
  initMatter()
  await initPixi()
}

function cleanup() {
  for (const ball of activeBalls) {
    ball.graphic.destroy()
    for (const t of ball.trail) t.destroy()
  }
  activeBalls = []
  if (app) { app.destroy(true, { children: true }); app = null }
  pegGraphics = []
  if (mEngine) { Matter.Engine.clear(mEngine); mEngine = null }
  pegBodies = []
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

defineExpose({ dropBall })
</script>

<style scoped>
.plinko-board-container {
  width: 100%;
  position: relative;
  flex-shrink: 1;
}

.pixi-canvas {
  width: 100%;
}

.pixi-canvas :deep(canvas) {
  display: block;
  width: 100% !important;
  height: auto !important;
}

.multiplier-row {
  display: flex;
  justify-content: center;
  gap: 2px;
  padding: 6px 4px 0;
  flex-wrap: nowrap;
  overflow-x: auto;
}

.mult-slot {
  flex: 1;
  min-width: 0;
  text-align: center;
  border-radius: 4px;
  padding: 4px 2px;
  font-size: 10px;
  font-weight: 700;
  font-family: 'CoFo Sans Mono', 'SF Mono', monospace;
  white-space: nowrap;
}

.mult-slot.extreme { background: rgba(226, 53, 53, 0.3); color: #E23535; }
.mult-slot.high { background: rgba(177, 76, 38, 0.3); color: #B14C26; }
.mult-slot.medium { background: rgba(255, 197, 2, 0.2); color: #FFC502; }
.mult-slot.low { background: rgba(0, 255, 98, 0.15); color: #00FF62; }
.mult-slot.center { background: rgba(128, 128, 128, 0.15); color: #808080; }

.gift-row {
  display: flex;
  justify-content: center;
  gap: 2px;
  padding: 4px 4px 0;
}

.gift-cell {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gift-video {
  width: 100%;
  max-width: 32px;
  height: auto;
  border-radius: 4px;
  pointer-events: none;
}
</style>
