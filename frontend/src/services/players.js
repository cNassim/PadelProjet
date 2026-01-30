
// ============================================
// FICHIER : frontend/src/services/players.js
// ============================================

import api from './api'

// CRUD + Actions spécifiques
export const playerAPI = {
  
  // Récupérer la liste des joueurs
  list: () => api.get('/players/'),
  
  // Créer un nouveau joueur
  create: (data) => api.post('/players/', data),
  
  // Mettre à jour un joueur existant
  update: (id, data) => api.put(`/players/${id}`, data),
  
  // Supprimer un joueur
  delete: (id) => api.delete(`/players/${id}`),

  /**
   * Mise à jour de la photo pour un joueur (Admin)
   * @param {number} id - L'ID du joueur
   * @param {string} base64String - La chaîne "data:image/..."
   */
  uploadPhoto: (id, base64String) => {
    // On envoie du JSON, plus de FormData
    return api.post(`/players/${id}/photo`, { photo_url: base64String })
  }
}