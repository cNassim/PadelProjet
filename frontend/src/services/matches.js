// ============================================
// FICHIER : frontend/src/services/matches.js
// ============================================

import api from './api'

export default {
  /**
   * Récupérer la liste des matchs
   * @param {Object} filters - { upcoming, team_id, status, my_matches }
   */
  async getMatches(filters = {}) {
    const response = await api.get('/matches', { params: filters })
    return response.data
  },

  /**
   * Mettre à jour un match (Score, statut...)
   * @param {Number} id 
   * @param {Object} data 
   */
  async updateMatch(id, data) {
    const response = await api.put(`/matches/${id}`, data)
    return response.data
  },

  /**
   * Supprimer un match
   * @param {Number} id 
   */
  async deleteMatch(id) {
    await api.delete(`/matches/${id}`)
  }
}