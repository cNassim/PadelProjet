// ============================================
// FICHIER : frontend/src/services/teams.js
// ============================================

import api from './api'

export default {
  /**
   * Récupérer la liste des équipes
   * @param {Object} params - { pool_id, company }
   */
  async getTeams(params = {}) {
    const response = await api.get('/teams', { params })
    return response.data
  },

  // Ces méthodes serviront plus tard pour la gestion des équipes
  async createTeam(data) {
    const response = await api.post('/teams', data)
    return response.data
  },

  async updateTeam(id, data) {
    const response = await api.put(`/teams/${id}`, data)
    return response.data
  },

  async deleteTeam(id) {
    await api.delete(`/teams/${id}`)
  }
}