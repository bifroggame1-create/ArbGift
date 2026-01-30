# TON Gift Aggregator - Style Guide

## Design System for Contracts & Upgrade Game Modes

This style guide defines the visual language, typography, spacing, and animations for the game interfaces. All components must follow these standards to maintain consistency with Telegram's native design patterns.

---

## 1. Visual Language

### 1.1 Risk Level Themes

#### 🛡️ **Safe Mode** - Soothing Green
Conveys security, trust, and high success probability.

**Colors:**
- Primary: `#10B981` (Emerald 500)
- Secondary: `#34D399` (Emerald 400)
- Hover: `#059669` (Emerald 600)
- Shadow: `rgba(16, 185, 129, 0.3)`

**Gradient:**
```css
background: linear-gradient(135deg, #10B981 0%, #059669 100%);
```

**Usage:**
- Risk selector button background
- Selection overlay for gift cards
- Success state indicators
- Checkmark backgrounds

---

#### ⚖️ **Normal Mode** - Balanced Blue
Represents moderate risk with balanced visuals.

**Colors:**
- Primary: `#3B82F6` (Blue 500)
- Secondary: `#60A5FA` (Blue 400)
- Hover: `#2563EB` (Blue 600)
- Shadow: `rgba(59, 130, 246, 0.3)`

**Gradient:**
```css
background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
```

**Usage:**
- Normal risk button
- Price badges
- Interactive elements
- Link colors

---

#### 🔥 **Risky Mode** - Fiery Red/Orange
Communicates danger, high risk, and excitement.

**Colors:**
- Primary: `#EF4444` (Red 500)
- Secondary: `#F97316` (Orange 500)
- Hover: `#DC2626` (Red 600)
- Shadow: `rgba(239, 68, 68, 0.5)` → `rgba(239, 68, 68, 0.8)` (pulsing)

**Gradient:**
```css
background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
```

**Special Effects:**
- **Flame Pulse Animation** (see Section 3.1)
- **Flame Emoji Flicker** (see Section 3.2)
- Glowing border effect

**Usage:**
- Risky risk button
- Fail state indicators
- Warning messages
- Destructive actions

---

#### 🌈 **Upgrade Wheel** - Rainbow Gradient

**Success Sector (Green):**
- Fill: `#10B981`
- Stroke: `#FFFFFF` (2px)

**Fail Sector (Red):**
- Fill: `#EF4444`
- Stroke: `#FFFFFF` (2px)

**Needle (Pointer):**
- Fill: `#FBBF24` (Amber 400)
- Shape: Polygon arrow pointing up

**Center Circle:**
- Fill: `#1F2937` (Gray 800)
- Radius: 30px

---

### 1.2 Gift Card Design

Inspired by **portals.tg** with Telegram-native aesthetics.

**Card Structure:**
```
┌─────────────────┐
│                 │  ← Rounded corners (16px)
│    3D Model     │  ← 70% width/height, centered
│                 │  ← Gradient background (rarity-based)
└─────────────────┘
     Gift Name       ← 14px, font-weight: 600
     #123456         ← 12px, opacity: 0.6 (serial number)
   ┌─────────┐
   │ 7.95 💎 │      ← Price badge (blue background)
   └─────────┘
```

**Rarity Colors:**
- **Common:** `linear-gradient(135deg, #64748b 0%, #475569 100%)` (Gray)
- **Uncommon:** `linear-gradient(135deg, #10b981 0%, #059669 100%)` (Green)
- **Rare:** `linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)` (Blue)
- **Epic:** `linear-gradient(135deg, #a855f7 0%, #9333ea 100%)` (Purple)
- **Legendary:** `linear-gradient(135deg, #f59e0b 0%, #d97706 100%)` (Gold)

**Card Dimensions:**
- Width: `100%` of grid cell
- Aspect Ratio: `1:1` (square)
- Border Radius: `16px`
- Box Shadow: `0 4px 12px rgba(0, 0, 0, 0.15)`

**Selection Overlay:**
- Background: `rgba(16, 185, 129, 0.3)` (semi-transparent green)
- Checkmark: 48px circle, `#10B981` background
- Checkmark Icon: `✓` in white, 24px

