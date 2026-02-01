# MyBalls.io Trading - Game Logic Specification

## Overview

Trading - это волатильная торговая игра, где цена может двигаться как ВВЕРХ, так и ВНИЗ (в отличие от Aviator, где только вверх). Игра заканчивается крашем только при достижении цены 0.000x (ликвидация).

---

## Ключевые отличия от Aviator

| Параметр | Aviator | Trading (MyBalls) |
|----------|---------|-------------------|
| Движение цены | Только вверх | Вверх И вниз |
| Краш | При достижении target multiplier | Только при 0.000x |
| Свечи | Всегда зелёные | Зелёные и красные |
| Можно быть в минусе | Нет | Да (цена < 1.0x) |
| Стратегия | Вовремя вывести | Можно пересидеть просадку |

---

## Модель цены

### Волатильная случайная прогулка с дрифтом

```typescript
interface PriceModel {
  volatility: number      // базовая волатильность (0.02-0.04)
  drift: number           // отрицательный дрифт для house edge (-0.001)
  momentum: number        // текущий импульс (создаёт тренды)
  momentumDecay: number   // затухание импульса (0.90-0.95)
}

const updatePrice = (current: number, model: PriceModel): number => {
  // Случайное изменение
  const random = (Math.random() - 0.5) * 2 * model.volatility

  // Эффект импульса (создаёт серии в одном направлении)
  const momentumEffect = model.momentum * 0.3

  // Суммарное изменение
  const change = random + model.drift + momentumEffect

  // Обновляем импульс
  model.momentum = model.momentum * model.momentumDecay + (Math.random() - 0.5) * 0.02

  // Новая цена (минимум 0)
  return Math.max(0, current + change)
}
```

### Параметры по умолчанию

```typescript
const DEFAULT_MODEL: PriceModel = {
  volatility: 0.025,     // ~2.5% за тик
  drift: -0.0008,        // небольшой негативный дрифт
  momentum: 0,           // начинаем без импульса
  momentumDecay: 0.92    // импульс затухает на 8% за тик
}
```

### Увеличение вероятности падения со временем

```typescript
// House edge: чем дольше игра, тем вероятнее падение
const getDownProbability = (elapsedSeconds: number): number => {
  const baseProb = 0.50           // 50% базовая
  const timeIncrease = 0.002      // +0.2% в секунду
  return Math.min(0.75, baseProb + elapsedSeconds * timeIncrease)
}

// Альтернативный подход: увеличиваем drift со временем
const getDynamicDrift = (elapsedSeconds: number): number => {
  const baseDrift = -0.0005
  const timeMultiplier = 1 + elapsedSeconds * 0.01
  return baseDrift * timeMultiplier
}
```

---

## Структура свечи (OHLC)

```typescript
interface Candle {
  open: number       // цена открытия
  high: number       // максимум за период
  low: number        // минимум за период
  close: number      // цена закрытия
  timestamp: number  // время начала свечи
  isBullish: boolean // close >= open
}
```

### Создание свечей

```typescript
const TICK_INTERVAL = 100       // мс между тиками
const TICKS_PER_CANDLE = 15     // ~1.5 секунды на свечу

let currentCandle: Candle | null = null
let tickCount = 0

const onTick = (newPrice: number) => {
  tickCount++

  if (!currentCandle) {
    // Начинаем новую свечу
    currentCandle = {
      open: newPrice,
      high: newPrice,
      low: newPrice,
      close: newPrice,
      timestamp: Date.now(),
      isBullish: true
    }
  } else {
    // Обновляем текущую свечу
    currentCandle.close = newPrice
    currentCandle.high = Math.max(currentCandle.high, newPrice)
    currentCandle.low = Math.min(currentCandle.low, newPrice)
    currentCandle.isBullish = currentCandle.close >= currentCandle.open
  }

  // Завершаем свечу
  if (tickCount >= TICKS_PER_CANDLE) {
    finalizeCandle(currentCandle)
    currentCandle = null
    tickCount = 0
  }
}
```

---

## Состояния игры

```typescript
type GameState =
  | 'countdown'    // Обратный отсчёт перед началом (3-5 сек)
  | 'active'       // Игра идёт, цена движется
  | 'crashed'      // Краш на 0.000x
  | 'waiting'      // Ожидание следующего раунда

interface GameSession {
  state: GameState
  gameId: number
  hash: string           // для provably fair
  startTime: number
  currentPrice: number
  maxPrice: number       // максимум за раунд
  candles: Candle[]
  traders: Trader[]
}
```

### Переходы состояний

```
[waiting] ---(countdown starts)---> [countdown]
[countdown] ---(3-5 sec)---> [active]
[active] ---(price <= 0.001)---> [crashed]
[crashed] ---(3 sec delay)---> [waiting]
```

---

## Механика ставок

### Структура ставки

```typescript
interface PlayerBet {
  oderId: string
  amount: number         // сумма ставки в TON
  entryPrice: number     // цена при входе (обычно 1.000x)
  exitPrice?: number     // цена при выходе (если вышел)
  profit?: number        // прибыль/убыток
  status: 'active' | 'exited' | 'liquidated'
}
```

### Расчёт P/L

