import api from './api'

export const playerAPI = {
  list: () => api.get('/players')
}

export default playerAPI
