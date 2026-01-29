// ============================================
// FICHIER : frontend/src/services/teams.js
// ============================================

import api from './api'

export const teamAPI = {
  /**
   * Récupérer la liste des équipes
   * @param {Object} params - { pool_id, company }
   */
  async list(params = {}) {
    const response = await api.get('/teams', { params })
    return response.data
  },

  /**
   * Récupérer une équipe par ID
   */
  async get(id) {
    const response = await api.get(`/teams/${id}`)
    return response.data
  },

  /**
   * Créer une équipe
   */
  async create(data) {
    const response = await api.post('/teams', data)
    return response.data
  },

  /**
   * Mettre à jour une équipe
   */
  async update(id, data) {
    const response = await api.put(`/teams/${id}`, data)
    return response.data
  },

  /**
   * Supprimer une équipe
   */
  async remove(id) {
    await api.delete(`/teams/${id}`)
  }
}

export default teamAPI
