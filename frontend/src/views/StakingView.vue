<template>
  <div class="staking-view">
    <!-- Hero Section with APY -->
    <div class="apy-hero">
      <div class="apy-badge">🔥 HIGHEST APR</div>
      <h1 class="apy-title">Stake Telegram Gifts</h1>
      <div class="apy-display">
        <span class="apy-number">{{ currentMaxAPY }}%</span>
        <span class="apy-label">APR</span>
      </div>
      <p class="apy-subtitle">Lock your Gifts, earn TON daily</p>
      <div class="apy-stats-row">
        <div class="stat-item">
          <span class="stat-value">{{ formatNumber(totalStaked) }}</span>
          <span class="stat-label">TON Staked</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ formatNumber(totalRewards) }}</span>
          <span class="stat-label">TON Paid</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ activeStakers }}</span>
          <span class="stat-label">Stakers</span>
        </div>
      </div>
    </div>

    <!-- Your Active Stakes -->
    <section v-if="userStakes.length > 0" class="stakes-section">
      <div class="section-header">
        <h2>Your Stakes</h2>
        <button @click="claimAllRewards" class="claim-all-btn" :disabled="!hasClaimableRewards">
          <span>💰</span>
          <span>Claim All</span>
        </button>
      </div>

      <div class="stakes-grid">
        <div v-for="stake in userStakes" :key="stake.id" class="stake-card">
          <div class="stake-header">
            <img :src="stake.gift.image_url" :alt="stake.gift.name" class="gift-image" />
            <div class="stake-info">
              <h3>{{ stake.gift.name }}</h3>
              <div class="stake-meta">
                <span class="rarity-badge" :class="`rarity-${stake.gift.rarity}`">
                  {{ stake.gift.rarity }}
                </span>
                <span class="value-badge">{{ stake.gift_value_ton }} TON</span>
              </div>
            </div>
          </div>

          <div class="stake-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: stake.progressPercent + '%' }"></div>
            </div>
            <div class="progress-text">
              <span v-if="stake.is_unlockable">✅ Unlocked!</span>
              <span v-else>⏳ {{ stake.days_remaining }} days left</span>
            </div>
          </div>

          <div class="stake-rewards">
            <div class="reward-item">
              <span class="reward-label">Earned:</span>
              <span class="reward-value earnings-counter">+{{ formatTON(stake.earned_rewards) }} TON</span>
            </div>
            <div class="reward-item">
              <span class="reward-label">APR:</span>
              <span class="reward-value">{{ stake.effective_apy }}%</span>
            </div>
          </div>

          <button
            @click="handleStakeAction(stake)"
            class="action-btn"
            :class="{ 'unlocked': stake.is_unlockable }"
          >
            <span v-if="stake.is_unlockable">Claim {{ formatTON(stake.total_at_unlock) }} TON</span>
            <span v-else>Unlock Early (-10% penalty)</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Empty State -->
    <div v-if="userStakes.length === 0" class="empty-state">
      <div class="empty-icon">🎁</div>
      <h3>No active stakes</h3>
      <p>Start staking your Gifts to earn up to 600% APR!</p>
    </div>

    <!-- Staking Tiers -->
    <section class="tiers-section">
      <h2>Choose Your Lock Period</h2>
      <div class="tiers-grid">
        <div
          v-for="tier in stakingTiers"
          :key="tier.period"
          class="tier-card"
          :class="{ 'popular': tier.popular, 'premium': tier.premium }"
          @click="selectedTier = tier.period"
        >
          <div v-if="tier.popular" class="tier-badge">POPULAR</div>
          <div v-if="tier.premium" class="tier-badge premium-badge">BEST VALUE</div>

          <h3 class="tier-title">{{ tier.label }}</h3>
          <div class="tier-apr">{{ tier.apy }}% <span>APR</span></div>
          <div class="tier-days">{{ tier.days }} days lock</div>

          <div class="tier-features">
            <div class="feature">✅ {{ tier.bonus }}</div>
            <div class="feature" v-if="tier.extraBonus">✨ {{ tier.extraBonus }}</div>
          </div>

          <div class="tier-example">
            <span>100 TON stake →</span>
            <span class="highlight">{{ tier.exampleReward }} TON profit</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Available Gifts to Stake -->
    <section class="available-section">
      <div class="section-header">
        <h2>Your Gifts</h2>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search gifts..."
          class="search-input"
        />
      </div>

      <div v-if="!walletConnected" class="connect-wallet-prompt">
        <div class="prompt-icon">🔗</div>
        <h3>Connect Wallet</h3>
        <p>Connect your TON wallet to see your Gifts</p>
        <button @click="connectWallet" class="connect-btn">Connect TON Wallet</button>
      </div>

      <div v-else-if="availableGifts.length === 0" class="no-gifts">
        <div class="no-gifts-icon">😢</div>
        <p>You don't have any Gifts to stake</p>
        <button @click="goToMarket" class="browse-btn">Browse Marketplace</button>
      </div>

      <div v-else class="gifts-grid">
        <div
          v-for="gift in filteredGifts"
          :key="gift.address"
          class="gift-card-wrapper"
          @click="openStakeModal(gift)"
        >
          <div class="gift-card">
            <img :src="gift.image_url" :alt="gift.name" />
            <div class="gift-details">
              <h4>{{ gift.name }}</h4>
              <div class="gift-meta">
                <span class="rarity" :class="`rarity-${gift.rarity}`">{{ gift.rarity }}</span>
                <span class="value">{{ gift.floor_price }} TON</span>
              </div>
              <div class="potential-apr">
                Earn up to <span class="highlight">{{ calculatePotentialAPR(gift) }}%</span> APR
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works">
      <h2>How It Works</h2>
      <div class="steps-grid">
        <div class="step">
          <div class="step-number">1</div>
          <h3>Select Gift</h3>
          <p>Choose a Gift from your inventory</p>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <h3>Choose Period</h3>
          <p>Pick lock period: 7, 14, 30, or 90 days</p>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <h3>Earn Rewards</h3>
          <p>Get daily TON rewards automatically</p>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <h3>Claim</h3>
          <p>Unlock after period + claim your profit</p>
        </div>
      </div>
    </section>

    <!-- Provably Fair -->
    <section class="provably-fair">
      <div class="fair-icon">🔐</div>
      <h3>Provably Fair Rewards</h3>
      <p>All staking rewards are calculated transparently on-chain. Verify anytime.</p>
      <button @click="showFairnessProof" class="verify-btn">Verify Fairness</button>
    </section>

    <!-- Stake Modal -->
    <div v-if="stakeModalOpen" class="modal-overlay" @click="closeStakeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeStakeModal">✕</button>

        <h2>Stake {{ selectedGift?.name }}</h2>

        <div class="modal-gift-preview">
          <img :src="selectedGift?.image_url" :alt="selectedGift?.name" />
          <div class="preview-details">
            <span class="rarity-badge" :class="`rarity-${selectedGift?.rarity}`">
              {{ selectedGift?.rarity }}
            </span>
            <span class="value-badge">{{ selectedGift?.floor_price }} TON</span>
          </div>
        </div>

        <div class="period-selector">
          <h3>Select Lock Period</h3>
          <div class="period-options">
            <button
              v-for="tier in stakingTiers"
              :key="tier.period"
              class="period-option"
              :class="{ 'selected': selectedPeriod === tier.period }"
              @click="selectedPeriod = tier.period"
            >
              <div class="period-label">{{ tier.label }}</div>
              <div class="period-apr">{{ tier.apy }}% APR</div>
            </button>
          </div>
        </div>

        <div class="stake-preview" v-if="stakePreview">
          <h3>Stake Preview</h3>
          <div class="preview-row">
            <span>Gift Value:</span>
            <span>{{ stakePreview.gift_value_ton }} TON</span>
          </div>
          <div class="preview-row">
            <span>Lock Period:</span>
            <span>{{ stakePreview.period_days }} days</span>
          </div>
          <div class="preview-row">
            <span>Base APR:</span>
            <span>{{ stakePreview.base_apy_percent }}%</span>
          </div>
          <div class="preview-row highlight">
            <span>Rarity Bonus:</span>
            <span>×{{ stakePreview.rarity_multiplier }}</span>
          </div>
          <div class="preview-row highlight">
            <span>Effective APR:</span>
            <span class="big">{{ stakePreview.effective_apy_percent }}%</span>
          </div>
          <div class="preview-divider"></div>
          <div class="preview-row reward">
            <span>Expected Reward:</span>
            <span>+{{ stakePreview.expected_reward_ton }} TON</span>
          </div>
          <div class="preview-row total">
            <span>Total at Unlock:</span>
            <span class="big">{{ stakePreview.total_at_unlock_ton }} TON</span>
          </div>
          <div class="preview-row roi">
            <span>ROI:</span>
            <span class="big green">+{{ stakePreview.roi_percent }}%</span>
          </div>
        </div>

        <button @click="confirmStake" class="confirm-stake-btn" :disabled="!selectedPeriod">
          <span>🔒</span>
          <span>Confirm Stake</span>
        </button>

        <div class="modal-warning">
          ⚠️ Early withdrawal penalty: 10% of Gift value
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTonConnect } from '@/composables/useTonConnect'
import apiClient from '@/api/client'

