# MyBalls.io Trading - Style Guide

## Color Palette

### Primary Colors
| Name | HEX | RGB | Usage |
|------|-----|-----|-------|
| Buy Green | `#09D76D` | `rgb(9, 215, 109)` | Buy button, positive P/L, green candles |
| Sell Red | `#FF394E` | `rgb(255, 57, 78)` | Crash state, negative P/L, red candles |
| Cyan Accent | `#34CDEF` | `rgb(52, 205, 239)` | Price line (dashed), TON icon accent |
| Blue Link | `#0098EA` | `rgb(0, 152, 234)` | TON blue, links |

### Background Colors
| Name | HEX | RGB | Usage |
|------|-----|-----|-------|
| App Background | `#0C0C0C` | `rgb(12, 12, 12)` | Main app background |
| Card Background | `#0E0F14` | `rgb(14, 15, 20)` | Chart container, panels |
| Card Surface | `#181818` | `rgb(24, 24, 24)` | Traders panel, elevated cards |
| Button Background | `#414244` | `rgb(65, 66, 68)` | Bet amount buttons (inactive) |
| Button Hover | `#2D2E30` | `rgb(45, 46, 48)` | Button hover state |
| Border Color | `#262729` | `rgb(38, 39, 41)` | Card borders, dividers |

### Text Colors
| Name | HEX | RGB | Usage |
|------|-----|-----|-------|
| Primary Text | `#FFFFFF` | `rgb(255, 255, 255)` | Main text, multiplier |
| Secondary Text | `#808080` | `rgb(128, 128, 128)` | Labels, Y-axis values |
| Muted Text | `#6D6D71` | `rgba(255,255,255,0.5)` | Inactive states |

---

## Typography

### Font Families
```css
/* Primary UI font */
font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;

/* Monospace for numbers/multiplier */
font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
```

### Font Sizes
| Element | Size | Weight |
|---------|------|--------|
| Multiplier (large) | 48px | 700 (Bold) |
| Multiplier (medium) | 32px | 600 (Semibold) |
| Button text | 16px | 600 (Semibold) |
| Bet amount | 14px | 500 (Medium) |
| Y-axis labels | 12px | 400 (Regular) |
| Status text | 11px | 500 (Medium) |

---

## Spacing & Sizing

### Border Radius
| Element | Radius |
|---------|--------|
| Buy/Sell button | 20px |
| Bet amount buttons | 16px |
| Chart container | 24px |
| Traders panel | 20px |
| Tournament banner | 24px (pill) |

### Padding
| Element | Padding |
|---------|---------|
| Chart container | 16px |
| Traders panel | 12px 16px |
| Buttons | 12px 20px |
| Bet buttons | 8px 16px |

### Gaps
| Element | Gap |
|---------|-----|
| Bet buttons row | 8px |
| Control sections | 16px |
| Main sections | 12px |

---

## Component Specifications

### Chart Container
```css
.chart-container {
  background: #0E0F14;
  border: 1px solid #262729;
  border-radius: 24px;
  aspect-ratio: 1; /* Square on mobile */
  position: relative;
  overflow: hidden;
}
```

### Y-Axis
- Position: Left side, inside chart
- Labels: 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00+ (dynamic)
- Color: `#808080` (gray)
- Font: 12px monospace
- Horizontal grid lines: `rgba(255,255,255,0.05)`

### Price Line (Dashed)
```css
.price-line {
  stroke: #34CDEF;
  stroke-width: 2px;
  stroke-dasharray: 8, 6;
  /* Animates horizontally */
}
```

### Multiplier Display
```css
.multiplier {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-family: monospace;
  font-size: 48px;
  font-weight: 700;
  color: #FFFFFF; /* Default */
}

.multiplier.positive { color: #09D76D; }
.multiplier.negative { color: #FF394E; }
.multiplier.crashed {
  color: #FF394E;
  animation: shake 0.5s;
}
```

