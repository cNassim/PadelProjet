import api from './api'

const teamService = {
  // Récupérer les équipes
  getTeams() {
    return api.get('/teams').then(response => response.data)
  },

  // --- Méthodes compatibles TeamManagement ---
  list() {
    return this.getTeams()
  },
  create(data) {
    return api.post('/teams', data).then(response => response.data)
  },
  update(id, data) {
    return api.put(`/teams/${id}`, data).then(response => response.data)
  },
  remove(id) {
    return api.delete(`/teams/${id}`)
  }
}

export const teamAPI = teamService
export default teamService