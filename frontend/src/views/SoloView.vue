<template>
  <div class="solo-view">
    <div class="page-header">
      <h1 class="page-title font-display">Solo Game</h1>
    </div>

    <!-- Trading — full-width banner card -->
    <router-link to="/trading" class="banner-card base-active-btn">
      <div class="banner-bg">
        <!-- Candlestick chart decoration -->
        <svg class="banner-chart" viewBox="0 0 320 120" fill="none" preserveAspectRatio="none">
          <!-- Grid lines -->
          <line x1="0" y1="30" x2="320" y2="30" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
          <line x1="0" y1="60" x2="320" y2="60" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
          <line x1="0" y1="90" x2="320" y2="90" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
          <!-- Candle wicks -->
          <line x1="40" y1="20" x2="40" y2="80" stroke="#22c55e" stroke-width="1" opacity="0.6"/>
          <line x1="70" y1="35" x2="70" y2="90" stroke="#ef4444" stroke-width="1" opacity="0.6"/>
          <line x1="100" y1="15" x2="100" y2="70" stroke="#22c55e" stroke-width="1" opacity="0.6"/>
          <line x1="130" y1="25" x2="130" y2="85" stroke="#22c55e" stroke-width="1" opacity="0.6"/>
          <line x1="160" y1="40" x2="160" y2="95" stroke="#ef4444" stroke-width="1" opacity="0.6"/>
          <line x1="190" y1="10" x2="190" y2="65" stroke="#22c55e" stroke-width="1" opacity="0.6"/>
          <line x1="220" y1="30" x2="220" y2="80" stroke="#ef4444" stroke-width="1" opacity="0.6"/>
          <line x1="250" y1="5" x2="250" y2="55" stroke="#22c55e" stroke-width="1" opacity="0.6"/>
          <line x1="280" y1="20" x2="280" y2="70" stroke="#22c55e" stroke-width="1" opacity="0.6"/>
          <!-- Candle bodies -->
          <rect x="34" y="35" width="12" height="30" rx="2" fill="#22c55e" opacity="0.7"/>
          <rect x="64" y="45" width="12" height="25" rx="2" fill="#ef4444" opacity="0.7"/>
          <rect x="94" y="25" width="12" height="28" rx="2" fill="#22c55e" opacity="0.7"/>
          <rect x="124" y="35" width="12" height="32" rx="2" fill="#22c55e" opacity="0.7"/>
          <rect x="154" y="50" width="12" height="28" rx="2" fill="#ef4444" opacity="0.7"/>
          <rect x="184" y="20" width="12" height="30" rx="2" fill="#22c55e" opacity="0.7"/>
          <rect x="214" y="40" width="12" height="25" rx="2" fill="#ef4444" opacity="0.7"/>
          <rect x="244" y="15" width="12" height="25" rx="2" fill="#22c55e" opacity="0.7"/>
          <rect x="274" y="30" width="12" height="22" rx="2" fill="#22c55e" opacity="0.7"/>
          <!-- Price line -->
          <polyline
            fill="none"
            stroke="rgba(34,197,94,0.5)"
            stroke-width="1.5"
            points="40,35 70,55 100,25 130,35 160,60 190,20 220,45 250,15 280,30"
          />
        </svg>
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
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <circle cx="60" cy="20" r="3" fill="rgba(59,130,246,0.5)"/>
            <circle cx="45" cy="38" r="3" fill="rgba(59,130,246,0.4)"/>
            <circle cx="75" cy="38" r="3" fill="rgba(59,130,246,0.4)"/>
            <circle cx="30" cy="56" r="3" fill="rgba(59,130,246,0.3)"/>
            <circle cx="60" cy="56" r="3" fill="rgba(59,130,246,0.3)"/>
            <circle cx="90" cy="56" r="3" fill="rgba(59,130,246,0.3)"/>
            <circle cx="45" cy="74" r="3" fill="rgba(59,130,246,0.2)"/>
            <circle cx="75" cy="74" r="3" fill="rgba(59,130,246,0.2)"/>
            <circle cx="55" cy="45" r="6" fill="#3b82f6" opacity="0.8"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Gift Plinko</h3>
          <p class="card-subtitle">Plinko with gifts</p>
        </div>
      </router-link>

      <router-link to="/gonka" class="game-card base-active-btn card-gonka">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <circle cx="30" cy="85" r="8" fill="rgba(34,197,94,0.3)"/>
            <circle cx="60" cy="50" r="6" fill="rgba(34,197,94,0.4)"/>
            <circle cx="85" cy="70" r="10" fill="rgba(34,197,94,0.25)"/>
            <circle cx="50" cy="30" r="5" fill="rgba(34,197,94,0.35)"/>
            <circle cx="90" cy="35" r="4" fill="rgba(34,197,94,0.2)"/>
            <path d="M30 90 Q45 40 60 55 Q75 70 90 35" stroke="rgba(34,197,94,0.3)" stroke-width="2" fill="none"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Gonka</h3>
          <p class="card-subtitle">Drop. Bounce. Win</p>
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

      <router-link to="/contracts" class="game-card base-active-btn card-contracts">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <rect x="30" y="25" width="60" height="75" rx="6" fill="rgba(52,205,239,0.1)" stroke="rgba(52,205,239,0.2)" stroke-width="1"/>
            <line x1="42" y1="45" x2="78" y2="45" stroke="rgba(52,205,239,0.25)" stroke-width="2"/>
            <line x1="42" y1="57" x2="70" y2="57" stroke="rgba(52,205,239,0.2)" stroke-width="2"/>
            <line x1="42" y1="69" x2="75" y2="69" stroke="rgba(52,205,239,0.15)" stroke-width="2"/>
            <circle cx="55" cy="85" r="5" fill="rgba(52,205,239,0.3)"/>
            <path d="M52 85 L54 87 L58 83" stroke="#34CDEF" stroke-width="1.5" fill="none"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Contracts</h3>
          <p class="card-subtitle">Smart contracts</p>
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

      <router-link to="/aviator" class="game-card base-active-btn card-aviator">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <path d="M20 90 Q40 85 55 60 Q65 45 75 35 Q85 28 95 25" stroke="rgba(239,68,68,0.35)" stroke-width="2" fill="none"/>
            <path d="M20 90 Q40 85 55 60 Q65 45 75 35 Q85 28 95 25 L95 90 Z" fill="rgba(239,68,68,0.08)"/>
            <circle cx="95" cy="25" r="4" fill="rgba(239,68,68,0.5)"/>
            <path d="M88 22 L95 15 L98 28" stroke="rgba(239,68,68,0.4)" stroke-width="1.5" fill="none"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Aviator</h3>
          <p class="card-subtitle">Catch the moment</p>
        </div>
      </router-link>

      <router-link to="/stars" class="game-card base-active-btn card-stars">
        <div class="card-bg">
          <svg class="card-decoration" viewBox="0 0 120 120" fill="none">
            <polygon points="60,15 68,42 97,42 74,58 82,85 60,70 38,85 46,58 23,42 52,42" fill="rgba(255,197,2,0.15)" stroke="rgba(255,197,2,0.25)" stroke-width="1"/>
            <polygon points="40,75 44,86 56,86 47,93 50,104 40,97 30,104 33,93 24,86 36,86" fill="rgba(255,197,2,0.1)"/>
            <polygon points="85,65 87,72 95,72 89,76 91,83 85,79 79,83 81,76 75,72 83,72" fill="rgba(255,197,2,0.1)"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">Stars</h3>
          <p class="card-subtitle">Collect stars</p>
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
  background: linear-gradient(135deg, #0a1628 0%, #0f2847 40%, #0d1f3a 100%);
}

