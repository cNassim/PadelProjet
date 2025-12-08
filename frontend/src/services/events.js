// ============================================
// FICHIER : frontend/src/services/events.js
// ============================================

import api from './api'

export default {
  /**
   * Récupérer les événements (avec filtres optionnels)
   * @param {Object} params - { start_date, end_date, month (YYYY-MM) }
   */
  async getEvents(params = {}) {
    const response = await api.get('/events', { params })
    return response.data
  },

  /**
   * Créer un événement (ADMIN seulement)
   * @param {Object} eventData 
   */
  async createEvent(eventData) {
    const response = await api.post('/events', eventData)
    return response.data
  },

  /**
   * Mettre à jour un événement (ADMIN seulement)
   */
  async updateEvent(id, eventData) {
    const response = await api.put(`/events/${id}`, eventData)
    return response.data
  },

  /**
   * Supprimer un événement (ADMIN seulement)
   */
  async deleteEvent(id) {
    await api.delete(`/events/${id}`)
  }
}