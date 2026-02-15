<template>
  <div class="admin-panel">
    <!-- Header -->
    <div class="admin-header">
      <div class="header-left">
        <button class="back-btn" @click="$router.back()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
        </button>
        <h1>Admin Panel</h1>
      </div>
      <div class="header-badge">GAMBLING CONTROL</div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <!-- Stats Summary -->
    <div v-if="activeTab === 'dashboard'" class="section">
      <div class="stats-grid">
        <div class="stat-card green">
          <div class="stat-label">Today Profit</div>
          <div class="stat-value"><img src="/images/ton_symbol.svg" width="12" height="12" style="display:inline-block;vertical-align:middle;margin-right:2px" /> {{ stats.today?.profit?.toFixed(2) || '0.00' }}</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-label">Today Volume</div>
          <div class="stat-value"><img src="/images/ton_symbol.svg" width="12" height="12" style="display:inline-block;vertical-align:middle;margin-right:2px" /> {{ stats.today?.volume?.toFixed(2) || '0.00' }}</div>
        </div>
        <div class="stat-card yellow">
          <div class="stat-label">Today Bets</div>
          <div class="stat-value">{{ stats.today?.bets || 0 }}</div>
        </div>
        <div class="stat-card red">
          <div class="stat-label">Week Profit</div>
          <div class="stat-value"><img src="/images/ton_symbol.svg" width="12" height="12" style="display:inline-block;vertical-align:middle;margin-right:2px" /> {{ stats.week?.profit?.toFixed(2) || '0.00' }}</div>
        </div>
      </div>

      <!-- Quick Actions -->
      <h2 class="section-title">Quick Actions</h2>
      <div class="quick-actions">
        <button class="action-btn red" @click="emergencyStop">STOP ALL GAMES</button>
        <button class="action-btn green" @click="resumeAll">RESUME ALL</button>
        <button class="action-btn blue" @click="initDefaults">Init Default Settings</button>
      </div>
    </div>

    <!-- Game Settings -->
    <div v-if="activeTab === 'settings'" class="section">
      <h2 class="section-title">Game Settings</h2>
      <div v-for="game in gameSettings" :key="game.game_type" class="game-card">
        <div class="game-header">
          <span class="game-name">{{ game.game_type.toUpperCase() }}</span>
          <div class="game-status" :class="{ enabled: game.is_enabled, disabled: !game.is_enabled }">
            {{ game.is_enabled ? 'ON' : 'OFF' }}
          </div>
        </div>
        <div class="game-controls">
          <div class="control-row">
            <label>RTP %</label>
            <input type="number" v-model.number="game.rtp_percent" min="50" max="99" step="0.5"
              @change="updateSettings(game)" />
          </div>
          <div class="control-row">
            <label>House Edge %</label>
            <input type="number" v-model.number="game.house_edge_percent" min="1" max="50" step="0.5"
              @change="updateSettings(game)" />
          </div>
          <div class="control-row">
            <label>Min Bet</label>
            <input type="number" v-model.number="game.min_bet" min="0.01" step="0.1"
              @change="updateSettings(game)" />
          </div>
          <div class="control-row">
            <label>Max Bet</label>
            <input type="number" v-model.number="game.max_bet" min="1" step="1"
              @change="updateSettings(game)" />
          </div>
          <div class="control-row">
            <label>Rigged Mode</label>
            <div class="toggle-group">
              <button
                :class="['toggle-btn', { active: game.rigged_mode }]"
                @click="toggleRigged(game)"
              >
                {{ game.rigged_mode ? 'ON' : 'OFF' }}
              </button>
              <input v-if="game.rigged_mode" type="number" v-model.number="game.rigged_win_rate"
                min="0" max="1" step="0.05" placeholder="Win Rate"
                @change="updateSettings(game)" />
            </div>
          </div>
          <div class="control-row actions">
            <button class="btn-small green" @click="toggleGame(game, true)">Enable</button>
            <button class="btn-small red" @click="toggleGame(game, false)">Disable</button>
          </div>
        </div>
      </div>
    </div>

    <!-- User Targeting -->
    <div v-if="activeTab === 'targets'" class="section">
      <h2 class="section-title">User Targeting</h2>

      <!-- Create Target -->
      <div class="create-form">
        <h3>New Target</h3>
        <div class="form-grid">
          <div class="form-field">
            <label>User ID (Telegram)</label>
            <input v-model="newTarget.user_id" placeholder="123456789" />
          </div>
          <div class="form-field">
            <label>Game</label>
            <select v-model="newTarget.game_type">
              <option value="">All Games</option>
              <option v-for="g in gameTypes" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>
          <div class="form-field">
            <label>Mode</label>
            <select v-model="newTarget.target_mode">
              <option value="win">FORCE WIN</option>
              <option value="lose">FORCE LOSE</option>
              <option value="specific">SPECIFIC RESULT</option>
            </select>
          </div>
          <div class="form-field">
            <label>Forced Multiplier</label>
            <input type="number" v-model.number="newTarget.forced_multiplier" placeholder="2.5" />
          </div>
          <div class="form-field">
            <label>Custom RTP %</label>
            <input type="number" v-model.number="newTarget.custom_rtp" placeholder="97" />
          </div>
          <div class="form-field">
            <label>Uses (-1 = infinite)</label>
            <input type="number" v-model.number="newTarget.uses" />
          </div>
          <div class="form-field">
            <label>Active Hours</label>
            <input type="number" v-model.number="newTarget.active_hours" placeholder="24" />
          </div>
          <div class="form-field">
            <label>Note</label>
            <input v-model="newTarget.note" placeholder="Admin note..." />
          </div>
        </div>
        <button class="action-btn blue" @click="createTarget">Create Target</button>
      </div>

      <!-- Quick Actions -->
      <div class="quick-target-actions">
        <h3>Quick</h3>
        <div class="inline-form">
          <input v-model="quickUserId" placeholder="User ID" />
          <button class="btn-small green" @click="quickForceWin">Force Win</button>
          <button class="btn-small red" @click="quickForceLose">Force Lose</button>
        </div>
      </div>

      <!-- Active Targets -->
      <div class="targets-list">
        <h3>Active Targets ({{ targets.length }})</h3>
        <div v-for="t in targets" :key="t.id" class="target-item">
          <div class="target-info">
            <span class="target-user">{{ t.user_id }}</span>
            <span :class="['target-mode', t.target_mode]">{{ t.target_mode.toUpperCase() }}</span>
            <span class="target-game">{{ t.game_type || 'ALL' }}</span>
            <span class="target-uses">{{ t.uses_remaining === -1 ? '∞' : t.uses_remaining }} uses left</span>
          </div>
          <button class="btn-small red" @click="deleteTarget(t.id)">Delete</button>
        </div>
        <div v-if="targets.length === 0" class="empty">No active targets</div>
      </div>
    </div>

    <!-- Round Override -->
    <div v-if="activeTab === 'rounds'" class="section">
      <h2 class="section-title">Round Override</h2>

      <!-- Trading Crash Override -->
      <div class="override-card">
        <h3>Trading / Crash</h3>
        <p class="hint">Force next round crash point</p>
        <div class="inline-form">
          <input type="number" v-model.number="crashOverride" placeholder="1.50" min="1" step="0.01" />
          <button class="action-btn yellow" @click="forceCrash">Set Crash Point</button>
        </div>
      </div>

      <!-- Plinko Override -->
      <div class="override-card">
        <h3>Plinko</h3>
        <p class="hint">Force next drop landing slot</p>
        <div class="slot-grid">
          <button
            v-for="(label, i) in plinkoSlots"
            :key="i"
            :class="['slot-btn', { selected: selectedPlinkoSlot === i }]"
            @click="selectedPlinkoSlot = i"
          >
            {{ label }}
          </button>
        </div>
        <div class="inline-form">
          <input v-model="plinkoTargetUser" placeholder="Target User ID (optional)" />
          <button class="action-btn yellow" @click="forcePlinkoSlot">Set Slot</button>
        </div>
      </div>

      <!-- Pending Overrides -->
      <div class="overrides-list">
        <h3>Pending Overrides</h3>
        <div v-for="o in pendingOverrides" :key="o.id" class="override-item">
          <span class="override-game">{{ o.game_type }}</span>
          <span v-if="o.forced_crash_point" class="override-value">Crash: {{ o.forced_crash_point }}x</span>
          <span v-if="o.forced_slot !== null" class="override-value">Slot: {{ o.forced_slot }}</span>
          <span class="override-status">{{ o.is_used ? 'USED' : 'PENDING' }}</span>
        </div>
        <div v-if="pendingOverrides.length === 0" class="empty">No pending overrides</div>
      </div>
    </div>

    <!-- Audit Log -->
    <div v-if="activeTab === 'audit'" class="section">
      <h2 class="section-title">Audit Log</h2>
      <div v-for="log in auditLogs" :key="log.id" class="audit-item">
        <div class="audit-time">{{ formatTime(log.timestamp) }}</div>
        <div class="audit-action">{{ log.action }}</div>
        <div class="audit-desc">{{ log.description }}</div>
      </div>
      <div v-if="auditLogs.length === 0" class="empty">No audit logs</div>
    </div>

    <!-- Status Bar -->
    <div class="status-bar" v-if="statusMessage">
      <span :class="['status-text', statusType]">{{ statusMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const API_BASE = '/api'  // Proxy to admin backend

const activeTab = ref('dashboard')
const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'settings', label: 'Settings', icon: '⚙️' },
  { id: 'targets', label: 'Targets', icon: '🎯' },
  { id: 'rounds', label: 'Rounds', icon: '🎲' },
  { id: 'audit', label: 'Audit', icon: '📋' }
]

