<template>
  <div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Search Input -->
    <div class="mb-6">
      <div class="relative">
        <input
          v-model="query"
          type="text"
          placeholder="Search gifts..."
          class="w-full px-4 py-3 pl-12 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          @input="onSearchInput"
        />
        <svg
          class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>

    <!-- Autocomplete suggestions -->
    <div v-if="suggestions.length > 0 && query" class="mb-6">
      <div class="bg-gray-800 rounded-xl p-2 space-y-1">
        <button
          v-for="(suggestion, index) in suggestions"
          :key="index"
          class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="loading" />

    <!-- Results -->
    <div v-else-if="results.length > 0">
      <div class="mb-4 text-gray-400">
        Found {{ results.length }} result{{ results.length !== 1 ? 's' : '' }}
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <GiftCard v-for="gift in results" :key="gift.id" :gift="gift" />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="query" class="text-center py-16">
      <div class="text-6xl mb-4">🔍</div>
      <h3 class="text-xl font-semibold mb-2">No results found</h3>
      <p class="text-gray-400">Try different keywords</p>
    </div>

    <!-- Initial State -->
    <div v-else class="text-center py-16">
      <div class="text-6xl mb-4">🎁</div>
      <h3 class="text-xl font-semibold mb-2">Search for gifts</h3>
      <p class="text-gray-400">Enter a keyword to get started</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { searchGifts, autocomplete } from '../api/client'
import type { Gift } from '../api/client'
import GiftCard from '../components/GiftCard.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const query = ref('')
const results = ref<Gift[]>([])
const suggestions = ref<string[]>([])
const loading = ref(false)

let searchTimeout: NodeJS.Timeout

const onSearchInput = () => {
  // Clear previous timeout
  clearTimeout(searchTimeout)

  // Debounce search
  searchTimeout = setTimeout(async () => {
    if (query.value.length < 2) {
      results.value = []
      suggestions.value = []
      return
    }

    await Promise.all([
      performSearch(),
      loadSuggestions(),
    ])
  }, 300)
}

const performSearch = async () => {
  try {
    loading.value = true
    const data = await searchGifts(query.value)
    results.value = data.hits || data.results || []
  } catch (error) {
    console.error('Search failed:', error)
    results.value = []
  } finally {
    loading.value = false
  }
}

const loadSuggestions = async () => {
  try {
    const data = await autocomplete(query.value)
    suggestions.value = data.suggestions || []
  } catch (error) {
    console.error('Autocomplete failed:', error)
    suggestions.value = []
  }
}

const selectSuggestion = (suggestion: string) => {
  query.value = suggestion
  suggestions.value = []
  performSearch()
}
</script>
