# MyBalls.io Style Guide

Pixel-perfect reference extracted from https://myballs.io

---

## 1. Color Tokens

### Core Colors
| Token | HEX | Usage |
|-------|-----|-------|
| `--color-c-1` | `#34CDEF` | Primary cyan/blue accent (buttons, active states, highlights) |
| `--color-c-2` | `#00FF62` | Green accent (win, success) |
| `--color-c-3` | `#E23535` | Red accent (loss, danger, down) |
| `--color-c-4` | `#FFC502` | Yellow/Gold accent |
| `--color-c-10` | `#0C0C0C` | Main dark background |

### Background Colors
| Color | HEX/Value | Usage |
|-------|-----------|-------|
| Page background | `#0C0C0C` | html background |
| Card background | `rgba(255, 255, 255, 0.05)` | Gift cards, containers |
| Secondary surface | `#1B1B1B` / `rgb(27, 27, 27)` | Elevated surfaces, panels |
| Button active | `#007AFF` | iOS-style blue buttons |
| White 20% | `rgba(255, 255, 255, 0.2)` | Subtle borders, overlays |
| White 5% | `rgba(255, 255, 255, 0.05)` | Card backgrounds |

### Text Colors
| Color | Value | Usage |
|-------|-------|-------|
| Primary text | `#FFFFFF` | Headings, body |
| Muted text | `rgba(255, 255, 255, 0.5)` | Hints, secondary info |
| Inactive nav | `#808080` | Bottom nav inactive items |
| Gray | `rgb(128, 128, 128)` | Subtle text |

---

## 2. Typography

### Font Families
| Font | Weights | Usage |
|------|---------|-------|
| **SF Pro Text** | 300, 400, 500, 600, 700, 800 | Primary UI font |
| **Chroma ST** | 300, 400, 500, 700, 900 | Display/headings |
| **CoFo Sans Mono** | 400, 500, 700, 900 | Numbers, monospace |

### Font URLs (woff2)
```
SF Pro Text:
  300: https://myballs.io/fonts/sf-pro-text-300.woff2
  400: https://myballs.io/fonts/sf-pro-text-400.woff2
  500: https://myballs.io/fonts/sf-pro-text-500.woff2
  600: https://myballs.io/fonts/sf-pro-text-600.woff2
  700: https://myballs.io/fonts/sf-pro-text-700.woff2
  800: https://myballs.io/fonts/sf-pro-text-800.woff2

Chroma ST:
  300: https://myballs.io/fonts/chroma-st-light.woff2
  400: https://myballs.io/fonts/chroma-st-regular.woff2
  500: https://myballs.io/fonts/chroma-st-medium.woff2
  700: https://myballs.io/fonts/chroma-st-bold.woff2
  900: https://myballs.io/fonts/chroma-st-black.woff2

CoFo Sans Mono:
  400: https://myballs.io/fonts/cofo-sans-mono-400.woff2
  500: https://myballs.io/fonts/cofo-sans-mono-500.woff2
  700: https://myballs.io/fonts/cofo-sans-mono-700.woff2
  900: https://myballs.io/fonts/cofo-sans-mono-900.woff2
```

### CSS Font Stack
```css
font-family: "SF Pro Text", "sans-serif";
```

### Base Typography
- Body font-size: `16px`
- Body line-height: `24px`
- Page titles: Large, bold, centered

---

## 3. Spacing & Layout

### CSS Variables
```css
:root {
  --top-safe: calc(var(--tg-safe-area-inset-top, 0px) + var(--tg-content-safe-area-inset-top, 0px));
  --bottom-safe: calc(var(--tg-safe-area-inset-bottom, 0px) + var(--tg-content-safe-area-inset-bottom, 0px));
  --app-navigation-height: 56px;
  --app-navigation-height-safe: calc(var(--app-navigation-height) + var(--bottom-safe));
  --game-controls-height: 161px;
  --container-max-width: 440px;
  --pvp-race-game-controls-height: 177px;
  --solo-trading-game-controls-height: 157px;
}
```

### Container
- Max width: `440px`
- Centered horizontally
- Content padding: ~`15px` horizontal

### Gift Card Grid
- 3 columns
- Gap: ~`8px`
- Card aspect-ratio: `1 / 1`

---

## 4. Border Radii
| Size | Value | Usage |
|------|-------|-------|
| Small | `8px` | Small badges, tags |
| Medium | `12px` | Buttons, inputs |
| Large | `16px` | Cards, containers (var(--radius-3xl)) |
| XL | `22px` | Large buttons |
| XXL | `24px` | Modal containers |
| Pill | `9999px` / `3.35544e+07px` | Round buttons, pills, nav items |
| Top sheet | `47px 47px 0 0` | Bottom sheets |

---

## 5. Backgrounds & Gradients

