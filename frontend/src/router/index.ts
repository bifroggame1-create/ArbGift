import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/market',
    },
    {
      path: '/market',
      name: 'market',
      component: () => import('../views/MarketView.vue'),
    },
    {
      path: '/market/gifts',
      redirect: '/market',
    },
    {
      path: '/gift/:id',
      name: 'gift-detail',
      component: () => import('../views/GiftDetailView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
    },
    {
      path: '/earn',
      name: 'earn',
      component: () => import('../views/EarnView.vue'),
    },
    {
      path: '/farming',
      redirect: '/earn',
    },
    {
      path: '/staking',
      name: 'staking',
      component: () => import('../views/StakingView.vue'),
    },
    {
      path: '/pvp',
      name: 'pvp',
      component: () => import('../views/PvPSelectorView.vue'),
    },
    {
      path: '/pvp/ice',
      name: 'pvp-ice',
      component: () => import('../views/PvPView.vue'),
    },
    {
      path: '/pvp/race',
      name: 'pvp-race',
      component: () => import('../views/PvPView.vue'),
      props: { mode: 'race' },
    },
    {
      path: '/solo',
      name: 'solo',
      component: () => import('../views/SoloView.vue'),
    },
    {
      path: '/inventory',
      name: 'inventory',
      component: () => import('../views/InventoryView.vue'),
    },
    {
      path: '/trading',
      name: 'trading',
      component: () => import('../views/TradingView.vue'),
    },
    {
      path: '/plinko',
      name: 'plinko',
      component: () => import('../views/PlinkoView.vue'),
    },
    {
      path: '/ball-escape',
      name: 'ball-escape',
      component: () => import('../views/BallEscapeView.vue'),
    },
    {
      path: '/gonka',
      name: 'gonka',
      component: () => import('../views/GonkaView.vue'),
    },
    // Redirects
    {
      path: '/topup',
      redirect: '/solo',
    },
    {
      path: '/shop',
      redirect: '/market',
    },
    // Game Routes
    {
      path: '/contracts',
      name: 'contracts',
      component: () => import('../views/ContractsView.vue'),
    },
    {
      path: '/upgrade',
      name: 'upgrade',
      component: () => import('../views/UpgradeView.vue'),
    },
    {
      path: '/aviator',
      name: 'aviator',
      component: () => import('../views/AviatorView.vue'),
    },
    {
      path: '/roulette',
      name: 'roulette',
      component: () => import('../views/RouletteView.vue'),
    },
    {
      path: '/stars',
      name: 'stars',
      component: () => import('../views/StarsView.vue'),
    },
    {
      path: '/rocket',
      name: 'rocket',
      component: () => import('../views/RocketView.vue'),
    },
    {
      path: '/lucky',
      name: 'lucky',
      component: () => import('../views/LuckyView.vue'),
    },
    // Admin Panel
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
    },
  ],
})

export default router
