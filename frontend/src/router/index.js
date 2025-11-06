// ============================================
// FICHIER : frontend/src/router/index.js
// ============================================

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
  }
  // TODO: Ajouter les autres routes (Planning, Matchs, Résultats, Admin, Profil)
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
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
