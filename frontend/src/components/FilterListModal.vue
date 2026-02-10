<template>
  <Teleport to="body">
    <Transition name="overlay-fade">
      <div v-if="visible" class="filter-modal-overlay" @click="closeModal"></div>
    </Transition>

    <Transition name="sheet-slide">
      <div v-if="visible" class="filter-modal-sheet">
        <!-- Header -->
        <div class="filter-modal-header">
          <h2 class="filter-modal-title">{{ title }}</h2>
          <button class="filter-modal-close-btn" @click="closeModal" aria-label="Close">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
        </div>

        <!-- Search Input -->
        <div class="filter-modal-search">
          <svg class="filter-modal-search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 12C9.76142 12 12 9.76142 12 7C12 4.23858 9.76142 2 7 2C4.23858 2 2 4.23858 2 7C2 9.76142 4.23858 12 7 12Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M14 14L10.5 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            class="filter-modal-search-input"
            placeholder="Enter a keyword to search"
            autocomplete="off"
          />
        </div>

        <!-- Counter Row -->
        <div class="filter-modal-counter-row">
          <span class="filter-modal-counter-text">Selected: {{ localSelected.length }}</span>
          <button
            class="filter-modal-toggle-btn"
            @click="toggleSelectAll"
          >
            {{ localSelected.length === filteredOptions.length && filteredOptions.length > 0 ? "Clear All" : "Select All" }}
          </button>
        </div>

        <!-- Options List -->
        <div class="filter-modal-list">
          <div
            v-for="option in filteredOptions"
            :key="option.value"
            class="filter-modal-item"
            @click="toggleOption(option.value)"
          >
            <!-- Thumbnail -->
            <div v-if="showThumbnails && option.imageUrl" class="filter-modal-thumbnail">
              <img :src="option.imageUrl" :alt="option.label" />
            </div>
            <div v-else-if="showThumbnails" class="filter-modal-thumbnail-fallback"></div>

            <!-- Text Block -->
            <div class="filter-modal-text-block">
              <div class="filter-modal-label">
                {{ option.label }}
                <span class="filter-modal-count">({{ option.count || 0 }})</span>
                <span v-if="showRarity && option.rarity" class="filter-modal-rarity">({{ option.rarity }})</span>
              </div>
              <div v-if="option.floorPrice !== undefined" class="filter-modal-price">
                ~{{ option.floorPrice.toFixed(2) }} TON floor
              </div>
            </div>

            <!-- Checkbox -->
            <div
              class="filter-modal-checkbox"
              :class="{ 'filter-modal-checkbox--checked': localSelected.includes(option.value) }"
            >
              <svg v-if="localSelected.includes(option.value)" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13.3333 4L6 11.3333L2.66667 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="filter-modal-footer">
          <button class="filter-modal-btn filter-modal-btn--secondary" @click="closeModal">Close</button>
          <button
            class="filter-modal-btn filter-modal-btn--primary"
            :disabled="localSelected.length === props.selected.length && localSelected.every(v => props.selected.includes(v))"
            @click="applyFilters"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";

interface FilterOption {
  value: string;
  label: string;
  count?: number;
  floorPrice?: number;
  rarity?: string;
  imageUrl?: string;
}

const props = defineProps<{
  visible: boolean;
  title: string;
  options: FilterOption[];
  selected: string[];
  showThumbnails?: boolean;
  showRarity?: boolean;
}>();

const emit = defineEmits<{
  "update:visible": [value: boolean];
  apply: [selected: string[]];
}>();

const localSelected = ref<string[]>([]);
const searchQuery = ref("");

const filteredOptions = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return props.options.filter((option) =>
    option.label.toLowerCase().includes(query)
  );
});

watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      localSelected.value = [...props.selected];
      searchQuery.value = "";
    }
  }
);

const toggleOption = (value: string) => {
  const index = localSelected.value.indexOf(value);
  if (index > -1) {
    localSelected.value.splice(index, 1);
  } else {
    localSelected.value.push(value);
  }
};

const toggleSelectAll = () => {
  if (
    localSelected.value.length === filteredOptions.value.length &&
    filteredOptions.value.length > 0
  ) {
    localSelected.value = [];
  } else {
    localSelected.value = filteredOptions.value.map((opt) => opt.value);
  }
};

const applyFilters = () => {
  emit("apply", localSelected.value);
  closeModal();
};

const closeModal = () => {
  emit("update:visible", false);
};
</script>

<style scoped>
.filter-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 999;
}

.filter-modal-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #1a1a1a;
  border-radius: 20px 20px 0 0;
  max-height: 75vh;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.2);
}

.filter-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.filter-modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: -0.3px;
}

.filter-modal-close-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.filter-modal-close-btn:hover {
  color: #ffffff;
}

.filter-modal-search {
  position: relative;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.filter-modal-search-icon {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
}

.filter-modal-search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  background-color: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.filter-modal-search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.filter-modal-search-input:focus {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.filter-modal-counter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.filter-modal-counter-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.filter-modal-toggle-btn {
  background: none;
  border: none;
  padding: 4px 0;
  cursor: pointer;
  color: #2681ff;
  font-size: 13px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.filter-modal-toggle-btn:hover {
  color: #1a6fbf;
}

.filter-modal-list {
  flex: 1;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.filter-modal-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.filter-modal-item:hover {
  background-color: rgba(255, 255, 255, 0.04);
}

.filter-modal-thumbnail {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.06);
}

.filter-modal-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.filter-modal-thumbnail-fallback {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background-color: #2681ff;
}

.filter-modal-text-block {
  flex: 1;
  min-width: 0;
}

.filter-modal-label {
  font-size: 14px;
  color: #ffffff;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.filter-modal-count {
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.filter-modal-rarity {
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.filter-modal-price {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 2px;
}

.filter-modal-checkbox {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  transition: all 0.2s ease;
  color: transparent;
}

.filter-modal-checkbox--checked {
  background-color: #2681ff;
  border-color: #2681ff;
  color: #ffffff;
}

.filter-modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background-color: #1a1a1a;
}

.filter-modal-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.filter-modal-btn--secondary {
  background-color: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.6);
}

.filter-modal-btn--secondary:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.filter-modal-btn--primary {
  background-color: #2681ff;
  color: #ffffff;
}

.filter-modal-btn--primary:hover:not(:disabled) {
  background-color: #1a6fbf;
}

.filter-modal-btn--primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Transitions */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.3s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

.sheet-slide-enter-active,
.sheet-slide-leave-active {
  transition: transform 0.3s ease;
}

.sheet-slide-enter-from,
.sheet-slide-leave-to {
  transform: translateY(100%);
}
</style>
