# MyBalls.io Trading Style Guide

## Colors

### Backgrounds
- Page background: `#000000`
- Card/Container: `#0E0F14` or `#111111`
- Card border: `#191919` or `#222222`
- Button background: `#1C1C1E`
- Button border: `#333333`

### Accent Colors
- TON Blue: `#0098EA`
- Green (positive/buy): `#09D76D`
- Red (negative/sell): `#FB2C36`
- Cyan (trader badge): `#34CDEF`
- Gold (level badge): `#FFD700` to `#FFA500`

### Text
- Primary: `#FFFFFF`
- Secondary: `rgba(255, 255, 255, 0.5)`
- Tertiary: `rgba(255, 255, 255, 0.4)`

## Typography
- Font family: `-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif`
- Monospace (numbers): `ui-monospace, SFMono-Regular, monospace`

### Font Sizes
- Multiplier: `20-24px` (bold 700)
- Button label: `16px` (bold 700)
- Body text: `14px` (medium 500)
- Small text: `12px`
- Tiny text: `11px`
- Nav labels: `10-11px`

## Spacing (padding/margin)
- Page padding: `12px`
- Card padding: `14-16px`
- Gap between sections: `12px`
- Button padding: `10px 14px`
- Large button padding: `16px 24px`

## Border Radius
- Large containers (chart): `24px` (rounded-3xl)
- Cards/panels: `20px` (rounded-2xl)
- Buttons: `14-16px` (rounded-xl)
- Pills: `14px`
- Small elements: `8px`

## Shadows
- Minimal shadows, mostly flat design
- Text shadow on multiplier: `0 2px 8px rgba(0,0,0,0.8)`

## Component Specifications

### Tournament Banner
- Background: `linear-gradient(135deg, #0098EA 0%, #0066CC 100%)`
- Border radius: `20px`
- Padding: `12px 20px`
- Full width

### Top Bar Icon Buttons
- Size: `44px x 44px`
- Background: `#1C1C1E`
- Border radius: `14px`
- Icon color: `rgba(255,255,255,0.5)`
- Icon size: `20px`

### Balance Pill
- Background: `#1C1C1E`
- Border radius: `20px`
- Padding: `10px 14px`
- Plus button: `22px` circle, background `#333`

### Chart Container
- Background: `#0E0F14`
- Border: `1px solid #191919`
- Border radius: `24px`
- Aspect ratio: `1:1` (square)

### Y-Axis
- Values: 7, 6, 5, 4, 3, 2, 1 (integers!)
- Font size: `11px`
- Color: `rgba(255,255,255,0.4)`
- Width: `~30px`

### Grid Lines
- Horizontal only
- Color: `rgba(255,255,255,0.06)`
- Style: solid (not dashed)

### Price Line (current)
- Style: dashed
- Color: `rgba(255,255,255,0.5)`

### Multiplier Display
- Font size: `20-24px`
- Font weight: `700`
- Font family: monospace
- Position: right side of chart, vertically aligned with price

### Traders Panel
- Background: `rgba(255,255,255,0.05)` with backdrop blur
- Border: `1px solid rgba(255,255,255,0.1)`
- Border radius: `20px`

### Bet Pills
- Background: `#1C1C1E`
- Border: `1px solid #333`
- Border radius: `14px`
- Active state: background `#0098EA`, border `#0098EA`
- TON icon before number

### Buy Button
- Background: `#09D76D`
- Border radius: `18px`
- Height: ~56px
- Text color: `#000000` (dark)
- Two lines: "Buy" (16px bold) + "0.5 TON" (12px)

### Swap/Deposit Buttons
- Background: `#1C1C1E`
- Border radius: `16px`
- Vertical layout (icon + text)
- Width: ~60px

### Bottom Navigation
- Background: page background
- Border top: `1px solid #262729`
- 5 items evenly spaced
- Icon: `20px`
- Label: `10-11px`
- Active color: `#0098EA` or white
- Inactive: `rgba(255,255,255,0.5)`
