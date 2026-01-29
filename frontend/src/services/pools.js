// ============================================
// FICHIER : frontend/src/services/pools.js
// ============================================
import api from './api'

export const poolAPI = {
  /**
   * Récupérer toutes les poules
   */
  async list() {
    const response = await api.get('/pools')
    // Gestion robuste : retourne le tableau directement ou l'objet qui le contient
    return response.data?.pools || response.data || []
  },
  async update(id, data) {
    const response = await api.put(`/pools/${id}`, data)
    return response.data
  },
  /**
   * Créer une poule
   */
  async create(data) {
    const response = await api.post('/pools', data)
    return response.data
  },

  /**
   * Supprimer une poule
   */
  async remove(id) {
    await api.delete(`/pools/${id}`)
  }
}

// Alias pour compatibilité avec ton PoolsPage.vue actuel (si tu as utilisé getPools/deletePool)
export default {
  ...poolAPI,
  getPools: poolAPI.list,
  createPool: poolAPI.create,
  updatePool: poolAPI.update,
  deletePool: poolAPI.remove
}