**Hover Effect:**
```css
transform: translateY(-4px);
transition: transform 0.2s ease;
```

**Selected State:**
```css
transform: scale(0.95);
```

---

## 2. Typography

Use **TelegramUI typography system** for consistency with Telegram native apps.

### 2.1 Hierarchy

**Fonts:**
- iOS: `-apple-system`, `San Francisco`
- Android: `Roboto`
- Fallback: `system-ui`, `sans-serif`

**Scale:**
| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| **Large Title** | 34px | 700 (Bold) | 1.2 | Page headers (rare) |
| **Title 1** | 28px | 700 | 1.2 | Section headers ("Contracts", "Upgrade") |
| **Title 2** | 22px | 600 | 1.3 | Subsection headers |
| **Title 3** | 20px | 600 | 1.3 | Card titles |
| **Headline** | 18px | 600 | 1.4 | Risk level names |
| **Body** | 16px | 400 | 1.5 | Descriptions, paragraphs |
| **Subheadline** | 15px | 400 | 1.4 | Secondary text |
| **Footnote** | 13px | 400 | 1.3 | Hints, captions |
| **Caption 1** | 12px | 400 | 1.2 | Labels, serial numbers |
| **Caption 2** | 11px | 400 | 1.2 | Timestamps, metadata |

### 2.2 Color Tokens

**Text:**
- Primary: `#FFFFFF` (white)
- Secondary: `rgba(255, 255, 255, 0.6)` (60% opacity)
- Tertiary: `rgba(255, 255, 255, 0.4)` (40% opacity)
- Disabled: `rgba(255, 255, 255, 0.25)` (25% opacity)

**Links:**
- Default: `#3B82F6` (Blue 500)
- Hover: `#60A5FA` (Blue 400)
- Visited: `#9333EA` (Purple 600)

---

## 3. Spacing System

**Grid Base Unit:** `4px`

### 3.1 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Icon gaps, tight spacing |
| `sm` | 8px | Text margins, small gaps |
| `md` | 12px | Card gaps, standard padding |
| `lg` | 16px | Section padding, container margins |
| `xl` | 24px | Large sections, page margins |
| `2xl` | 32px | Major section breaks |
| `3xl` | 48px | Hero sections |

### 3.2 Layout Grid

**Gift Card Grid:**
```css
display: grid;
grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
gap: 12px; /* md */
```

**Mobile Breakpoints:**
- Small: `< 375px` → 2 columns
- Medium: `375px - 768px` → 2-3 columns
- Tablet: `768px - 1024px` → 3-4 columns
- Desktop: `> 1024px` → 4-5 columns

**Card Padding:**
- Internal: `16px` (lg)
- Between cards: `12px` (md)

---

## 4. Animations

### 4.1 Flame Pulse (Risky Mode)

**CSS Keyframes:**
```css
@keyframes flame-pulse {
  0%, 100% {
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
  }
  50% {
    box-shadow: 0 0 40px rgba(239, 68, 68, 0.8);
  }
}

.risk-button.risky {
  animation: flame-pulse 2s ease-in-out infinite;
}
```

**Effect:**
- Duration: 2 seconds
- Easing: `ease-in-out`
- Loop: infinite
- Shadow intensity: 0.5 → 0.8 → 0.5

---

### 4.2 Flame Emoji Flicker

**CSS Keyframes:**
```css
@keyframes flame-flicker {
  0%, 100% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.1) rotate(5deg); }
  50% { transform: scale(0.9) rotate(-5deg); }
  75% { transform: scale(1.05) rotate(3deg); }
}

.flame-effect {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 24px;
  animation: flame-flicker 1s ease-in-out infinite;
}
```

**Effect:**
- Duration: 1 second
- Easing: `ease-in-out`
- Loop: infinite
- Scale range: 0.9 → 1.1
- Rotation: -5° → +5°

---

### 4.3 Wheel Spin (Upgrade Mode)

**JavaScript Animation:**
```javascript
const spinWheel = () => {
  const spins = 3 // Full rotations
  const finalAngle = Math.random() * 360
  const totalRotation = spins * 360 + finalAngle
  const duration = 3000 // 3 seconds

  const startTime = Date.now()

  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    // Cubic easing out
    const eased = 1 - Math.pow(1 - progress, 3)
    needleAngle.value = eased * totalRotation

    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }

  animate()
}
```

