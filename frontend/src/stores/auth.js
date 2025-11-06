// ============================================
// FICHIER : frontend/src/stores/auth.js
// ============================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'ADMINISTRATEUR')

  function setAuth(authToken, userData) {
    token.value = authToken
    user.value = userData
    localStorage.setItem('token', authToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function checkAuth() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    
    try {
      const response = await authAPI.login(email, password)
      const { access_token, user: userData } = response.data
      
      setAuth(access_token, userData)
      return { success: true }
    } catch (err) {
      const errorData = err.response?.data?.detail
      
      if (typeof errorData === 'object') {
        error.value = errorData.message || 'Erreur de connexion'
        return { 
          success: false, 
          error: errorData.message,
          attemptsRemaining: errorData.attempts_remaining,
          minutesRemaining: errorData.minutes_remaining
        }
      } else {
        error.value = errorData || 'Erreur de connexion'
        return { success: false, error: error.value }
      }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authAPI.logout()
    } catch (err) {
      console.error('Erreur lors de la déconnexion:', err)
    } finally {
      clearAuth()
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    checkAuth
  }
})
