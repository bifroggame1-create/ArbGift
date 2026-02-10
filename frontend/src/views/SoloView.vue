<template>
  <div class="solo-view">
    <div class="page-header">
      <h1 class="page-title font-display">Solo Game</h1>
    </div>

    <!-- Trading — full-width banner card -->
    <router-link to="/trading" class="banner-card base-active-btn">
      <div class="banner-bg">
        <img src="/images/app-trading-bg-1.webp" class="banner-image" alt="" />
      </div>
      <div class="banner-badge">NEW</div>
      <div class="banner-content">
        <h2 class="banner-title">Trading</h2>
        <p class="banner-subtitle">Flip chart, earn TON</p>
      </div>
    </router-link>

    <!-- Game Grid -->
    <div class="games-grid">
      <router-link to="/plinko" class="game-card base-active-btn card-plinko">
        <div class="card-bg">
          <img src="/images/plinko-card-bg-1.webp" class="card-image" alt="" />
        </div>
        <div class="card-content">
          <h3 class="card-title">Gift Plinko</h3>
          <p class="card-subtitle">Plinko with gifts</p>
        </div>
      </router-link>

      <router-link to="/ball-escape" class="game-card base-active-btn card-ball-escape">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <circle cx="70" cy="40" r="20" fill="rgba(139,92,246,0.2)"/>
            <circle cx="40" cy="65" r="15" fill="rgba(168,85,247,0.15)"/>
            <circle cx="85" cy="75" r="12" fill="rgba(139,92,246,0.25)"/>
            <circle cx="55" cy="35" r="8" fill="rgba(168,85,247,0.3)"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Ball Escape</h3>
          <p class="card-subtitle">ASMR fast game</p>
        </div>
      </router-link>

      <router-link to="/upgrade" class="game-card base-active-btn card-upgrade">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <path d="M60 20 L80 55 H68 L75 95 H45 L52 55 H40 Z" fill="rgba(255,197,2,0.25)"/>
            <path d="M55 35 L68 58 H60 L65 85 H50 L55 58 H47 Z" fill="rgba(255,197,2,0.15)"/>
          </svg>
        </div>
        <div class="card-badge">HOT</div>
        <div class="card-content">
          <h3 class="card-title">Gift Upgrade</h3>
          <p class="card-subtitle">Upgrade your gifts</p>
        </div>
      </router-link>

      <router-link to="/rocket" class="game-card base-active-btn card-rocket">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <path d="M60 15 C60 15 80 40 80 70 C80 85 70 95 60 100 C50 95 40 85 40 70 C40 40 60 15 60 15Z" fill="rgba(239,68,68,0.15)" stroke="rgba(239,68,68,0.25)" stroke-width="1"/>
            <circle cx="60" cy="55" r="8" fill="rgba(239,68,68,0.25)"/>
            <path d="M50 85 L45 100" stroke="rgba(251,146,60,0.3)" stroke-width="2"/>
            <path d="M60 90 L60 105" stroke="rgba(251,146,60,0.25)" stroke-width="2"/>
            <path d="M70 85 L75 100" stroke="rgba(251,146,60,0.3)" stroke-width="2"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Rocket</h3>
          <p class="card-subtitle">To the moon</p>
        </div>
      </router-link>

      <router-link to="/lucky" class="game-card base-active-btn card-lucky">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <circle cx="60" cy="55" r="35" fill="rgba(0,255,98,0.06)" stroke="rgba(0,255,98,0.15)" stroke-width="1"/>
            <path d="M60 30 L63 48 L80 42 L68 55 L85 60 L68 65 L80 78 L63 62 L60 80 L57 62 L40 78 L52 65 L35 60 L52 55 L40 42 L57 48 Z" fill="rgba(0,255,98,0.12)"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Lucky Wheel</h3>
          <p class="card-subtitle">Spin to win</p>
        </div>
      </router-link>

    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.solo-view {
  padding: 0 12px;
  padding-bottom: 100px;
}

/* ---------- Header ---------- */
.page-header {
  text-align: center;
  padding: 8px 0 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

/* ---------- Banner (Trading) ---------- */
.banner-card {
  display: block;
  position: relative;
  width: 100%;
  height: 150px;
  border-radius: var(--mb-radius-lg, 16px);
  overflow: hidden;
  text-decoration: none;
  color: #fff;
  margin-bottom: 8px;
}

.banner-bg {
  position: absolute;
  inset: 0;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: rgba(0, 255, 98, 0.15);
  color: var(--mb-green, #00FF62);
  backdrop-filter: blur(4px);
}

.banner-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
}

.banner-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 2px;
}

.banner-subtitle {
  font-size: 13px;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  margin: 0;
}

/* ---------- 2x2 Grid ---------- */
.games-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.game-card {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: var(--mb-radius-lg, 16px);
  overflow: hidden;
  text-decoration: none;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

/* Card backgrounds */
.card-bg {
  position: absolute;
  inset: 0;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-ball-escape .card-bg {
  background: linear-gradient(160deg, #2d1a5e 0%, #1a0f3a 60%, #100a24 100%);
}

.card-upgrade .card-bg {
  background: linear-gradient(160deg, #3a2d0a 0%, #2a1f05 60%, #1a1400 100%);
}

.card-rocket .card-bg {
  background: linear-gradient(160deg, #3a1a1a 0%, #2a0e0e 60%, #1e0808 100%);
}

.card-lucky .card-bg {
  background: linear-gradient(160deg, #0a3a1a 0%, #052a10 60%, #031e0a 100%);
}

.card-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: rgba(255, 197, 2, 0.15);
  color: var(--mb-gold, #FFC502);
  z-index: 2;
}

.card-decoration {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* Card content overlay */
.card-content {
  position: relative;
  z-index: 1;
  padding: 14px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 2px;
}

.card-subtitle {
  font-size: 12px;
  color: var(--mb-text-secondary, rgba(255, 255, 255, 0.5));
  margin: 0;
}
</style>
