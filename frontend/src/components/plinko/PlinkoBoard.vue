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
const BALL_RADIUS = 8
const PEG_RADIUS = 6
const BOARD_PADDING_X = 30
const TOP_PADDING = 40
const BOTTOM_PADDING = 20

// ===== STATE =====
let boardWidth = 360
let boardHeight = 340
let pegSpacingX = 26
let pegSpacingY = 26

let app: PIXI.Application | null = null
let pegGraphics: PIXI.Graphics[] = []
let backgroundGraphics: PIXI.Graphics | null = null
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
  if (!pixiRef.value || !containerRef.value) {
    console.error('❌ [PlinkoBoard] Cannot init PixiJS - refs not available', {
      pixiRef: !!pixiRef.value,
      containerRef: !!containerRef.value
    })
    return
  }

  console.log('🎨 [PlinkoBoard] Starting PixiJS initialization...')

  // Use PixiJS resizeTo for automatic canvas sizing
  app = new PIXI.Application()
  await app.init({
    resizeTo: containerRef.value,
    backgroundAlpha: 0,
    antialias: true,
    resolution: Math.min(window.devicePixelRatio, 2),
    autoDensity: true,
  })

  pixiRef.value.appendChild(app.canvas as HTMLCanvasElement)

  // CRITICAL: Update board dimensions from actual canvas size
  boardWidth = app.screen.width
  boardHeight = app.screen.height

  console.log('🎨 [PlinkoBoard] PixiJS initialized:', {
    screenWidth: app.screen.width,
    screenHeight: app.screen.height,
    boardWidth,
    boardHeight,
    canvasElement: !!app.canvas
  })

  // Now compute layout and positions based on ACTUAL canvas size
  computeLayoutFromCanvas()
  computePegPositions()

  // Draw background elements
  drawBackground()

  // Draw drop zone gradient at top
  drawDropZone()

  // Create physics bodies now that we have positions
  createPhysicsBodies()

  // Draw pegs
  drawPegs()

  // Start render loop
  app.ticker.add(renderLoop)
  console.log('✅ [PlinkoBoard] Render loop started, ticker running:', app.ticker.started)
  console.log('✅ [PlinkoBoard] Ticker FPS:', app.ticker.FPS)
  console.log('✅ [PlinkoBoard] Matter engine exists:', !!mEngine)
  console.log('✅ [PlinkoBoard] Physics bodies in world:', mEngine?.world.bodies.length)
}

function computeLayoutFromCanvas() {
  // Canvas size is already set by PixiJS, now compute peg spacing
  const rows = props.rowCount

  // Compute horizontal spacing based on board width
  const bottomPegs = rows + 2
  pegSpacingX = (boardWidth - BOARD_PADDING_X * 2) / (bottomPegs - 1)

  // Compute vertical spacing based on available height
  // Reserve space for multipliers and gifts at bottom (100px total)
  const availableHeight = boardHeight - TOP_PADDING - BOTTOM_PADDING - 100
  pegSpacingY = availableHeight / (rows - 1)

  // Clamp spacing to reasonable values
  pegSpacingY = Math.max(20, Math.min(pegSpacingY, 40))

  console.log('📐 [PlinkoBoard] Layout from canvas:', {
    boardWidth,
    boardHeight,
    pegSpacingX,
    pegSpacingY,
    rows,
    availableHeight
  })
}

function drawPegs() {
  if (!app) return
  for (const g of pegGraphics) g.destroy()
  pegGraphics = []

  for (const { x, y } of pegPositions) {
    const g = new PIXI.Graphics()
    // Outer glow ring (bright cyan)
    g.circle(0, 0, PEG_RADIUS + 3)
    g.fill({ color: 0x00D9FF, alpha: 0.3 })
    // Main peg (bright cyan/blue)
    g.circle(0, 0, PEG_RADIUS)
    g.fill({ color: 0x00C3FF })
    // Inner highlight (white)
    g.circle(-1.5, -1.5, PEG_RADIUS * 0.4)
    g.fill({ color: 0xFFFFFF, alpha: 0.7 })
    g.position.set(x, y)
    app.stage.addChild(g)
    pegGraphics.push(g)
  }
}

