<template>
  <Teleport to="body">
    <div v-if="open" class="overlay" @click.self="$emit('close')">
      <div class="sheet">
        <div class="handle"></div>
        <header class="sheet__header">
          <div>
            <p class="eyebrow">Ставка подарком</p>
            <h3>Выберите гифт для ставки</h3>
          </div>
          <button class="icon-btn" @click="$emit('close')">×</button>
        </header>

        <div class="hash-row" v-if="serverSeedHash">
          <span class="hash-label">hash</span>
          <code class="hash">{{ serverSeedHash }}</code>
          <button class="icon-btn" @click="copy(serverSeedHash)">⧉</button>
        </div>

        <div class="search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="7" /><path d="m16.5 16.5 3.5 3.5" />
          </svg>
          <input v-model="query" placeholder="Поиск по названию или slug" />
        </div>

        <div v-if="loading" class="state muted">Загрузка инвентаря…</div>
        <div v-else-if="filtered.length === 0" class="state muted">Нет доступных гифтов</div>

        <div class="grid">
          <button
            v-for="item in filtered"
            :key="item.id"
            :class="['card', { active: selected?.id === item.id, locked: item.is_locked }]"
            @click="select(item)"
            :disabled="item.is_locked || !item.is_available_for_betting"
          >
            <div class="card__img">
              <img :src="item.gift.image_url || fallback" :alt="item.gift.name" loading="lazy" />
            </div>
            <div class="card__body">
              <div class="card__title">{{ item.gift.name }}</div>
              <div class="card__meta">
                <span class="pill">{{ item.gift.rarity || 'gift' }}</span>
                <span class="price">
                  <img src="/icons/ton.svg" alt="TON" width="12" height="12" />
                  {{ item.current_floor_price_ton?.toFixed?.(2) ?? item.current_floor_price_ton }}
                </span>
              </div>
              <div v-if="item.is_locked" class="lock">🔒 {{ item.locked_reason }}</div>
            </div>
          </button>
        </div>

        <footer class="sheet__footer">
          <button class="ghost" @click="$emit('close')">Отмена</button>
          <button class="primary" :disabled="!selected" @click="confirm">Поставить</button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, type PropType } from 'vue'
import type { InventoryItem } from '@/api/client'

const props = defineProps({
  open: { type: Boolean, default: false },
  items: { type: Array as PropType<InventoryItem[]>, default: () => [] },
  loading: { type: Boolean, default: false },
  serverSeedHash: { type: String, default: '' },
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', payload: InventoryItem): void
}>()

const fallback = '/gifts/default.webp'
const query = ref('')
const selected = ref<InventoryItem | null>(null)

watch(() => props.open, (isOpen) => {
  if (!isOpen) {
    query.value = ''
    selected.value = null
  }
})

const filtered = computed(() => {
  const q = query.value.toLowerCase().trim()
  return props.items.filter((item) => {
    const name = item.gift.name?.toLowerCase() || ''
    const slug = item.telegram_slug?.toLowerCase() || ''
    return q === '' || name.includes(q) || slug.includes(q)
  })
})

function select(item: InventoryItem) {
  selected.value = item
}

function confirm() {
  if (selected.value) emit('confirm', selected.value)
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    /* ignore */
  }
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding: 12px;
}
.sheet {
  width: min(480px, 100%);
  max-height: 90vh;
  background: #0f1116;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px;
  padding: 12px 12px 16px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.45);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.handle {
  width: 48px;
  height: 4px;
  border-radius: 999px;
  background: rgba(255,255,255,0.15);
  margin: 0 auto;
}
.sheet__header, .sheet__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.sheet__footer {
  margin-top: auto;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  margin: 0;
}
h3 {
  margin: 2px 0 0;
  font-size: 18px;
}
.icon-btn {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  width: 32px;
  height: 32px;
  border-radius: 10px;
  color: #fff;
}
.search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
}
.search input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  outline: none;
  font-size: 14px;
}
.state {
  padding: 12px;
  border-radius: 12px;
  text-align: center;
}
.muted { color: rgba(255,255,255,0.6); }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
  overflow-y: auto;
  max-height: 50vh;
  padding-right: 4px;
}
.card {
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  border-radius: 14px;
  padding: 8px;
  text-align: left;
  color: #fff;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.card.locked {
  opacity: 0.5;
  cursor: not-allowed;
}
.card.active {
  border-color: #5ce1e6;
  box-shadow: 0 0 0 1px #5ce1e6;
}
.card__img {
  border-radius: 10px;
  overflow: hidden;
  aspect-ratio: 1;
  background: #141820;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card__img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card__title {
  font-weight: 600;
  font-size: 14px;
}
.card__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: rgba(255,255,255,0.8);
}
.pill {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  text-transform: capitalize;
}
.price {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.lock {
  font-size: 12px;
  color: #ffa94d;
}
.sheet__footer button {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.1);
  font-weight: 600;
}
.sheet__footer .primary {
  background: linear-gradient(90deg, #2dd4bf, #6366f1);
  border: none;
  color: #0b0d12;
}
.sheet__footer .ghost {
  background: rgba(255,255,255,0.04);
  color: #fff;
}
.hash-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255,255,255,0.04);
  border: 1px dashed rgba(255,255,255,0.08);
}
.hash-label {
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.6);
}
.hash {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
}
</style>