### Candlestick Chart
```css
/* Candle body */
.candle-body {
  width: 6px;
  border-radius: 1px;
}

.candle-body.bullish { fill: #09D76D; }
.candle-body.bearish { fill: #FF394E; }

/* Candle wick */
.candle-wick {
  width: 1px;
}

.candle-wick.bullish { stroke: #09D76D; }
.candle-wick.bearish { stroke: #FF394E; }
```

### Buy Button
```css
.buy-button {
  background: #09D76D;
  color: #101010;
  border: none;
  border-radius: 20px;
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 600;
  width: 100%;
  max-width: 200px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.buy-button:hover {
  opacity: 0.9;
}

.buy-button:active {
  transform: scale(0.98);
}
```

### Sell Button (appears after buying)
```css
.sell-button {
  background: linear-gradient(135deg, #FF394E 0%, #FF6B7A 100%);
  color: #FFFFFF;
  /* Same dimensions as buy button */
}
```

### Bet Amount Buttons
```css
.bet-button {
  background: #414244;
  color: #FFFFFF;
  border: none;
  border-radius: 16px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.bet-button:hover {
  background: #2D2E30;
}

.bet-button.selected {
  background: #34CDEF;
  color: #101010;
}

.bet-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
```

### Traders Panel
```css
.traders-panel {
  background: #181818;
  border-radius: 20px;
  padding: 12px 16px;
}

.traders-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
}

.traders-count {
  color: #808080;
}

.trader-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #262729;
}

.trader-item.exited {
  background: rgba(9, 215, 109, 0.1);
}

.trader-profit {
  color: #09D76D;
  font-weight: 600;
}
```

### Tournament Banner
```css
.tournament-banner {
  background: linear-gradient(135deg, #0098EA 0%, #006AFF 100%);
  border-radius: 24px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #FFFFFF;
  font-weight: 600;
}
```

### Bottom Navigation
```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #0C0C0C;
  display: flex;
  justify-content: space-around;
  padding: 8px 0 20px; /* extra for safe area */
  border-top: 1px solid #262729;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #808080;
  font-size: 11px;
}

.nav-item.active {
  color: #34CDEF;
}
```

---

## Animations

### Multiplier Pulse (when active)
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.multiplier.active {
  animation: pulse 1s infinite;
}
```

### Crash Shake
```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
```

### Candle Appear
```css
@keyframes candleGrow {
  from {
    transform: scaleY(0);
    transform-origin: bottom;
  }
  to {
    transform: scaleY(1);
  }
}
```

### Toast Notification (buy/sell events)
```css
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(24, 24, 24, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 8px 16px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
```

---

## Icons

### TON Diamond
- Used in: bet buttons, balance display
- Color: `#34CDEF` (cyan) or white
- Size: 16px in buttons, 20px in balance

### Ping Indicator
- Position: Top-left of chart
- Format: "69ms" with WiFi icon
- Color: Green if <100ms, yellow if <200ms, red if >200ms

---

## Responsive Breakpoints

```css
/* Mobile (default) */
.chart-container {
  aspect-ratio: 1; /* Square */
}

/* Tablet and up */
@media (min-width: 768px) {
  .chart-container {
    aspect-ratio: 16/9;
  }
}
```

---

## Dark Theme Variables (CSS Custom Properties)

```css
:root {
  /* Colors */
  --color-buy: #09D76D;
  --color-sell: #FF394E;
  --color-accent: #34CDEF;
  --color-blue: #0098EA;

  /* Backgrounds */
  --bg-app: #0C0C0C;
  --bg-card: #0E0F14;
  --bg-surface: #181818;
  --bg-button: #414244;
  --bg-button-hover: #2D2E30;

  /* Text */
  --text-primary: #FFFFFF;
  --text-secondary: #808080;
  --text-muted: rgba(255, 255, 255, 0.5);

  /* Borders */
  --border-color: #262729;

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 20px;
  --radius-xl: 24px;

  /* Spacing */
  --gap-sm: 8px;
  --gap-md: 12px;
  --gap-lg: 16px;
}
```