### Page Background
```css
background: linear-gradient(360deg, rgba(23,24,26,0) 0%, rgb(16,17,18) 100%),
            url("https://myballs.io/assets/bg1.svg");
background-color: #0C0C0C;
```

### Bottom Nav Fade
```css
background: radial-gradient(119.98% 100% at 50% 100%, rgb(0,0,0) 45%, rgba(0,0,0,0) 100%);
```

### Card Bottom Gradient (text readability over images)
```css
background: linear-gradient(rgba(12,12,12,0) 0%, rgba(12,12,12,0.78) 14.84%, rgb(12,12,12) 28.68%);
```

### Skeleton Loading
```css
background: linear-gradient(90deg, rgba(115,115,115,0.2), rgba(31,31,31,0.2) 50%, rgba(115,115,115,0.2)) 200% 0 / 200% 100%;
animation: skeleton-pulse 6s linear infinite;
```

### Farming Page Top Gradient
Purple gradient at top of Earn/Farming page.

### Profile Page Top Gradient
Cyan-to-dark gradient: `#34CDEF` transitioning to `#0C0C0C`.

---

## 6. Shadows & Effects

### Backdrop Blur
- Skeleton: `backdrop-filter: blur(17.5px)`
- Price tag: `backdrop-filter: blur(6px)`

### Button Press Effect
```css
.base-active-btn {
  transform-origin: 50% center;
  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
  will-change: transform;
}
```

### Pending Sheen Animation
```css
.pending-overlay {
  background-image:
    linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.5)),
    repeating-linear-gradient(120deg, rgba(255,255,255,0), rgba(255,255,255,0) 42%,
      rgba(255,255,255,0.1) 48%, rgba(255,255,255,0.16),
      rgba(255,255,255,0.1) 52%, rgba(255,255,255,0) 58%, rgba(255,255,255,0));
  animation: pendingGradientShift 1.8s linear infinite;
}
```

### Balance Button Glow Border
SVG radial gradient overlay with `mix-blend-mode: overlay`, `stroke-opacity: 0.6`.

---

## 7. Animations

### Gift Card Enter
```css
.gift-card-appear {
  --gift-card-enter-duration: .16s;
  animation: gift-card-in var(--gift-card-enter-duration) ease-out forwards;
}
@keyframes gift-card-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Gift Selection Scale
```css
.gift-enter-active, .gift-leave-active { transition: opacity 0.2s, transform 0.2s; }
.gift-enter-from, .gift-leave-to { opacity: 0; transform: scale(0.85); }
```

### Nav Slide
```css
.app-nav-slide-enter-active, .app-nav-slide-leave-active {
  transition: transform 0.22s, opacity 0.22s;
  will-change: transform, opacity;
}
.app-nav-slide-enter-from { opacity: 0; transform: translate3d(0, 100%, 0); }
```

### Modal Overlay
```css
.overlay { opacity: 0; transition: opacity 0.18s ease-out; }
.overlay--shown { opacity: 1; transition: opacity 0.25s ease-out; }
```

### Skeleton Pulse
```css
@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 8. Component Specifications

### Bottom Navigation
- Height: `56px` + safe area
- Background: `radial-gradient(119.98% 100% at 50% 100%, rgb(0,0,0) 45%, rgba(0,0,0,0) 100%)`
- Icon size: `18x18px`
- Icon style: `stroke-current`, no fill
- Label font-size: ~`10px`
- Inactive color: `#808080`
- Active color: `#FFFFFF`
- 5 items: Market, PvP, Solo, Earn, Profile

