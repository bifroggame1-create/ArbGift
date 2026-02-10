<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-wrapper">
        <div class="overlay" @click="cancel" />
        <div class="sheet">
          <div class="header">
            <h2 class="title">Gift ID</h2>
            <button class="close-btn" @click="cancel" aria-label="Close">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>

          <div class="body">
            <div class="input-group">
              <input
                v-model.number="localId"
                type="number"
                class="input"
                placeholder="Enter Gift ID"
                min="0"
              />
            </div>
          </div>

          <div class="footer">
            <button class="btn btn-secondary" @click="cancel">Cancel</button>
            <button class="btn btn-primary" :disabled="!localId" @click="save">Save</button>
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
  giftId: number | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'apply': [id: number | null]
}>()

const localId = ref<number | null>(null)

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      localId.value = props.giftId
    }
  }
)

const cancel = () => {
  emit('update:visible', false)
}

const save = () => {
  emit('apply', localId.value)
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

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input:focus {
  border-color: #2681ff;
}

.input::-webkit-outer-spin-button,
.input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input[type='number'] {
  -moz-appearance: textfield;
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

.btn-primary:hover:not(:disabled) {
  background: #1f68d4;
}

.btn-primary:active:not(:disabled) {
  background: #1856b5;
}

.btn-primary:disabled {
  background: rgba(38, 129, 255, 0.3);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
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