const gameTypes = ['plinko', 'trading', 'roulette', 'aviator', 'pvp', 'upgrade', 'lucky', 'gonka', 'ball_escape', 'rocket']
const plinkoSlots = ['💀', '🎁', '2.0x', '0.7x', '0.6x', '0.7x', '2.0x', '🎁', '💀']

// State
const stats = ref<any>({})
const gameSettings = ref<any[]>([])
const targets = ref<any[]>([])
const pendingOverrides = ref<any[]>([])
const auditLogs = ref<any[]>([])

// Forms
const newTarget = ref({
  user_id: '',
  game_type: '',
  target_mode: 'win',
  forced_multiplier: null as number | null,
  custom_rtp: null as number | null,
  uses: 1,
  active_hours: null as number | null,
  note: ''
})

const quickUserId = ref('')
const crashOverride = ref<number>(1.5)
const selectedPlinkoSlot = ref<number>(4)
const plinkoTargetUser = ref('')

// Status
const statusMessage = ref('')
const statusType = ref('success')

function showStatus(msg: string, type: string = 'success') {
  statusMessage.value = msg
  statusType.value = type
  setTimeout(() => { statusMessage.value = '' }, 3000)
}

function formatTime(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString('ru-RU')
}

// API calls
async function fetchJson(url: string, options?: RequestInit) {
  try {
    const res = await fetch(API_BASE + url, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    })
    return await res.json()
  } catch (e) {
    console.error('API error:', e)
    showStatus('API Error: ' + (e as Error).message, 'error')
    return null
  }
}

