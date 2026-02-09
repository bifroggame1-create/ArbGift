<template>
  <div class="pvp-selector">
    <div class="page-header">
      <h1 class="page-title font-display">PvP Game</h1>
    </div>
    <div class="game-cards">
      <router-link to="/pvp/ice" class="game-card base-active-btn">
        <div class="game-card-content">
          <h2>Ice Arena</h2>
          <p>Ice battle for gift, Ton and Stars</p>
        </div>
      </router-link>
      <router-link to="/pvp/race" class="game-card base-active-btn">
        <div class="game-card-content">
          <h2>Ball Race</h2>
          <p>Classic ball race game</p>
        </div>
      </router-link>
      <router-link to="/roulette" class="game-card base-active-btn">
        <div class="game-card-content">
          <h2>Gift Roulette</h2>
          <p>Spin the wheel, win gifts</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.pvp-selector {
  padding: 16px var(--mb-content-padding, 12px);
}
.page-header { text-align: center; padding: 8px 0 20px; }
.page-title { font-size: 28px; font-weight: 700; color: #fff; }
.game-cards { display: flex; flex-direction: column; gap: 8px; }
.game-card {
  display: block;
  background: var(--mb-card, rgba(255,255,255,0.05));
  border-radius: var(--mb-radius-lg, 16px);
  overflow: hidden;
  min-height: 180px;
  position: relative;
  text-decoration: none;
  color: #fff;
}
.game-card-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
}
.game-card-content h2 { font-size: 20px; font-weight: 700; }
.game-card-content p { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 2px; }
</style>
