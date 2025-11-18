// ============================================
// FICHIER : frontend/src/services/admin.js
// ============================================

import api from './api'

/**
 * Service API pour les fonctionnalités d'administration
 */
export const adminAPI = {
  /**
   * Créer un compte utilisateur pour un joueur
   * @param {number} playerId - ID du joueur
   * @param {string} role - Rôle de l'utilisateur (JOUEUR ou ADMINISTRATEUR)
   * @returns {Promise} Réponse avec l'email et le mot de passe temporaire
   */
  createAccount: (playerId, role = 'JOUEUR') => 
    api.post('/admin/accounts/create', { 
      player_id: playerId, 
      role 
    }),

  /**
   * Réinitialiser le mot de passe d'un utilisateur
   * @param {number} userId - ID de l'utilisateur
   * @returns {Promise} Réponse avec le nouveau mot de passe temporaire
   */
  resetPassword: (userId) => 
    api.post(`/admin/accounts/${userId}/reset-password`),

  /**
   * Récupérer la liste des joueurs sans compte
   * @returns {Promise} Liste des joueurs qui n'ont pas encore de compte
   */
  getPlayersWithoutAccount: () => 
    api.get('/admin/players-without-account'),

  /**
   * Récupérer la liste de tous les utilisateurs
   * @returns {Promise} Liste de tous les utilisateurs
   */
  getUsers: () => 
    api.get('/admin/users')
}