async function loadStats() {
  const data = await fetchJson('/admin/stats')
  if (data) stats.value = data
}

async function loadSettings() {
  const data = await fetchJson('/admin/settings')
  if (data) gameSettings.value = data.settings || []
}

async function loadTargets() {
  const data = await fetchJson('/admin/targets')
  if (data) targets.value = data.targets || []
}

async function loadOverrides() {
  // Load for all game types
  const trading = await fetchJson('/admin/rounds/trading')
  const plinko = await fetchJson('/admin/rounds/plinko')
  pendingOverrides.value = [
    ...(trading?.overrides || []),
    ...(plinko?.overrides || [])
  ]
}

async function loadAudit() {
  const data = await fetchJson('/admin/audit')
  if (data) auditLogs.value = data.logs || []
}

// Actions
async function updateSettings(game: any) {
  await fetchJson(`/admin/settings/${game.game_type}`, {
    method: 'PUT',
    body: JSON.stringify({
      rtp_percent: game.rtp_percent,
      house_edge_percent: game.house_edge_percent,
      min_bet: game.min_bet,
      max_bet: game.max_bet,
      rigged_mode: game.rigged_mode,
      rigged_win_rate: game.rigged_win_rate
    })
  })
  showStatus(`${game.game_type} settings updated`)
}

async function toggleGame(game: any, enabled: boolean) {
  await fetchJson(`/admin/settings/${game.game_type}/toggle?enabled=${enabled}`, { method: 'POST' })
  game.is_enabled = enabled
  showStatus(`${game.game_type} ${enabled ? 'enabled' : 'disabled'}`)
}

async function toggleRigged(game: any) {
  game.rigged_mode = !game.rigged_mode
  await updateSettings(game)
}

async function createTarget() {
  const body: any = {
    user_id: newTarget.value.user_id,
    target_mode: newTarget.value.target_mode,
    uses: newTarget.value.uses
  }
  if (newTarget.value.game_type) body.game_type = newTarget.value.game_type
  if (newTarget.value.forced_multiplier) body.forced_multiplier = newTarget.value.forced_multiplier
  if (newTarget.value.custom_rtp) body.custom_rtp = newTarget.value.custom_rtp
  if (newTarget.value.active_hours) body.active_hours = newTarget.value.active_hours
  if (newTarget.value.note) body.note = newTarget.value.note

  const data = await fetchJson('/admin/targets', { method: 'POST', body: JSON.stringify(body) })
  if (data?.status === 'ok') {
    showStatus('Target created')
    await loadTargets()
  }
}

