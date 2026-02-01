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
      path: '/gift/:id',
      name: 'gift-detail',
      component: () => import('../views/GiftDetailView.vue'),
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('../views/SearchView.vue'),
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('../views/FavoritesView.vue'),
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
      path: '/pvp',
      name: 'pvp',
      component: () => import('../views/PvPView.vue'),
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
      path: '/shop',
      name: 'shop',
      component: () => import('../views/ShopView.vue'),
    },
    {
      path: '/lucky',
      name: 'lucky',
      component: () => import('../views/LuckyView.vue'),
    },
    {
      path: '/roll',
      name: 'roll',
      component: () => import('../views/RollView.vue'),
    },
    // Gaming Hub
    {
      path: '/topup',
      name: 'topup',
      component: () => import('../views/TopUpView.vue'),
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
    // Solo Games
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
      path: '/gonka',
      name: 'gonka',
      component: () => import('../views/GonkaView.vue'),
    },
    {
      path: '/ball-escape',
      name: 'ball-escape',
      component: () => import('../views/BallEscapeView.vue'),
    },
    {
      path: '/rocket',
      name: 'rocket',
      component: () => import('../views/RocketView.vue'),
    },
  ],
})

export default router