function drawDropZone() {
  if (!app) return

  // Create drop zone gradient rectangle at top
  const dropZone = new PIXI.Graphics()

  // Draw gradient background (top to transparent)
  const gradient = dropZone.rect(0, 0, boardWidth, TOP_PADDING + 20)

  // Create gradient fill (cyan to transparent)
  gradient.fill({
    color: 0x00D9FF,
    alpha: 0.15,
  })

  // Add border line at bottom
  dropZone.moveTo(0, TOP_PADDING + 20)
  dropZone.lineTo(boardWidth, TOP_PADDING + 20)
  dropZone.stroke({ color: 0x00D9FF, width: 2, alpha: 0.3 })

  app.stage.addChildAt(dropZone, 0) // Add to back
}

function drawBackground() {
  if (!app) return

  // Clean up old background
  if (backgroundGraphics) {
    backgroundGraphics.destroy()
  }

  backgroundGraphics = new PIXI.Graphics()

  // Draw subtle grid pattern
  const gridSpacing = 30
  for (let x = 0; x < boardWidth; x += gridSpacing) {
    backgroundGraphics.moveTo(x, 0)
    backgroundGraphics.lineTo(x, boardHeight)
    backgroundGraphics.stroke({ color: 0x00D9FF, width: 0.5, alpha: 0.05 })
  }

  for (let y = 0; y < boardHeight; y += gridSpacing) {
    backgroundGraphics.moveTo(0, y)
    backgroundGraphics.lineTo(boardWidth, y)
    backgroundGraphics.stroke({ color: 0x00D9FF, width: 0.5, alpha: 0.05 })
  }

  // Add subtle vignette effect at edges
  const vignette = new PIXI.Graphics()

  // Left edge
  vignette.rect(0, 0, 30, boardHeight)
  vignette.fill({ color: 0x000000, alpha: 0.1 })

  // Right edge
  vignette.rect(boardWidth - 30, 0, 30, boardHeight)
  vignette.fill({ color: 0x000000, alpha: 0.1 })

  backgroundGraphics.addChild(vignette)
  app.stage.addChildAt(backgroundGraphics, 0)
}

// ===== MATTER.JS SETUP =====

function initMatter() {
  mEngine = Matter.Engine.create({
    gravity: { x: 0, y: 1, scale: 0.005 },
  })

  // Enable better collision detection
  mEngine.positionIterations = 10
  mEngine.velocityIterations = 8

  console.log('⚙️ [PlinkoBoard] Matter.js initialized', {
    gravity: mEngine.gravity,
    positionIterations: mEngine.positionIterations,
    velocityIterations: mEngine.velocityIterations
  })
}