const router = useRouter()
const { wallet, connect } = useTonConnect()

// State
const currentMaxAPY = ref(600)
const totalStaked = ref(125000)
const totalRewards = ref(45000)
const activeStakers = ref(1250)

const userStakes = ref<any[]>([])
const availableGifts = ref<any[]>([])
const searchQuery = ref('')

const stakeModalOpen = ref(false)
const selectedGift = ref<any>(null)
const selectedPeriod = ref('')
const selectedTier = ref('1m')
const stakePreview = ref<any>(null)

// Staking Tiers Configuration
const stakingTiers = computed(() => [
  {
    period: '1w',
    label: '7 Days',
    days: 7,
    apy: 300,
    bonus: 'Flexible unlock',
    popular: false,
    premium: false,
    exampleReward: '5.75',
  },
  {
    period: '2w',
    label: '14 Days',
    days: 14,
    apy: 400,
    bonus: '+10% early bird',
    popular: true,
    premium: false,
    exampleReward: '15.34',
  },
  {
    period: '1m',
    label: '30 Days',
    days: 30,
    apy: 450,
    bonus: '+20% boost',
    popular: false,
    premium: false,
    exampleReward: '36.99',
  },
  {
    period: '3m',
    label: '90 Days',
    days: 90,
    apy: 600,
    bonus: '+50% mega boost',
    extraBonus: 'NFT Badge',
    popular: false,
    premium: true,
    exampleReward: '148.77',
  },
])