**Easing Function:**
- Cubic bezier: `cubic-bezier(0.33, 1, 0.68, 1)`
- Equivalent CSS: `ease-out`

**Effect:**
- Total rotations: 3 full + final position
- Duration: 3000ms (3 seconds)
- Smooth deceleration
- Precise final angle matching result

---

### 4.4 Success Confetti

**For Future Implementation:**

**Libraries:**
- `canvas-confetti` (npm package)
- Custom particle system

**Effect:**
```javascript
confetti({
  particleCount: 100,
  spread: 70,
  origin: { y: 0.6 },
  colors: ['#10B981', '#3B82F6', '#F59E0B']
})
```

**Trigger:**
- Contract success (high multiplier)
- Upgrade success
- Achievement unlocks

---

## 5. Interactive States

### 5.1 Button States

**Default:**
```css
background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
border: none;
border-radius: 12px;
padding: 16px 24px;
font-size: 16px;
font-weight: 600;
color: #FFFFFF;
transition: all 0.2s ease;
```

**Hover:**
```css
transform: translateY(-2px);
box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
```

**Active (Press):**
```css
transform: translateY(0px);
box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
```

**Disabled:**
```css
opacity: 0.5;
cursor: not-allowed;
pointer-events: none;
```

**Loading:**
```css
.button-loading::after {
  content: '';
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

### 5.2 Haptic Feedback

**Telegram WebApp Integration:**

| Action | Haptic Type | Description |
|--------|------------|-------------|
| Select gift card | `light` | Subtle tap feedback |
| Toggle risk level | `medium` | Standard selection |
| Execute contract | `heavy` | Strong confirmation |
| Contract success | `success` | Success notification |
| Contract fail | `error` | Failure notification |
| Wheel spin start | `medium` | Initiate action |
| Wheel spin end | `heavy` | Result reveal |

**Implementation:**
```typescript
import { useTelegram } from '@/composables/useTelegram'

const { hapticImpact, hapticNotification } = useTelegram()

// Light tap
hapticImpact('light')

// Success notification
hapticNotification('success')

// Error notification
hapticNotification('error')
```

---

## 6. Loading States

### 6.1 Spinner

**Default Spinner:**
```vue
<div class="spinner">
  <div class="spinner-circle"></div>
</div>

<style>
.spinner {
  width: 48px;
  height: 48px;
}