function createPhysicsBodies() {
  if (!mEngine) return

  // Clear existing bodies
  Matter.Composite.clear(mEngine.world, false)

  // Peg bodies (static circles)
  pegBodies = []
  for (const { x, y } of pegPositions) {
    const peg = Matter.Bodies.circle(x, y, PEG_RADIUS, {
      isStatic: true,
      restitution: 0.8,
      friction: 0.01,
      frictionStatic: 0.01,
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

  console.log('🎯 [PlinkoBoard] Physics bodies created:', {
    pegs: pegBodies.length,
    boardWidth,
    boardHeight
  })

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
  if (!app || !mEngine) {
    console.error('❌ [PlinkoBoard] Cannot drop ball - app or engine not initialized', { app: !!app, mEngine: !!mEngine })
    return
  }

  console.log('🎯 [PlinkoBoard] dropBall called', { dropIndex, pathLength: path.length, boardWidth, boardHeight })

  // Determine target slot from path endpoint
  const numSlots = props.rowCount + 1
  let targetSlot = 0
  if (path.length > 0) {
    const lastX = path[path.length - 1][0]
    targetSlot = Math.round(lastX * (numSlots - 1))
    targetSlot = Math.max(0, Math.min(numSlots - 1, targetSlot))
  }

  // Drop from top center with slight random offset
  const startX = boardWidth / 2 + (Math.random() - 0.5) * 8
  const startY = 10

  console.log('🎯 [PlinkoBoard] Creating ball at', { startX, startY, targetSlot })

  const body = Matter.Bodies.circle(startX, startY, BALL_RADIUS, {
    restitution: 0.75,
    friction: 0.01,
    frictionStatic: 0.01,
    density: 0.005,
    frictionAir: 0.01,
    label: 'ball',
  })

  // Initial downward velocity for immediate drop
  Matter.Body.setVelocity(body, { x: 0, y: 5 })
  Matter.Composite.add(mEngine.world, body)

  console.log('✅ [PlinkoBoard] Ball added to physics world', {
    bodyId: body.id,
    position: body.position,
    velocity: body.velocity
  })

  const graphic = new PIXI.Graphics()
  // Ball glow (cyan)
  graphic.circle(0, 0, BALL_RADIUS + 5)
  graphic.fill({ color: 0x00D9FF, alpha: 0.3 })
  // Ball body (white/yellow)
  graphic.circle(0, 0, BALL_RADIUS)
  graphic.fill({ color: 0xFFEB3B })
  // Inner highlight
  graphic.circle(-2, -2, BALL_RADIUS * 0.4)
  graphic.fill({ color: 0xFFFFFF, alpha: 0.8 })
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

  console.log('✅ [PlinkoBoard] Ball added to activeBalls', {
    totalActiveBalls: activeBalls.length
  })
}

// ===== RENDER LOOP =====

let frameCounter = 0
function renderLoop() {
  if (!mEngine) return

  frameCounter++

  // Log every 60 frames (once per second at 60fps)
  if (frameCounter % 60 === 0) {
    console.log('🔄 [PlinkoBoard] Render loop running', {
      frame: frameCounter,
      activeBalls: activeBalls.length,
      worldBodies: mEngine.world.bodies.length,
      gravity: mEngine.gravity
    })
  }

  // Step physics with fixed timestep for consistent behavior
  Matter.Engine.update(mEngine, 16.666)

  // Update peg glow
  updatePegGlow()

  // Update balls
  let anyActive = false
  for (const ball of activeBalls) {
    if (ball.landed) continue
    anyActive = true
    ball.frameCount++

    // Log ball position every 30 frames (half second)
    if (ball.frameCount % 30 === 0) {
      console.log('🏐 [PlinkoBoard] Ball update', {
        dropIndex: ball.dropIndex,
        frameCount: ball.frameCount,
        position: { x: Math.round(ball.body.position.x), y: Math.round(ball.body.position.y) },
        velocity: { x: ball.body.velocity.x.toFixed(2), y: ball.body.velocity.y.toFixed(2) },
        boardHeight,
        progress: (ball.body.position.y / boardHeight * 100).toFixed(1) + '%'
      })
    }

    // Sync PixiJS to Matter.js position
    ball.graphic.position.set(ball.body.position.x, ball.body.position.y)

    // Very gentle steering toward target slot (only in bottom third)
    const progress = ball.body.position.y / boardHeight
    if (progress > 0.65 && ball.targetSlot >= 0) {
      const numSlots = props.rowCount + 1
      const bottomRowWidth = numSlots * pegSpacingX
      const slotStartX = (boardWidth - bottomRowWidth) / 2
      const targetX = slotStartX + (ball.targetSlot + 0.5) * (bottomRowWidth / numSlots)

      const dx = targetX - ball.body.position.x
      // Very subtle force - just a gentle nudge
      const strength = 0.00002 * (progress - 0.65) * 3
      Matter.Body.applyForce(ball.body, ball.body.position, { x: dx * strength, y: 0 })
    }

    // Speed limiter — prevent unrealistic speeds
    const vel = ball.body.velocity
    const maxSpeed = 8
    const speed = Math.sqrt(vel.x * vel.x + vel.y * vel.y)
    if (speed > maxSpeed) {
      const scale = maxSpeed / speed
      Matter.Body.setVelocity(ball.body, { x: vel.x * scale, y: vel.y * scale })
    }

    // Trail particles (cyan)
    if (app && Math.random() > 0.7) {
      const trail = new PIXI.Graphics()
      trail.circle(0, 0, 2 + Math.random() * 2)
      trail.fill({ color: 0x00D9FF, alpha: 0.5 })
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

    // Check if ball reached bottom (or timeout after 15s = 900 frames)
    if (ball.body.position.y >= boardHeight - 30 || ball.frameCount > 900) {
      ball.landed = true

      // Use server-determined slot for consistency with payout
      const finalSlot = ball.targetSlot >= 0 ? ball.targetSlot : 0
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
      // Animated glow ring (bright cyan)
      g.circle(0, 0, PEG_RADIUS + 5 * t)
      g.fill({ color: 0x00FFFF, alpha: 0.5 * t })
      // Core peg (lit up bright)
      g.circle(0, 0, PEG_RADIUS)
      g.fill({ color: lerpColor(0x00C3FF, 0x00FFFF, t) })
      // Inner highlight
      g.circle(-1.5, -1.5, PEG_RADIUS * 0.4)
      g.fill({ color: 0xFFFFFF, alpha: 0.9 * t })
      pegGlowTimers.set(idx, frames - 1)
    } else {
      pegGlowTimers.delete(idx)
      g.clear()
      g.circle(0, 0, PEG_RADIUS + 3)
      g.fill({ color: 0x00D9FF, alpha: 0.3 })
      g.circle(0, 0, PEG_RADIUS)
      g.fill({ color: 0x00C3FF })
      g.circle(-1.5, -1.5, PEG_RADIUS * 0.4)
      g.fill({ color: 0xFFFFFF, alpha: 0.7 })
    }
  }
}

function spawnBurst(x: number, y: number) {
  if (!app) return
  for (let i = 0; i < 8; i++) {
    const p = new PIXI.Graphics()
    p.circle(0, 0, 2 + Math.random() * 3)
    p.fill({ color: 0xFFEB3B, alpha: 0.8 })
    p.position.set(x, y)
    app.stage.addChild(p)

    const angle = (Math.PI * 2 * i) / 8
    const vx = Math.cos(angle) * (3 + Math.random() * 2)
    const vy = Math.sin(angle) * (3 + Math.random() * 2) - 2
    let life = 20
    const anim = () => {
      p.position.x += vx
      p.position.y += vy + (20 - life) * 0.1
      p.alpha -= 0.05
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
  console.log('🔄 [PlinkoBoard] Rebuilding...')
  cleanup()
  await nextTick()

  // Initialize Matter.js first
  initMatter()

  // Initialize PixiJS - this will compute layout and positions
  await initPixi()
}

function cleanup() {
  for (const ball of activeBalls) {
    ball.graphic.destroy()
    for (const t of ball.trail) t.destroy()
  }
  activeBalls = []
  if (backgroundGraphics) { backgroundGraphics.destroy(); backgroundGraphics = null }
  if (app) { app.destroy(true, { children: true }); app = null }
  pegGraphics = []
  if (mEngine) { Matter.Engine.clear(mEngine); mEngine = null }
  pegBodies = []
  pegGlowTimers.clear()
}

onMounted(async () => {
  await nextTick() // Wait for DOM to render
  console.log('🚀 [PlinkoBoard] Mounted, initializing...')

  // Initialize Matter.js physics first (doesn't need exact dimensions yet)
  initMatter()

  // Initialize PixiJS - this will set boardWidth/boardHeight and compute layout
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
  height: 100%;
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
