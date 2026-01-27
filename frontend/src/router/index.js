// ============================================
// FICHIER : frontend/src/router/index.js
// ============================================

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import AdminPage from '../views/AdminPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import MatchesPage from '../views/MatchesPage.vue'
import ResultsPage from '../views/ResultsPage.vue'
import PlanningPage from '../views/PlanningPage.vue'
import TeamManagement from '../views/TeamManagement.vue'
import PoolsPage from '../views/PoolsPage.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminPage,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: { requiresAuth: true }
  }, {
    path: '/matches',
    name: 'matches',
    component: MatchesPage,
    meta: { requiresAuth: true }
  }, {
    path: '/results',
    name: 'results',
    component: ResultsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/planning',
    name: 'planning',
    component: PlanningPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/teams',
    name: 'teams',
    component: TeamManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/pools',
    name: 'pools',
    component: PoolsPage,
    meta: { requiresAuth: true } // Accessible aux joueurs et admins
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard pour protéger les routes
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