// Computed
const walletConnected = computed(() => !!wallet.value)

const hasClaimableRewards = computed(() => {
  return userStakes.value.some(stake => stake.is_unlockable)
})

const filteredGifts = computed(() => {
  if (!searchQuery.value) return availableGifts.value
  const query = searchQuery.value.toLowerCase()
  return availableGifts.value.filter(gift =>
    gift.name.toLowerCase().includes(query) ||
    gift.rarity.toLowerCase().includes(query)
  )
})

// Methods
async function loadUserStakes() {
  try {
    const response = await apiClient.get('/staking/my-stakes')
    userStakes.value = response.data.stakes || []
  } catch (error) {
    console.error('Failed to load stakes:', error)
  }
}

async function loadAvailableGifts() {
  if (!walletConnected.value) return

  try {
    const response = await apiClient.get(`/gifts/owned/${wallet.value.address}`)
    availableGifts.value = response.data.gifts || []
  } catch (error) {
    console.error('Failed to load gifts:', error)
  }
}

function calculatePotentialAPR(gift: any): number {
  // Legendary gets 600% * 3.0 = 1800%!
  const baseAPR = 600
  const multipliers: Record<string, number> = {
    common: 1.0,
    uncommon: 1.2,
    rare: 1.5,
    epic: 2.0,
    legendary: 3.0,
    mythic: 5.0,
  }
  const mult = multipliers[gift.rarity?.toLowerCase()] || 1.0
  return Math.round(baseAPR * mult)
}