### Gift Card
- Aspect ratio: `1:1`
- Border radius: `var(--radius-3xl)` = `16px`
- Background: `rgba(255, 255, 255, 0.05)`
- Image fills the card
- Name: white, medium weight
- Serial: muted (#number)
- Price tag: cyan background (`#34CDEF`), white text, pill shape, `backdrop-filter: blur(6px)`
- Price tag height: `34px`
- Price tag border-radius: `2xl` (pill)

### Market Tabs
- Items: Gifts, Lootpacks, Upgrades, Real Items
- Active: white text, underline
- Inactive: muted text, no underline

### Filter Dropdowns
- Background: `rgba(255, 255, 255, 0.05)`
- Border radius: `16px`
- Chevron icon on right
- Text: `16px`

### Balance Pill (Header)
- Border radius: `16px`
- Background: dark with glow border SVG overlay
- TON icon + number + plus icon
- Padding: `0 6px 0 10px`

### PvP Game Room
- Status bar: Waiting badge (cyan bg), Prize Pool display
- Main arena: Large card with image, gradient border effect
- Players list: Dark card, player rows with avatar, username, percentage, bet amount
- Bet buttons: Row of pills (0.5, 1, 5, 10, 50, 100, 500), disabled state for insufficient balance
- Action buttons: Swap (dark), Deposit Gifts (cyan, large), Deposit (dark with plus icon)

### Farming/Earn
- Timer: 4 digit groups (DD:HH:MM:SS), pill containers for each digit
- Farming Pool: Big number with TON icon, Chroma ST font
- User card: Avatar, username, "Balance: X BP", rank display "Top N /total"
- CTA: Cyan full-width button "Farm more to win the prize"
- Module cards: Dark background, progress bars, level badges (LvL X)

### Profile
- "Play Balance" label: cyan color, small caps
- Balance: Large bold number with TON icon
- Action circles: 3 icon buttons (Top Up Stars, Top Up TON, Deposit Gifts) with labels
- User section: Circular avatar, username
- Inventory card: Dark card, 3-column mini-grid, "All Items" link
- Referral card: Dark card with green 3D illustration, "Invite Friends" white button
- Claim section: Claimable amount, invited users count, total claimed, Claim button

---

## 9. Asset CDN

### Gift Images
Pattern: `https://cdn.myballs.io/gifts/{giftname}/{giftname}-{id}.webp` (1500x1500 WebP)

### Background
- `https://myballs.io/assets/bg1.svg`

### Game Selector Cards
- `https://myballs.io/assets/pvp/selector/ice-card-bg.webp`
- `https://myballs.io/assets/pvp/selector/race-card-bg.webp`

### External
- Lottie/TGS Player: `https://unpkg.com/@lottiefiles/lottie-player@latest/dist/tgs-player.js`

---

## 10. SVG Icons

### Bottom Navigation Icons

All use `viewBox="0 0 18 18"`, `fill="none"`, `class="stroke-current"` for dynamic color.

#### Market (storefront)
```svg
<svg viewBox="0 0 18 18" fill="none"><path d="M2.25684 8.41602V11.7835C2.25684 15.151 3.60684 16.501 6.97434 16.501H11.0168C14.3843 16.501 15.7343 15.151 15.7343 11.7835V8.41602" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M8.99988 9C10.3724 9 11.3849 7.8825 11.2499 6.51L10.7549 1.5H7.25237L6.74987 6.51C6.61487 7.8825 7.62738 9 8.99988 9Z" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M13.7321 9C15.2471 9 16.3571 7.77 16.2071 6.2625L15.9971 4.2C15.7271 2.25 14.9771 1.5 13.0121 1.5H10.7246L11.2496 6.7575C11.3771 7.995 12.4946 9 13.7321 9Z" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M4.22979 9C5.46729 9 6.58479 7.995 6.70479 6.7575L6.86979 5.1L7.2298 1.5H4.94229C2.9773 1.5 2.22729 2.25 1.95729 4.2L1.75479 6.2625C1.60479 7.77 2.71479 9 4.22979 9Z" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M8.99951 12.75C7.74701 12.75 7.12451 13.3725 7.12451 14.625V16.5H10.8745V14.625C10.8745 13.3725 10.252 12.75 8.99951 12.75Z" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/></svg>
```

#### PvP (circles)
```svg
<svg viewBox="0 0 18 18" fill="none"><g clip-path="url(#pvp)"><circle cx="9" cy="9" r="7.534" stroke="currentColor" stroke-width="1.314"/><ellipse cx="6.074" cy="9" rx="2.244" ry="1.875" transform="rotate(90 6.074 9)" stroke="currentColor" stroke-width="1.314"/><ellipse cx="11.928" cy="9" rx="2.244" ry="1.875" transform="rotate(90 11.928 9)" stroke="currentColor" stroke-width="1.314"/></g><defs><clipPath id="pvp"><rect width="18" height="18" fill="currentColor"/></clipPath></defs></svg>
```

#### Solo (star)
```svg
<svg viewBox="0 0 18 18" fill="none"><path d="M10.0889 4.26367C10.3142 4.7512 10.894 4.96229 11.3799 4.7334L13.7314 3.62402L13.0498 6.13477C12.9089 6.65311 13.2169 7.1872 13.7363 7.32422L16.25 7.9873L14.1152 9.4707C13.6741 9.77707 13.5664 10.3844 13.876 10.8232L15.376 12.9482L12.7861 12.7119L12.6865 12.708C12.2264 12.713 11.8316 13.0438 11.7471 13.4961L11.7344 13.5947L11.5176 16.1865L9.68555 14.3398L9.61133 14.2734C9.23037 13.9607 8.66627 13.9823 8.31152 14.3398L6.47949 16.1865L6.26367 13.5947L6.25 13.4961C6.16542 13.0437 5.77069 12.7129 5.31055 12.708L5.21094 12.7119L2.62012 12.9482L4.12109 10.8232C4.43068 10.3844 4.3239 9.77712 3.88281 9.4707L1.74609 7.9873L4.26074 7.32422C4.7801 7.18722 5.08901 6.65305 4.94824 6.13477L4.26465 3.62402L6.61816 4.7334C7.10398 4.96198 7.68294 4.75102 7.9082 4.26367L8.99805 1.90137L10.0889 4.26367Z" stroke="currentColor" stroke-width="1.26"/></svg>
```

#### Earn (wand)
```svg
<svg viewBox="0 0 18 18" fill="none"><path d="M5.48227 6.86281L4.78477 7.02781C4.28227 7.14031 3.89227 7.5378 3.77227 8.0328L3.60727 8.73031C3.59227 8.80531 3.47977 8.80531 3.46477 8.73031L3.29977 8.0328C3.18727 7.5303 2.78977 7.14031 2.29477 7.02031L1.59727 6.85531C1.52227 6.84031 1.52227 6.72781 1.59727 6.71281L2.29477 6.54781C2.79727 6.43531 3.18727 6.03781 3.30727 5.54281L3.47227 4.84531C3.48727 4.77031 3.59977 4.77031 3.61477 4.84531L3.77977 5.54281C3.89227 6.04531 4.28977 6.43531 4.78477 6.55531L5.48227 6.72031C5.55727 6.73531 5.55727 6.84781 5.48227 6.86281Z" stroke="currentColor" stroke-width="1.125" stroke-miterlimit="10"/><path d="M13.0342 3.68309L14.0467 2.67059C14.5567 2.16059 15.3817 2.16059 15.8917 2.67059C16.4017 3.18059 16.4017 4.00559 15.8917 4.51559L14.8792 5.52809" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M10.1173 10.3953L4.42482 16.0878C3.88482 16.6278 3.01482 16.6278 2.47482 16.0878C1.93482 15.5478 1.93482 14.6778 2.47482 14.1378L8.16732 8.44531" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M12.2555 9.6971L15.653 13.0946C15.8705 13.3121 16.1855 13.3796 16.4705 13.2896C16.7555 13.1921 16.9655 12.9446 17.0105 12.6446C17.228 11.1446 16.718 9.6371 15.653 8.5721L14.5205 7.43957L15.098 6.86207C15.248 6.71207 15.3305 6.51707 15.3305 6.30707C15.3305 6.09707 15.248 5.89457 15.098 5.75207L12.818 3.47207C12.5105 3.16457 12.008 3.16457 11.7005 3.47207L11.123 4.04957L9.99045 2.91707C8.91795 1.84457 7.41049 1.34207 5.91799 1.55957C5.61799 1.60457 5.37049 1.81457 5.27299 2.09957C5.17549 2.38457 5.25049 2.70707 5.46799 2.91707L8.86545 6.31457L8.01045 7.16957C7.70295 7.47707 7.70295 7.9796 8.01045 8.2871L10.2905 10.5671C10.4405 10.7171 10.6355 10.7996 10.8455 10.7996C11.0555 10.7996 11.258 10.7171 11.4005 10.5671L12.2555 9.7121V9.6971Z" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/></svg>
```

#### Profile (person + sparkle)
```svg
<svg viewBox="0 0 18 18" fill="none"><path d="M14.8132 12.578L14.0032 12.7655C13.4257 12.9005 12.9682 13.3505 12.8332 13.928L12.6457 14.738C12.6307 14.8205 12.5032 14.8205 12.4807 14.738L12.2932 13.928C12.1582 13.3505 11.7082 12.893 11.1307 12.758L10.3207 12.5705C10.2382 12.5555 10.2382 12.428 10.3207 12.4055L11.1307 12.218C11.7082 12.083 12.1657 11.633 12.3007 11.0555L12.4882 10.2455C12.5032 10.163 12.6307 10.163 12.6532 10.2455L12.8407 11.0555C12.9757 11.633 13.4257 12.0905 14.0032 12.2255L14.8132 12.413C14.8957 12.428 14.8957 12.5555 14.8132 12.578Z" stroke="currentColor" stroke-width="1.125" stroke-miterlimit="10"/><path d="M8.99902 9C11.069 9 12.749 7.32 12.749 5.25C12.749 3.18 11.069 1.5 8.99902 1.5C6.92902 1.5 5.24902 3.18 5.24902 5.25C5.24902 7.32 6.92902 9 8.99902 9Z" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.00014 11.25C5.44512 11.25 2.55762 13.5975 2.55762 16.5" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/><path d="M15.4422 16.4998C15.4422 15.8173 15.2847 15.1723 14.9922 14.5723" stroke="currentColor" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/></svg>
```

### TON Diamond Icon
```svg
<svg viewBox="0 0 16 16" fill="none"><path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z" fill="currentColor"/></svg>
```

### Utility Icons
- Plus: `viewBox="0 0 14 14"`, two cross paths
- Sort: `viewBox="0 0 20 20"`, arrows up/down
- Chevron Down: `viewBox="0 0 16 16"`, dropdown arrow
