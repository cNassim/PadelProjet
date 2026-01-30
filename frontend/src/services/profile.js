// ============================================
// FICHIER : frontend/src/services/profile.js
// ============================================

import api from './api'

/**
 * Service pour gérer le profil utilisateur
 */
export default {
  /**
   * Récupérer le profil de l'utilisateur connecté
   * @returns {Promise} Profil complet (user + player si joueur)
   */
  async getMyProfile() {
    const response = await api.get('/profile/me')
    return response.data
  },

  /**
   * Mettre à jour le profil
   * @param {Object} data - Données à mettre à jour
   * @param {string} data.first_name - Prénom
   * @param {string} data.last_name - Nom
   * @param {string} data.birth_date - Date de naissance (YYYY-MM-DD)
   * @param {string} data.email - Email
   * @returns {Promise} Profil mis à jour
   */
  async updateProfile(data) {
    const response = await api.put('/profile/me', data)
    return response.data
  },

  /**
   * Changer le mot de passe
   * @param {Object} data - Données du changement
   * @param {string} data.current_password - Mot de passe actuel
   * @param {string} data.new_password - Nouveau mot de passe
   * @param {string} data.confirm_password - Confirmation
   * @returns {Promise} Message de succès
   */
  async changePassword(data) {
    const response = await api.post('/profile/me/password', data)
    return response.data
  },

  /**
   * Upload photo de profil
   * @param {File} file - Fichier image
   * @returns {Promise} URL de la photo
   */
  /*async uploadPhoto(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/profile/me/photo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }*/
  async uploadPhoto(payload) {
    // payload doit être { photo_url: "data:image..." }
    // Axios détecte automatiquement qu'il s'agit de JSON, pas besoin de headers spécifiques
    const response = await api.post('/profile/me/photo', payload);
    return response.data;
  },

  /**
   * Supprimer la photo de profil
   * @returns {Promise} Message de succès
   */
  async deletePhoto() {
    const response = await api.delete('/profile/me/photo')
    return response.data
  }
}