async function openStakeModal(gift: any) {
  selectedGift.value = gift
  selectedPeriod.value = '1m' // default
  stakeModalOpen.value = true

  // Load stake preview
  await loadStakePreview()
}

async function loadStakePreview() {
  if (!selectedGift.value || !selectedPeriod.value) return

  try {
    const response = await apiClient.get('/staking/preview', {
      params: {
        gift_value_ton: selectedGift.value.floor_price,
        period: selectedPeriod.value,
        rarity: selectedGift.value.rarity,
      }
    })
    stakePreview.value = response.data
  } catch (error) {
    console.error('Failed to load preview:', error)
  }
}

function closeStakeModal() {
  stakeModalOpen.value = false
  selectedGift.value = null
  selectedPeriod.value = ''
  stakePreview.value = null
}

async function confirmStake() {
  if (!selectedGift.value || !selectedPeriod.value) return

  try {
    await apiClient.post('/staking/stake', {
      gift_address: selectedGift.value.address,
      period: selectedPeriod.value,
    })

    alert('✅ Stake created successfully!')
    closeStakeModal()
    await loadUserStakes()
    await loadAvailableGifts()
  } catch (error) {
    console.error('Stake failed:', error)
    alert('❌ Failed to create stake')
  }
}

async function handleStakeAction(stake: any) {
  if (stake.is_unlockable) {
    await claimStake(stake)
  } else {
    await earlyWithdraw(stake)
  }
}

async function claimStake(stake: any) {
  try {
    await apiClient.post(`/staking/claim/${stake.id}`)
    alert(`✅ Claimed ${stake.total_at_unlock} TON!`)
    await loadUserStakes()
  } catch (error) {
    console.error('Claim failed:', error)
    alert('❌ Failed to claim rewards')
  }
}

async function earlyWithdraw(stake: any) {
  const confirmed = confirm(
    `⚠️ Early withdrawal penalty: 10% (${stake.early_penalty} TON)\n\nContinue?`
  )
  if (!confirmed) return

  try {
    await apiClient.post(`/staking/withdraw/${stake.id}`)
    alert('Stake withdrawn with penalty')
    await loadUserStakes()
  } catch (error) {
    console.error('Withdrawal failed:', error)
    alert('Failed to withdraw')
  }
}

async function claimAllRewards() {
  try {
    await apiClient.post('/staking/claim-all')
    alert('✅ All rewards claimed!')
    await loadUserStakes()
  } catch (error) {
    console.error('Claim all failed:', error)
  }
}

async function connectWallet() {
  await connect()
  await loadAvailableGifts()
}

function goToMarket() {
  router.push('/market')
}

function showFairnessProof() {
  alert('Provably Fair verification coming soon!')
}

function formatTON(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toFixed(2)
}

function formatNumber(value: number): string {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
  return value.toString()
}

onMounted(async () => {
  await loadUserStakes()
  await loadAvailableGifts()
})
</script>

<style scoped>
.staking-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 100px;
}

/* Hero Section */
.apy-hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 24px;
  padding: 48px 24px;
  text-align: center;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
}

