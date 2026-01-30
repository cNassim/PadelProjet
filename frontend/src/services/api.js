// ============================================
// FICHIER : frontend/src/services/api.js (CORRIGÉ)
// ============================================

import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // ✅ FIX: Ne PAS rediriger si c'est une erreur de login (401 sur /auth/login)
    // Laisser le composant Login gérer l'erreur 401
    const isLoginRoute = error.config?.url?.includes('/auth/login')
    
    if (error.response?.status === 401 && !isLoginRoute) {
      // Token expiré ou invalide (pas pendant le login)
      const authStore = useAuthStore()
      authStore.clearAuth()
      
      // Rediriger seulement si on n'est pas déjà sur /login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// API d'authentification
export const authAPI = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  logout: () => 
    api.post('/auth/logout'),
  
  changePassword: (currentPassword, newPassword, confirmPassword) =>
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
}

export default api