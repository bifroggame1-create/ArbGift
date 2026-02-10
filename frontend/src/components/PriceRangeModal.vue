<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-wrapper">
        <div class="overlay" @click="close" />
        <div class="sheet">
          <div class="header">
            <h2 class="title">Price Range</h2>
            <button class="close-btn" @click="close" aria-label="Close">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>

          <div class="body">
            <div class="inputs-grid">
              <div class="input-group">
                <div class="input-wrapper">
                  <svg class="icon" width="12" height="12" viewBox="0 0 16 16" fill="none">
                    <path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z" fill="currentColor" />
                  </svg>
                  <input
                    v-model.number="localMin"
                    type="number"
                    class="input"
                    placeholder="0.00"
                    min="0"
                    step="0.01"
                  />
                </div>
                <label class="label">Min</label>
              </div>

              <div class="input-group">
                <div class="input-wrapper">
                  <svg class="icon" width="12" height="12" viewBox="0 0 16 16" fill="none">
                    <path d="M12.7238 1.00488H3.27565C1.53846 1.00488 0.437395 2.87874 1.31137 4.39358L7.14243 14.5002C7.52294 15.1601 8.47652 15.1601 8.85703 14.5002L14.6893 4.39358C15.5621 2.88116 14.461 1.00488 12.725 1.00488H12.7238ZM7.13769 11.4694L5.86778 9.01168L2.80363 3.53153C2.60149 3.18078 2.85116 2.7313 3.27446 2.7313H7.1365V11.4705L7.13769 11.4694ZM13.1935 3.53035L10.1305 9.01287L8.86059 11.4694V2.73011H12.7226C13.1459 2.73011 13.3956 3.17959 13.1935 3.53035Z" fill="currentColor" />
                  </svg>
                  <input
                    v-model.number="localMax"
                    type="number"
                    class="input"
                    placeholder="100 000.00"
                    min="0"
                    step="0.01"
                  />
                </div>
                <label class="label">Max</label>
              </div>
            </div>
          </div>

          <div class="footer">
            <button class="btn btn-secondary" @click="close">Close</button>
            <button class="btn btn-primary" @click="apply">Apply Filters</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  minPrice: number | null
  maxPrice: number | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'apply': [min: number | null, max: number | null]
}>()

const localMin = ref<number | null>(null)
const localMax = ref<number | null>(null)

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      localMin.value = props.minPrice
      localMax.value = props.maxPrice
    }
  }
)

const close = () => {
  emit('update:visible', false)
}

const apply = () => {
  emit('apply', localMin.value, localMax.value)
  emit('update:visible', false)
}
</script>

<style scoped>
.modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: flex-end;
  z-index: 1000;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  cursor: pointer;
}

.sheet {
  position: relative;
  background: #1a1a1a;
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.4);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #fff;
}

.body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.inputs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: #2681ff;
}

.icon {
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.input {
  flex: 1;
  background: none;
  border: none;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input::-webkit-outer-spin-button,
.input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input[type='number'] {
  -moz-appearance: textfield;
}

.label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.6);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.btn-primary {
  background: #2681ff;
  color: #fff;
}

.btn-primary:hover {
  background: #1f68d4;
}

.btn-primary:active {
  background: #1856b5;
}

/* Transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from .overlay {
  opacity: 0;
}

.modal-enter-from .sheet {
  transform: translateY(100%);
}

.modal-leave-to .overlay {
  opacity: 0;
}

.modal-leave-to .sheet {
  transform: translateY(100%);
}
</style>