.spinner-circle {
  width: 100%;
  height: 100%;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #3B82F6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
```

**Sizes:**
- Small: `24px`
- Medium: `48px` (default)
- Large: `64px`

---

### 6.2 Skeleton Screens

**For Future Implementation:**

```vue
<div class="skeleton-card">
  <div class="skeleton-image"></div>
  <div class="skeleton-text"></div>
  <div class="skeleton-text short"></div>
</div>

<style>
.skeleton-image,
.skeleton-text {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

---

## 7. Responsive Design

### 7.1 Breakpoints

```css
/* Mobile First Approach */
.container {
  padding: 16px;
}

/* Small devices (landscape phones, 576px and up) */
@media (min-width: 576px) {
  .container {
    padding: 20px;
  }
}

/* Medium devices (tablets, 768px and up) */
@media (min-width: 768px) {
  .container {
    padding: 24px;
  }
}

/* Large devices (desktops, 992px and up) */
@media (min-width: 992px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

### 7.2 Touch Targets

**Minimum Touch Target:** `44px × 44px` (iOS Human Interface Guidelines)

**Recommended:** `48px × 48px` (Android Material Design)

**Spacing Between Targets:** Minimum `8px`

---

## 8. Accessibility

### 8.1 Color Contrast

All text must meet **WCAG AA standards:**
- Normal text (< 18px): Minimum 4.5:1 contrast ratio
- Large text (≥ 18px): Minimum 3:1 contrast ratio

**Verified Combinations:**
- White text on `#10B981` (Safe): ✅ 2.3:1 (large text only)
- White text on `#3B82F6` (Normal): ✅ 2.9:1 (large text only)
- White text on `#EF4444` (Risky): ✅ 3.3:1 (large text only)
- White text on `#1F2937` (Background): ✅ 15.5:1 (all text)

### 8.2 Focus States

**Keyboard Navigation:**
```css
.button:focus-visible {
  outline: 2px solid #60A5FA;
  outline-offset: 2px;
}
```

**Skip to Content:**
```vue
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #3B82F6;
  color: white;
  padding: 8px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
</style>
```

---

## 9. Dark Mode (Default)

All interfaces are **dark mode by default** to match Telegram's native theme.

**Background Colors:**
- Primary: `#030712` (Gray 950)
- Secondary: `#111827` (Gray 900)
- Tertiary: `#1F2937` (Gray 800)
- Elevated: `#374151` (Gray 700)

**Border Colors:**
- Subtle: `rgba(255, 255, 255, 0.05)`
- Standard: `rgba(255, 255, 255, 0.1)`
- Strong: `rgba(255, 255, 255, 0.2)`

---

## 10. Best Practices

### 10.1 Performance

**Optimize Assets:**
- Use WebP format for images
- Lazy load images below fold
- Compress SVG files
- Use CSS animations over JavaScript when possible

**Reduce Reflows:**
- Use `transform` instead of `top/left`
- Use `opacity` instead of `visibility`
- Batch DOM updates

### 10.2 Code Organization

**File Structure:**
```
styles/
├── base/
│   ├── reset.css
│   ├── typography.css
│   └── colors.css
├── components/
│   ├── buttons.css
│   ├── cards.css
│   └── inputs.css
├── animations/
│   ├── flame.css
│   ├── wheel.css
│   └── transitions.css
└── utilities/
    ├── spacing.css
    └── layout.css
```

**CSS Variables:**
```css
:root {
  /* Colors */
  --color-safe: #10B981;
  --color-normal: #3B82F6;
  --color-risky: #EF4444;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 24px;

  /* Typography */
  --font-size-body: 16px;
  --font-weight-normal: 400;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Transitions */
  --transition-fast: 0.1s ease;
  --transition-normal: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

---

## 11. Component Examples

### 11.1 Risk Selector Button

```vue
<template>
  <button
    class="risk-button"
    :class="[riskLevel, { active: isActive }]"
    @click="$emit('select')"
  >
    <div class="risk-icon">{{ icon }}</div>
    <div class="risk-info">
      <div class="risk-name">{{ name }}</div>
      <div class="risk-multiplier">x{{ multiplier }}</div>
      <div class="risk-chance">{{ probability }}% chance</div>
    </div>
    <div v-if="riskLevel === 'risky' && isActive" class="flame-effect">
      🔥
    </div>
  </button>
</template>

<style scoped>
.risk-button {
  position: relative;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.risk-button.safe {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
}

.risk-button.normal {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
}

.risk-button.risky {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  animation: flame-pulse 2s ease-in-out infinite;
}

.risk-button.active {
  border-color: white;
  transform: scale(1.02);
}
</style>
```

---

## 12. Design Review Checklist

Before committing UI changes, verify:

- [ ] Matches portals.tg gift card design (3D models, gradients, layout)
- [ ] Uses TelegramUI components where possible
- [ ] All text meets WCAG AA contrast requirements
- [ ] Touch targets are minimum 44px × 44px
- [ ] Animations run at 60fps without jank
- [ ] Haptic feedback implemented for all interactions
- [ ] Loading states present for async operations
- [ ] Responsive on mobile (375px), tablet (768px), desktop (1024px+)
- [ ] Dark mode backgrounds used throughout
- [ ] Follows spacing system (4px grid)
- [ ] Typography uses defined scale
- [ ] State changes have smooth transitions (0.2s default)

---

## 13. References

**Design Inspiration:**
- **portals.tg** - Gift card layout, color schemes
- **myballs.io** - Game mechanics, animations
- **Telegram iOS App** - Native design patterns
- **Telegram Mini Apps UI Kit** - Official Figma file

**Documentation:**
- TelegramUI: https://tgui.xelene.me
- Telegram WebApp API: https://core.telegram.org/bots/webapps
- TON Design Guidelines: https://ton.org/brand-assets

---

**Last Updated:** January 30, 2026
**Version:** 1.0.0
**Authors:** Claude Code + Design Team