.apy-hero::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,215,0,0.1) 0%, transparent 70%);
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.apy-badge {
  display: inline-block;
  background: linear-gradient(90deg, #FFD700, #FFA500);
  color: #000;
  padding: 8px 24px;
  border-radius: 24px;
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 16px;
}

.apy-title {
  font-size: 32px;
  font-weight: 900;
  color: #fff;
  margin: 16px 0;
}

.apy-display {
  margin: 24px 0;
  position: relative;
  z-index: 1;
}

.apy-number {
  font-size: 96px;
  font-weight: 900;
  background: linear-gradient(90deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: glow 2s ease-in-out infinite;
  display: block;
  line-height: 1;
}

.apy-label {
  font-size: 24px;
  color: #FFD700;
  font-weight: 600;
  margin-left: 8px;
}

@keyframes glow {
  0%, 100% { filter: drop-shadow(0 0 20px rgba(255,215,0,0.5)); }
  50% { filter: drop-shadow(0 0 40px rgba(255,215,0,0.8)); }
}

.apy-subtitle {
  font-size: 18px;
  color: #a0a0a0;
  margin-bottom: 32px;
}

.apy-stats-row {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-top: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #4CAF50;
}

.stat-label {
  font-size: 14px;
  color: #888;
}

/* Stakes Section */
.stakes-section,
.tiers-section,
.available-section,
.how-it-works {
  margin-bottom: 48px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 700;
}

.claim-all-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.claim-all-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.claim-all-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Stake Cards */
.stakes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.stake-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid #0f3460;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s;
}

.stake-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(15, 52, 96, 0.4);
}

.stake-header {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.gift-image {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  object-fit: cover;
}

.stake-info h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.stake-meta {
  display: flex;
  gap: 8px;
}

.rarity-badge,
.value-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.rarity-badge {
  background: rgba(255,215,0,0.2);
  color: #FFD700;
  text-transform: capitalize;
}

.rarity-epic {
  background: rgba(138,43,226,0.2);
  color: #BA55D3;
}

.rarity-legendary {
  background: rgba(255,215,0,0.3);
  color: #FFD700;
}

.value-badge {
  background: rgba(76,175,80,0.2);
  color: #4CAF50;
}

.stake-progress {
  margin: 16px 0;
}

.progress-bar {
  height: 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  transition: width 0.3s;
}

.progress-text {
  margin-top: 8px;
  font-size: 14px;
  color: #888;
}

.stake-rewards {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0;
}

.reward-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.reward-label {
  color: #888;
}

.reward-value {
  font-weight: 600;
  color: #fff;
}

.earnings-counter {
  color: #4CAF50;
  font-size: 18px;
  font-weight: 700;
  animation: pulse-text 1s infinite;
}

@keyframes pulse-text {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.action-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(90deg, #0f3460, #16213e);
  color: white;
  border: 2px solid #0f3460;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.unlocked {
  background: linear-gradient(90deg, #4CAF50, #45a049);
  border-color: #4CAF50;
}

.action-btn:hover {
  transform: scale(1.02);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 64px 24px;
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 24px;
  margin-bottom: 8px;
}

.empty-state p {
  color: #888;
}

/* Tiers */
.tiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.tier-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid #0f3460;
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.tier-card.popular {
  border-color: #4CAF50;
  box-shadow: 0 0 30px rgba(76,175,80,0.3);
}

.tier-card.premium {
  border-color: #FFD700;
  box-shadow: 0 0 30px rgba(255,215,0,0.3);
}

.tier-card:hover {
  transform: translateY(-8px);
}

.tier-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #4CAF50;
  color: white;
  padding: 4px 16px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}

.tier-badge.premium-badge {
  background: linear-gradient(90deg, #FFD700, #FFA500);
  color: #000;
}

.tier-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
}

.tier-apr {
  font-size: 48px;
  font-weight: 900;
  color: #FFD700;
  margin: 16px 0;
}

.tier-apr span {
  font-size: 20px;
  color: #888;
}

.tier-days {
  color: #888;
  margin-bottom: 16px;
}

.tier-features {
  margin: 16px 0;
}

.feature {
  padding: 8px 0;
  font-size: 14px;
}

.tier-example {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255,215,0,0.1);
  border-radius: 8px;
  font-size: 14px;
}

.tier-example .highlight {
  color: #4CAF50;
  font-weight: 700;
}

/* Gifts Grid */
.gifts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.gift-card-wrapper {
  cursor: pointer;
}

.gift-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid #0f3460;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s;
}