```typescript
// Текущий P/L (пока в позиции)
const getCurrentPL = (bet: PlayerBet, currentPrice: number): number => {
  return bet.amount * currentPrice - bet.amount
}

// Процентный P/L
const getCurrentPLPercent = (bet: PlayerBet, currentPrice: number): number => {
  return (currentPrice - 1) * 100  // -50% если цена 0.5x
}

// Финальный P/L при выходе
const getFinalPL = (bet: PlayerBet): number => {
  if (!bet.exitPrice) return 0
  return bet.amount * bet.exitPrice - bet.amount
}
```

### Примеры

| Ставка | Цена входа | Текущая цена | P/L | P/L % |
|--------|------------|--------------|-----|-------|
| 1 TON | 1.000x | 1.500x | +0.5 TON | +50% |
| 1 TON | 1.000x | 0.800x | -0.2 TON | -20% |
| 1 TON | 1.000x | 2.000x | +1.0 TON | +100% |
| 1 TON | 1.000x | 0.000x | -1.0 TON | -100% (ликвидация) |

---

## Условие краша

```typescript
const CRASH_THRESHOLD = 0.001  // 0.001x = считаем как 0

const checkCrash = (price: number): boolean => {
  return price <= CRASH_THRESHOLD
}

const onCrash = (session: GameSession) => {
  session.state = 'crashed'

  // Ликвидируем всех активных трейдеров
  session.traders.forEach(trader => {
    if (trader.bet.status === 'active') {
      trader.bet.status = 'liquidated'
      trader.bet.exitPrice = 0
      trader.bet.profit = -trader.bet.amount  // полная потеря
    }
  })

  // Показываем результат 3 секунды
  setTimeout(() => {
    startNewRound()
  }, 3000)
}
```

---

## Y-Ось графика

### Динамический диапазон

```typescript
const getYAxisRange = (candles: Candle[], currentPrice: number): [number, number] => {
  const allPrices = candles.flatMap(c => [c.high, c.low])
  allPrices.push(currentPrice)

  const min = Math.min(...allPrices)
  const max = Math.max(...allPrices)

  // Добавляем padding 10%
  const padding = (max - min) * 0.1

  return [
    Math.max(0, min - padding),
    max + padding
  ]
}

// Фиксированные метки
const Y_AXIS_LABELS = [0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00]
// Динамически добавляем больше если цена выше 2.0x
```

---

## Traders Panel

### Структура трейдера

```typescript
interface Trader {
  id: string
  username: string
  avatar: string
  bet: PlayerBet
  rank?: number           // для лидерборда
  totalProfit?: number    // за турнир
}
```

### Отображение статуса

```typescript
const getTraderStatus = (trader: Trader): string => {
  switch (trader.bet.status) {
    case 'active':
      return 'В игре'
    case 'exited':
      return `Вышел +${trader.bet.profit?.toFixed(2)} TON`
    case 'liquidated':
      return 'Ликвидирован'
  }
}
```

---

## События WebSocket (для будущей интеграции)

```typescript
// Клиент -> Сервер
interface ClientEvents {
  'join_game': { gameId: number }
  'place_bet': { amount: number }
  'cash_out': {}
}

// Сервер -> Клиент
interface ServerEvents {
  'game_state': GameSession
  'price_update': { price: number, candle?: Candle }
  'trader_joined': Trader
  'trader_exited': { oderId: string, exitPrice: number, profit: number }
  'game_crashed': { finalPrice: number, maxPrice: number }
  'new_round': { gameId: number, hash: string, countdown: number }
}
```

---

## Provably Fair

```typescript
// Генерация hash для раунда
const generateGameHash = (serverSeed: string, gameId: number): string => {
  return sha256(`${serverSeed}:${gameId}`)
}

// Верификация результата
const verifyResult = (
  serverSeed: string,
  clientSeed: string,
  nonce: number
): number => {
  const combined = `${serverSeed}:${clientSeed}:${nonce}`
  const hash = sha256(combined)
  // Конвертируем hash в crash point
  return hashToCrashPoint(hash)
}
```

---

## Демо режим (офлайн)

```typescript
const startDemoGame = () => {
  const model: PriceModel = { ...DEFAULT_MODEL }
  let price = 1.0
  let elapsedSeconds = 0

  const interval = setInterval(() => {
    // Увеличиваем вероятность падения со временем
    model.drift = getDynamicDrift(elapsedSeconds)

    // Обновляем цену
    price = updatePrice(price, model)
    elapsedSeconds += TICK_INTERVAL / 1000

    // Проверяем краш
    if (price <= CRASH_THRESHOLD) {
      clearInterval(interval)
      onCrash()
    }

    // Emit price update
    emit('price_update', price)
  }, TICK_INTERVAL)
}
```

---

## Ключевые метрики

| Параметр | Значение |
|----------|----------|
| Tick interval | 100ms |
| Ticks per candle | 15 (1.5 сек) |
| Base volatility | 2.5% |
| Base drift | -0.08% |
| Momentum decay | 8% per tick |
| Crash threshold | 0.001x |
| Post-crash delay | 3 seconds |
| Countdown duration | 3-5 seconds |
| Average game duration | 30-120 seconds |
| House edge | ~2-5% (via drift) |
