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

      <router-link to="/rocket" class="game-card base-active-btn card-rocket game-card-wide rocket-banner">
        <div class="card-bg rocket-bg">
          <!-- Blurred light circles -->
          <div class="rocket-glow rocket-glow-1"></div>
          <div class="rocket-glow rocket-glow-2"></div>
          <div class="rocket-glow rocket-glow-3"></div>
          <!-- Geometric light triangles -->
          <div class="rocket-triangle rocket-tri-1"></div>
          <div class="rocket-triangle rocket-tri-2"></div>
          <!-- Star decorations -->
          <svg class="rocket-star" style="left:8%;top:15%;width:12px;opacity:0.6;transform:rotate(-10deg)"><polygon points="7,0 9,5 14,5 10,8 12,13 7,10 2,13 4,8 0,5 5,5" fill="white"/></svg>
          <svg class="rocket-star" style="left:18%;top:35%;width:16px;opacity:0.9;transform:rotate(-10deg)"><polygon points="7,0 9,5 14,5 10,8 12,13 7,10 2,13 4,8 0,5 5,5" fill="white"/></svg>
          <svg class="rocket-star" style="left:30%;top:10%;width:14px;opacity:0.5;filter:blur(1px);transform:rotate(-10deg)"><polygon points="7,0 9,5 14,5 10,8 12,13 7,10 2,13 4,8 0,5 5,5" fill="white"/></svg>
          <svg class="rocket-star" style="left:60%;top:30%;width:16px;opacity:0.8;transform:rotate(-10deg)"><polygon points="7,0 9,5 14,5 10,8 12,13 7,10 2,13 4,8 0,5 5,5" fill="white"/></svg>
          <svg class="rocket-star" style="left:45%;bottom:10%;width:18px;opacity:0.7;filter:blur(1px);transform:rotate(-10deg)"><polygon points="7,0 9,5 14,5 10,8 12,13 7,10 2,13 4,8 0,5 5,5" fill="white"/></svg>
          <svg class="rocket-star" style="left:70%;bottom:20%;width:22px;opacity:0.9;transform:rotate(-10deg)"><polygon points="7,0 9,5 14,5 10,8 12,13 7,10 2,13 4,8 0,5 5,5" fill="white"/></svg>
          <svg class="rocket-star" style="right:10%;top:40%;width:12px;opacity:0.6;filter:blur(0.5px);transform:rotate(-10deg)"><polygon points="7,0 9,5 14,5 10,8 12,13 7,10 2,13 4,8 0,5 5,5" fill="white"/></svg>
        </div>
        <!-- 3D Rocket image -->
        <img src="/images/rocket.png" class="rocket-3d" alt="" />
        <!-- Floating multiplier badges -->
        <div class="rocket-mult rocket-mult-1"><span>x4.84</span></div>
        <div class="rocket-mult rocket-mult-2"><span>x2.38</span></div>
        <div class="rocket-mult rocket-mult-3"><span>x4.19</span></div>
        <div class="rocket-mult rocket-mult-4"><span>x2.02</span></div>
        <!-- HIT badge -->
        <div class="rocket-hit-badge">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M3.71 1.42C3.8 1.17 4.04 1 4.3 1H7.53C7.95 1 8.26 1.42 8.12 1.82L7.4 4H9.37C9.93 4 10.21 4.66 9.82 5.06L4.29 10.77C3.77 11.31 2.86 10.82 3.02 10.08L3.66 7.25L2.87 7.25C2.27 7.24 1.85 6.64 2.05 6.08L3.71 1.42Z" fill="currentColor"/></svg>
          <span>HIT</span>
        </div>
        <!-- Title -->
        <div class="rocket-title-row">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M13.06 7.43C14.03 6.45 15.62 6.45 16.59 7.43C17.57 8.41 17.57 9.99 16.59 10.97C15.62 11.94 14.03 11.94 13.06 10.97C12.08 9.99 12.08 8.41 13.06 7.43ZM15.53 8.49C15.14 8.1 14.51 8.1 14.12 8.49C13.73 8.88 13.73 9.52 14.12 9.91C14.51 10.3 15.14 10.3 15.53 9.91C15.92 9.52 15.92 8.88 15.53 8.49ZM21.51 4.32C21.24 3.46 20.56 2.78 19.7 2.51L19.04 2.31C16.64 1.56 14.03 2.21 12.26 3.98L11.27 4.98C9.9 3.95 7.94 4.06 6.7 5.3L5.45 6.55C5.16 6.84 5.16 7.31 5.45 7.61L7.05 9.2L6.87 9.38C6.18 10.06 6.18 11.17 6.87 11.85L7.36 12.35L5.97 13.14C5.76 13.26 5.62 13.46 5.59 13.69C5.56 13.93 5.64 14.16 5.81 14.32L9.7 18.21C9.86 18.38 10.09 18.46 10.33 18.43C10.56 18.4 10.76 18.26 10.88 18.06L11.67 16.66L12.17 17.16C12.86 17.84 13.96 17.84 14.65 17.16L14.82 16.98L16.41 18.57C16.71 18.86 17.18 18.86 17.47 18.57L18.72 17.33C19.96 16.08 20.07 14.13 19.04 12.76L20.04 11.76C21.81 9.99 22.46 7.38 21.72 4.99L21.51 4.32Z" fill="white"/></svg>
          <h3 class="rocket-title">ROCKET</h3>
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

