// ============================================
// FICHIER : frontend/src/services/api.js
// ============================================

import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
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
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
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