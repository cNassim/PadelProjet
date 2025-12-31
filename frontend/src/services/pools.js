import api from './api'

export const poolAPI = {
  list: () => api.get('/pools')
}

export default poolAPI
