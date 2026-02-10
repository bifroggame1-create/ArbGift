<template>
  <div v-if="visible" class="sort-dropdown-overlay" @click="closeDropdown"></div>

  <Transition name="sort-dropdown-fade">
    <div v-if="visible" class="sort-dropdown-container">
      <div class="sort-dropdown">
        <div
          v-for="option in options"
          :key="option.value"
          class="sort-item"
          :class="{ active: current === option.value }"
          @click="selectOption(option.value)"
        >
          <div class="radio-circle" :class="{ active: current === option.value }"></div>
          <span class="item-label">{{ option.label }}</span>
          <div v-if="option.icon" class="item-icon">
            <span>{{ option.icon }}</span>
          </div>
          <svg v-if="current === option.value" class="checkmark-icon" viewBox="0 0 24 24" width="16" height="16">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="currentColor" />
          </svg>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
interface SortOption {
  value: string
  label: string
  icon?: string
}

defineProps<{
  visible: boolean
  options: SortOption[]
  current: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'select': [value: string]
}>()


const closeDropdown = () => {
  emit('update:visible', false)
}

const selectOption = (value: string) => {
  emit('select', value)
  emit('update:visible', false)
}
</script>

<style scoped>
.sort-dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: transparent;
  z-index: 200;
  cursor: pointer;
}

.sort-dropdown-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 201;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 16px;
  pointer-events: none;
}

.sort-dropdown {
  background-color: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  min-width: 240px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  pointer-events: auto;
  overflow: hidden;
  margin-top: 8px;
  margin-right: 0;
}

.sort-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.sort-item:last-child {
  border-bottom: none;
}

.sort-item:hover:not(.active) {
  background-color: rgba(255, 255, 255, 0.04);
}

.sort-item.active {
  background-color: rgba(38, 129, 255, 0.1);
}

.radio-circle {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.radio-circle.active {
  border-color: #2681ff;
  background-color: #2681ff;
  box-shadow: 0 0 8px rgba(38, 129, 255, 0.4);
}

.item-label {
  flex: 1;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.sort-item.active .item-label {
  color: #2681ff;
}

.item-icon {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  flex-shrink: 0;
}

.sort-item.active .item-icon {
  color: #2681ff;
}

.checkmark-icon {
  color: #2681ff;
  flex-shrink: 0;
  margin-left: auto;
}

.sort-dropdown-fade-enter-active,
.sort-dropdown-fade-leave-active {
  transition: opacity 0.2s ease;
}

.sort-dropdown-fade-enter-from,
.sort-dropdown-fade-leave-to {
  opacity: 0;
}

.sort-dropdown-container {
  transition: opacity 0.2s ease;
}
</style>