async function quickForceWin() {
  if (!quickUserId.value) return
  await fetchJson('/admin/targets/force-win', {
    method: 'POST',
    body: JSON.stringify({ user_id: quickUserId.value, uses: 1 })
  })
  showStatus(`Force WIN for ${quickUserId.value}`)
  await loadTargets()
}

async function quickForceLose() {
  if (!quickUserId.value) return
  await fetchJson('/admin/targets/force-lose', {
    method: 'POST',
    body: JSON.stringify({ user_id: quickUserId.value, uses: 1 })
  })
  showStatus(`Force LOSE for ${quickUserId.value}`, 'error')
  await loadTargets()
}

async function deleteTarget(id: number) {
  await fetchJson(`/admin/targets/${id}`, { method: 'DELETE' })
  showStatus('Target deleted')
  await loadTargets()
}

async function forceCrash() {
  const data = await fetchJson('/admin/rounds/force-crash', {
    method: 'POST',
    body: JSON.stringify({ crash_point: crashOverride.value })
  })
  if (data?.status === 'ok') {
    showStatus(`Next crash at ${crashOverride.value}x`)
    await loadOverrides()
  }
}

async function forcePlinkoSlot() {
  const url = `/admin/rounds/force-plinko-slot?slot=${selectedPlinkoSlot.value}` +
    (plinkoTargetUser.value ? `&user_id=${plinkoTargetUser.value}` : '')
  const data = await fetchJson(url, { method: 'POST' })
  if (data?.status === 'ok') {
    showStatus(`Plinko → slot ${selectedPlinkoSlot.value} (${plinkoSlots[selectedPlinkoSlot.value]})`)
    await loadOverrides()
  }
}

async function emergencyStop() {
  await fetchJson('/admin/emergency/stop-all', { method: 'POST' })
  showStatus('ALL GAMES STOPPED', 'error')
  await loadSettings()
}

async function resumeAll() {
  await fetchJson('/admin/emergency/resume-all', { method: 'POST' })
  showStatus('All games resumed')
  await loadSettings()
}

async function initDefaults() {
  await fetchJson('/admin/settings/init-defaults', { method: 'POST' })
  showStatus('Default settings initialized')
  await loadSettings()
}

onMounted(async () => {
  await Promise.all([
    loadStats(),
    loadSettings(),
    loadTargets(),
    loadOverrides(),
    loadAudit()
  ])
})
</script>

<style scoped>
.admin-panel {
  min-height: 100vh;
  background: #000;
  color: #fff;
  padding: 0 0 80px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #1c1c1e;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 {
  font-size: 20px;
  font-weight: 700;
}

.back-btn {
  background: none;
  border: none;
  color: #fff;
  padding: 4px;
  cursor: pointer;
}

.header-badge {
  background: #ef4444;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 4px;
  letter-spacing: 1px;
}

/* Tabs */
.tabs {
  display: flex;
  overflow-x: auto;
  border-bottom: 1px solid #1c1c1e;
  padding: 0 8px;
  -webkit-overflow-scrolling: touch;
}