/* ---------- Rocket Banner ---------- */
.rocket-banner {
  aspect-ratio: 2.6 / 1;
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.rocket-bg {
  background: linear-gradient(135deg, #3B82C4 0%, #2563A0 40%, #4A90D9 100%);
}

.rocket-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(16px);
  mix-blend-mode: soft-light;
}

.rocket-glow-1 {
  width: 100px; height: 110px;
  background: rgba(255,255,255,0.5);
  left: -20px; top: -40px;
}

.rocket-glow-2 {
  width: 80px; height: 80px;
  background: rgba(100,180,255,0.4);
  left: 50%; top: -30px;
  filter: blur(40px);
}

.rocket-glow-3 {
  width: 100px; height: 80px;
  background: rgba(255,255,255,0.3);
  right: 10px; bottom: -20px;
  filter: blur(40px);
  mix-blend-mode: luminosity;
}

.rocket-triangle {
  position: absolute;
  background: rgba(255,255,255,0.08);
  clip-path: polygon(0 0, 100% 0, 100% 100%);
  transform: rotate(-174deg);
}

.rocket-tri-1 {
  width: 200px; height: 220px;
  left: 25%; top: -100px;
}

.rocket-tri-2 {
  width: 150px; height: 170px;
  left: 45%; top: -60px;
  background: rgba(255,255,255,0.12);
}

.rocket-star {
  position: absolute;
  z-index: 1;
}

.rocket-3d {
  position: absolute;
  right: 8%;
  top: -8px;
  width: 110px;
  height: 110px;
  object-fit: contain;
  z-index: 10;
  transform: rotate(-8deg);
  filter: drop-shadow(0 4px 12px rgba(74, 144, 226, 0.4));
}

/* Floating green multiplier badges */
.rocket-mult {
  position: absolute;
  z-index: 5;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.25);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  backdrop-filter: blur(12px);
  transform: rotate(10deg);
}

.rocket-mult span {
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  line-height: 1;
}

.rocket-mult-1 {
  background: rgba(0, 255, 47, 0.5);
  left: 42%; top: 12%;
  animation: rocketFloat 3s ease-in-out infinite;
}

.rocket-mult-2 {
  background: rgba(0, 255, 47, 0.3);
  left: 55%; top: 55%;
  font-size: 11px;
  animation: rocketFloat 3s ease-in-out 0.8s infinite;
}

.rocket-mult-2 span { font-size: 11px; }

.rocket-mult-3 {
  background: rgba(0, 255, 47, 0.3);
  right: 5%; top: 15%;
  animation: rocketFloat 3s ease-in-out 1.5s infinite;
}

.rocket-mult-3 span { font-size: 11px; }

.rocket-mult-4 {
  background: rgba(0, 255, 47, 0.25);
  right: 12%; bottom: 18%;
  animation: rocketFloat 3s ease-in-out 2.2s infinite;
}

.rocket-mult-4 span { font-size: 10px; }

@keyframes rocketFloat {
  0%, 100% { transform: rotate(10deg) translateY(0); }
  50% { transform: rotate(10deg) translateY(-6px); }
}

/* HIT badge */
.rocket-hit-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.25);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 10;
  color: #3B82C4;
  font-size: 11px;
  font-weight: 700;
}

/* Rocket title row */
.rocket-title-row {
  position: absolute;
  bottom: 14px;
  left: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 10;
}

.rocket-title {
  font-size: 22px;
  font-weight: 900;
  color: #fff;
  margin: 0;
  letter-spacing: 1px;
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
