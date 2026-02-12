<template>
  <div class="fairness-section" v-if="gameNumber > 0">
    <button class="fairness-toggle" @click="expanded = !expanded">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
      <span>Provably Fair</span>
      <span class="game-num">#{{ gameNumber }}</span>
      <svg
        class="chevron"
        :class="{ open: expanded }"
        width="12" height="12" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2"
      >
        <path d="M6 9l6 6 6-6"/>
      </svg>
    </button>

    <Transition name="fairness-expand">
      <div v-if="expanded" class="fairness-details">
        <div class="fair-row">
          <span class="fair-label">Игра</span>
          <span class="fair-value">#{{ gameNumber }}</span>
        </div>
        <div class="fair-row">
          <span class="fair-label">Хеш сервера</span>
          <span class="fair-value hash" @click="copy(serverSeedHash)">
            {{ truncHash(serverSeedHash) }}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="9" y="9" width="13" height="13" rx="2"/>
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
            </svg>
          </span>
        </div>
        <div class="fair-row">
          <span class="fair-label">Клиент сид</span>
          <span class="fair-value hash" @click="copy(clientSeed)">
            {{ truncHash(clientSeed) }}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="9" y="9" width="13" height="13" rx="2"/>
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
            </svg>
          </span>
        </div>
        <div class="fair-row">
          <span class="fair-label">Nonce</span>
          <span class="fair-value">{{ nonce }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  gameNumber: number
  serverSeedHash: string
  clientSeed: string
  nonce: number
}>()

const expanded = ref(false)

function truncHash(h: string): string {
  if (!h || h.length < 16) return h
  return h.slice(0, 8) + '...' + h.slice(-8)
}

function copy(text: string) {
  navigator.clipboard?.writeText(text)
}
</script>

<style scoped>
.fairness-section {
  padding: 0 16px;
}

.fairness-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 8px 0;
  background: none;
  border: none;
  color: var(--plinko-text-tertiary, rgba(253,253,253,0.25));
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: color 0.15s;
}
.fairness-toggle:active {
  color: var(--plinko-text-secondary, rgba(253,253,253,0.5));
}

.game-num {
  color: var(--plinko-text-secondary, rgba(253,253,253,0.5));
  font-family: 'CoFo Sans Mono', monospace;
  margin-left: auto;
  margin-right: 4px;
}

.chevron {
  transition: transform 0.2s;
}
.chevron.open {
  transform: rotate(180deg);
}

.fairness-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 6px 0 10px;
  border-top: 1px solid var(--plinko-card-border, rgba(62,30,84,0.4));
}

.fair-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fair-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--plinko-text-tertiary, rgba(253,253,253,0.25));
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.fair-value {
  font-family: 'CoFo Sans Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  color: var(--plinko-text-secondary, rgba(253,253,253,0.5));
}

.fair-value.hash {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: color 0.15s;
}
.fair-value.hash:active {
  color: var(--plinko-white, #FDFDFD);
}

/* Expand transition */
.fairness-expand-enter-active {
  transition: all 0.2s ease-out;
  overflow: hidden;
}
.fairness-expand-leave-active {
  transition: all 0.15s ease-in;
  overflow: hidden;
}
.fairness-expand-enter-from,
.fairness-expand-leave-to {
  opacity: 0;
  max-height: 0;
}
.fairness-expand-enter-to,
.fairness-expand-leave-from {
  opacity: 1;
  max-height: 200px;
}
</style>
