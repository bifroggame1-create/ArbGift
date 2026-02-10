<template>
  <div v-if="tags.length > 0" class="filter-tags-container">
    <div class="tags-scroll">
      <button class="clear-all-btn" @click="handleClearAll">
        Clear All
      </button>

      <div
        v-for="tag in tags"
        :key="`${tag.key}-${tag.label}`"
        class="filter-tag"
      >
        <img
          v-if="tag.imageUrl"
          :src="tag.imageUrl"
          :alt="tag.label"
          class="tag-thumbnail"
        />
        <span class="tag-label">{{ tag.label }}</span>
        <button
          class="tag-remove-btn"
          @click="handleRemove(tag.key, tag.label)"
          :aria-label="`Remove ${tag.label} filter`"
        >
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface FilterTag {
  key: string
  label: string
  imageUrl?: string
}

defineProps<{
  tags: FilterTag[]
}>()

const emit = defineEmits<{
  'remove': [key: string, label: string]
  'clear-all': []
}>()

const handleRemove = (key: string, label: string) => {
  emit('remove', key, label)
}

const handleClearAll = () => {
  emit('clear-all')
}
</script>

<style scoped>
.filter-tags-container {
  width: 100%;
  padding: 12px 0;
}

.tags-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0 16px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tags-scroll::-webkit-scrollbar {
  display: none;
}

.clear-all-btn {
  flex-shrink: 0;
  padding: 6px 12px;
  background-color: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #2681ff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.clear-all-btn:hover {
  background-color: rgba(38, 129, 255, 0.15);
  border-color: rgba(38, 129, 255, 0.3);
}

.clear-all-btn:active {
  background-color: rgba(38, 129, 255, 0.25);
}

.filter-tag {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background-color: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  white-space: nowrap;
  transition: background-color 0.2s ease;
}

.filter-tag:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.tag-thumbnail {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.tag-label {
  color: #fff;
  font-size: 13px;
  font-weight: 500;
}

.tag-remove-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  padding: 0;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: color 0.2s ease;
  flex-shrink: 0;
}

.tag-remove-btn:hover {
  color: #fff;
}

.tag-remove-btn:active {
  color: #2681ff;
}
</style>
