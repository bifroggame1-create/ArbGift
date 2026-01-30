<template>
  <div
    class="game-card relative overflow-hidden rounded-2xl cursor-pointer transform transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
    :class="`bg-gradient-to-br ${gradient}`"
    @click="$emit('click')"
  >
    <!-- Animated Background Pattern -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent_50%)]"></div>
    </div>

    <!-- Content -->
    <div class="relative p-5">
      <!-- Header -->
      <div class="flex items-start justify-between mb-3">
        <div class="flex items-center space-x-3">
          <div class="text-4xl">{{ icon }}</div>
          <div>
            <h3 class="text-xl font-bold text-white">{{ title }}</h3>
            <p class="text-sm text-white/70">{{ subtitle }}</p>
          </div>
        </div>

        <!-- Arrow Icon -->
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>

      <!-- Description -->
      <div class="mb-4">
        <p class="text-sm text-white/80 leading-relaxed">
          <slot name="description" />
        </p>
      </div>

      <!-- Features -->
      <div class="flex flex-wrap gap-2 mb-4">
        <slot name="features" />
      </div>

      <!-- Stats -->
      <div v-if="stats" class="flex items-center space-x-6 pt-3 border-t border-white/20">
        <div class="flex items-center space-x-2">
          <svg class="w-4 h-4 text-white/60" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
          </svg>
          <span class="text-xs font-medium text-white/80">{{ stats.players }} players</span>
        </div>
        <div class="flex items-center space-x-2">
          <svg class="w-4 h-4 text-white/60" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
          </svg>
          <span class="text-xs font-medium text-white/80">{{ stats.volume }} volume</span>
        </div>
      </div>
    </div>

    <!-- Shine Effect on Hover -->
    <div class="shine absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500">
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 -translate-x-full hover:translate-x-full transition-transform duration-1000"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  subtitle: string
  icon: string
  gradient: string
  stats?: {
    players?: string
    volume?: string
    exchanges?: string
  }
}

defineProps<Props>()
defineEmits(['click'])
</script>

<style scoped>
.game-card {
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.3);
}

.game-card:active {
  box-shadow: 0 5px 20px -5px rgba(0, 0, 0, 0.3);
}
</style>