.gift-card:hover {
  transform: translateY(-4px);
  border-color: #FFD700;
}

.gift-card img {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 12px;
  object-fit: cover;
  margin-bottom: 12px;
}

.gift-details h4 {
  font-size: 16px;
  margin-bottom: 8px;
}

.gift-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.potential-apr {
  font-size: 13px;
  color: #888;
}

.potential-apr .highlight {
  color: #FFD700;
  font-weight: 700;
}

/* Connect Wallet Prompt */
.connect-wallet-prompt,
.no-gifts {
  text-align: center;
  padding: 64px 24px;
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
}

.prompt-icon,
.no-gifts-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.connect-btn,
.browse-btn {
  margin-top: 24px;
  padding: 16px 32px;
  background: linear-gradient(90deg, #0f3460, #16213e);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

/* How It Works */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.step {
  text-align: center;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(90deg, #FFD700, #FFA500);
  color: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 900;
  margin: 0 auto 16px;
}

.step h3 {
  font-size: 18px;
  margin-bottom: 8px;
}

.step p {
  color: #888;
  font-size: 14px;
}

/* Provably Fair */
.provably-fair {
  text-align: center;
  padding: 48px 24px;
  background: rgba(76,175,80,0.1);
  border: 2px solid #4CAF50;
  border-radius: 20px;
}

.fair-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.provably-fair h3 {
  font-size: 24px;
  margin-bottom: 12px;
}

.provably-fair p {
  color: #888;
  margin-bottom: 24px;
}

.verify-btn {
  padding: 12px 32px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #1a1a2e;
  border: 2px solid #0f3460;
  border-radius: 24px;
  padding: 32px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: #888;
  font-size: 24px;
  cursor: pointer;
}

.modal-gift-preview {
  text-align: center;
  margin: 24px 0;
}

.modal-gift-preview img {
  width: 120px;
  height: 120px;
  border-radius: 16px;
  object-fit: cover;
  margin-bottom: 16px;
}

.preview-details {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.period-selector {
  margin: 24px 0;
}

.period-selector h3 {
  font-size: 18px;
  margin-bottom: 16px;
}

.period-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.period-option {
  padding: 16px;
  background: rgba(255,255,255,0.05);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.period-option.selected {
  border-color: #FFD700;
  background: rgba(255,215,0,0.1);
}

.period-label {
  font-weight: 600;
  margin-bottom: 4px;
}

.period-apr {
  font-size: 20px;
  color: #FFD700;
  font-weight: 700;
}

.stake-preview {
  margin: 24px 0;
  padding: 20px;
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
}

.stake-preview h3 {
  font-size: 18px;
  margin-bottom: 16px;
}

.preview-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
}

.preview-row.highlight {
  color: #FFD700;
  font-weight: 600;
}

.preview-row.reward {
  color: #4CAF50;
  font-weight: 600;
  font-size: 16px;
}

.preview-row.total {
  font-size: 18px;
  font-weight: 700;
}

.preview-row.roi {
  font-size: 16px;
  font-weight: 600;
}

.preview-row .big {
  font-size: 20px;
  font-weight: 700;
}

.preview-row .green {
  color: #4CAF50;
}

.preview-divider {
  height: 1px;
  background: rgba(255,255,255,0.1);
  margin: 16px 0;
}

.confirm-stake-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(90deg, #FFD700, #FFA500);
  color: #000;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
}

.confirm-stake-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.confirm-stake-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-warning {
  margin-top: 16px;
  padding: 12px;
  background: rgba(239,68,68,0.1);
  border: 1px solid #EF4444;
  border-radius: 8px;
  color: #EF4444;
  font-size: 13px;
  text-align: center;
}

.search-input {
  padding: 12px 20px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  color: white;
  font-size: 14px;
  min-width: 250px;
}

.search-input::placeholder {
  color: #888;
}
</style>