.tab {
  background: none;
  border: none;
  color: #666;
  padding: 12px 16px;
  font-size: 13px;
  white-space: nowrap;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab.active {
  color: #fff;
  border-bottom-color: #3b82f6;
}

.section {
  padding: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  margin: 16px 0 12px;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-card {
  background: #1c1c1e;
  border-radius: 12px;
  padding: 14px;
}

.stat-card.green { border-left: 3px solid #22c55e; }
.stat-card.blue { border-left: 3px solid #3b82f6; }
.stat-card.yellow { border-left: 3px solid #eab308; }
.stat-card.red { border-left: 3px solid #ef4444; }

.stat-label {
  font-size: 11px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  margin-top: 4px;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
}

.action-btn.red { background: #ef4444; }
.action-btn.green { background: #22c55e; }
.action-btn.blue { background: #3b82f6; }
.action-btn.yellow { background: #eab308; color: #000; }

/* Game Cards */
.game-card {
  background: #1c1c1e;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #2c2c2e;
}

.game-name {
  font-weight: 700;
  font-size: 14px;
}

.game-status {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
}

.game-status.enabled { background: #22c55e33; color: #22c55e; }
.game-status.disabled { background: #ef444433; color: #ef4444; }

.game-controls {
  padding: 12px 16px;
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.control-row label {
  font-size: 12px;
  color: #999;
}

.control-row input {
  width: 100px;
  background: #2c2c2e;
  border: 1px solid #3c3c3e;
  border-radius: 6px;
  color: #fff;
  padding: 6px 8px;
  font-size: 13px;
  text-align: right;
}

.control-row select {
  background: #2c2c2e;
  border: 1px solid #3c3c3e;
  border-radius: 6px;
  color: #fff;
  padding: 6px 8px;
  font-size: 13px;
}

.toggle-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.toggle-btn {
  padding: 4px 12px;
  border-radius: 12px;
  border: none;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  background: #2c2c2e;
  color: #666;
}

.toggle-btn.active {
  background: #ef4444;
  color: #fff;
}

.control-row.actions {
  margin-top: 8px;
  gap: 8px;
}

.btn-small {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
}

.btn-small.green { background: #22c55e; }
.btn-small.red { background: #ef4444; }
.btn-small.blue { background: #3b82f6; }

/* Forms */
.create-form, .override-card {
  background: #1c1c1e;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.create-form h3, .override-card h3 {
  font-size: 14px;
  margin-bottom: 12px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.form-field label {
  display: block;
  font-size: 11px;
  color: #888;
  margin-bottom: 4px;
}

.form-field input,
.form-field select {
  width: 100%;
  background: #2c2c2e;
  border: 1px solid #3c3c3e;
  border-radius: 6px;
  color: #fff;
  padding: 8px;
  font-size: 13px;
  box-sizing: border-box;
}

.hint {
  font-size: 12px;
  color: #666;
  margin-bottom: 12px;
}

.inline-form {
  display: flex;
  gap: 8px;
  align-items: center;
}

.inline-form input {
  flex: 1;
  background: #2c2c2e;
  border: 1px solid #3c3c3e;
  border-radius: 6px;
  color: #fff;
  padding: 8px;
  font-size: 13px;
}

/* Plinko Slots */
.slot-grid {
  display: grid;
  grid-template-columns: repeat(9, 1fr);
  gap: 4px;
  margin-bottom: 12px;
}

.slot-btn {
  background: #2c2c2e;
  border: 2px solid transparent;
  border-radius: 6px;
  color: #fff;
  padding: 8px 2px;
  font-size: 11px;
  cursor: pointer;
  text-align: center;
}

.slot-btn.selected {
  border-color: #eab308;
  background: #eab30833;
}

/* Targets List */
.quick-target-actions {
  background: #1c1c1e;
  border-radius: 12px;
  padding: 16px;
  margin: 12px 0;
}

.quick-target-actions h3 {
  font-size: 14px;
  margin-bottom: 8px;
}

.targets-list {
  margin-top: 12px;
}

.targets-list h3 {
  font-size: 14px;
  margin-bottom: 8px;
}

.target-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1c1c1e;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 6px;
}

.target-info {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.target-user {
  font-weight: 600;
  font-size: 13px;
}

.target-mode {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.target-mode.win { background: #22c55e33; color: #22c55e; }
.target-mode.lose { background: #ef444433; color: #ef4444; }
.target-mode.specific { background: #eab30833; color: #eab308; }

.target-game {
  font-size: 11px;
  color: #888;
}

.target-uses {
  font-size: 11px;
  color: #666;
}

/* Overrides */
.overrides-list {
  margin-top: 16px;
}

.overrides-list h3 {
  font-size: 14px;
  margin-bottom: 8px;
}

.override-item {
  display: flex;
  gap: 12px;
  align-items: center;
  background: #1c1c1e;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 6px;
}

.override-game {
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
}

.override-value {
  font-size: 13px;
  color: #eab308;
}

.override-status {
  font-size: 10px;
  color: #666;
  margin-left: auto;
}

/* Audit */
.audit-item {
  background: #1c1c1e;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 6px;
}

.audit-time {
  font-size: 10px;
  color: #666;
}

.audit-action {
  font-size: 12px;
  font-weight: 600;
  color: #3b82f6;
  margin: 2px 0;
}

.audit-desc {
  font-size: 12px;
  color: #999;
}

.empty {
  text-align: center;
  color: #444;
  padding: 24px;
  font-size: 13px;
}

/* Status Bar */
.status-bar {
  position: fixed;
  bottom: 80px;
  left: 16px;
  right: 16px;
  padding: 10px 16px;
  background: #1c1c1e;
  border-radius: 8px;
  text-align: center;
  z-index: 100;
}

.status-text.success { color: #22c55e; }
.status-text.error { color: #ef4444; }
</style>
