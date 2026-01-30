import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
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
  ],
})

export default router
