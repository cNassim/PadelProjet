// ============================================
// FICHIER : frontend/src/services/results.js
// ============================================

import api from './api'

export default {
  /**
   * Obtenir l'historique et les stats du joueur connecté
   */
  async getMyResults() {
    const response = await api.get('/results/my-results')
    return response.data
  },

  /**
   * Obtenir le classement général
   */
  async getRankings() {
    const response = await api.get('/results/rankings')
    return response.data
  }
}