.banner-chart {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.7;
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

.card-plinko .card-bg {
  background: linear-gradient(160deg, #1a3a6b 0%, #0e1e3a 60%, #0a1528 100%);
}

.card-gonka .card-bg {
  background: linear-gradient(160deg, #0f3a20 0%, #0a2615 60%, #071a0e 100%);
}

.card-ball-escape .card-bg {
  background: linear-gradient(160deg, #2d1a5e 0%, #1a0f3a 60%, #100a24 100%);
}

.card-upgrade .card-bg {
  background: linear-gradient(160deg, #3a2d0a 0%, #2a1f05 60%, #1a1400 100%);
}

.card-contracts .card-bg {
  background: linear-gradient(160deg, #0a2a3a 0%, #071e2a 60%, #05141e 100%);
}

.card-rocket .card-bg {
  background: linear-gradient(160deg, #3a1a1a 0%, #2a0e0e 60%, #1e0808 100%);
}

.card-lucky .card-bg {
  background: linear-gradient(160deg, #0a3a1a 0%, #052a10 60%, #031e0a 100%);
}

.card-aviator .card-bg {
  background: linear-gradient(160deg, #3a1020 0%, #2a0a15 60%, #1e050e 100%);
}

.card-stars .card-bg {
  background: linear-gradient(160deg, #3a3010 0%, #2a220a 60%, #1e1805 100%);
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
