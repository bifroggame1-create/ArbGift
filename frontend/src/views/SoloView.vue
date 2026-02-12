<template>
  <div class="solo-view">
    <div class="page-header">
      <h1 class="page-title font-display">Solo Game</h1>
    </div>

    <!-- Trading — full-width banner card -->
    <router-link to="/trading" class="banner-card base-active-btn">
      <div class="banner-bg">
        <img src="/images/trading-card-bg.webp" class="banner-image" alt="" />
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
        <div class="card-badge mult-badge">x100</div>
        <div class="card-content">
          <h3 class="card-title">Gift Plinko</h3>
          <p class="card-subtitle">Plinko with gifts</p>
        </div>
      </router-link>

      <router-link to="/ball-escape" class="game-card base-active-btn card-ball-escape">
        <div class="card-bg">
          <img src="/images/escape-card-bg.webp" class="card-image" alt="" />
        </div>
        <div class="card-content">
          <h3 class="card-title">Ball Escape</h3>
          <p class="card-subtitle">ASMR fast game</p>
        </div>
      </router-link>

      <router-link to="/upgrade" class="game-card base-active-btn card-upgrade">
        <div class="card-bg">
          <div class="upgrade-visual">
            <div class="upgrade-arrow">
              <svg viewBox="0 0 48 48" fill="none">
                <path d="M24 40V12M24 12L12 24M24 12L36 24" stroke="rgba(255,197,2,0.6)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
        <div class="card-badge hot-badge">HOT</div>
        <div class="card-content">
          <h3 class="card-title">Gift Upgrade</h3>
          <p class="card-subtitle">Upgrade your gifts</p>
        </div>
      </router-link>

      <router-link to="/rocket" class="game-card base-active-btn card-rocket">
        <div class="card-bg">
          <div class="rocket-visual">
            <div class="rocket-icon">🚀</div>
          </div>
        </div>
        <div class="card-content">
          <h3 class="card-title">Rocket</h3>
          <p class="card-subtitle">To the moon</p>
        </div>
      </router-link>

      <router-link to="/lucky" class="game-card base-active-btn card-lucky game-card-wide">
        <div class="card-bg">
          <div class="lucky-visual">
            <div class="lucky-icon">🎡</div>
          </div>
        </div>
        <div class="card-badge soon-badge">SOON</div>
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
  padding: 8px 0 16px;
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
  height: 140px;
  border-radius: 16px;
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
  color: #00FF62;
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
  color: rgba(255, 255, 255, 0.5);
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
  border-radius: 16px;
  overflow: hidden;
  text-decoration: none;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.game-card-wide {
  grid-column: 1 / -1;
  aspect-ratio: 2.2 / 1;
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

.card-upgrade .card-bg {
  background: linear-gradient(160deg, #3a2d0a 0%, #2a1f05 60%, #1a1400 100%);
}

.card-rocket .card-bg {
  background: linear-gradient(160deg, #2a1030 0%, #1a0a20 60%, #0e0614 100%);
}

.card-lucky .card-bg {
  background: linear-gradient(160deg, #0a2a3a 0%, #061a2a 60%, #03101e 100%);
}

/* Badges */
.card-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  z-index: 2;
  backdrop-filter: blur(4px);
}

.mult-badge {
  background: rgba(57, 26, 173, 0.4);
  color: #A78BFA;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.hot-badge {
  background: rgba(255, 197, 2, 0.15);
  color: #FFC502;
}

.soon-badge {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.4);
}

/* Card visuals */
.upgrade-visual {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upgrade-arrow {
  width: 60px;
  height: 60px;
  opacity: 0.6;
}

.rocket-visual {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rocket-icon {
  font-size: 48px;
  filter: drop-shadow(0 4px 12px rgba(239, 68, 68, 0.3));
}

.lucky-visual {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lucky-icon {
  font-size: 52px;
  filter: drop-shadow(0 4px 12px rgba(52, 211, 153, 0.3));
}

/* Card content overlay */
.card-content {
  position: relative;
  z-index: 1;
  padding: 14px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.65));
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 2px;
}

.card-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}
</style>
