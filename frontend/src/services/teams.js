import api from './api'

export const teamAPI = {
  list: () => api.get('/teams'),
  get: (id) => api.get(`/teams/${id}`),
  create: (payload) => api.post('/teams', payload),
  update: (id, payload) => api.put(`/teams/${id}`, payload),
  remove: (id) => api.delete(`/teams/${id}`)
}

export default teamAPI
