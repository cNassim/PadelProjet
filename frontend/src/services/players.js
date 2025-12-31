import api from './api' 


//CRUD
export const playerAPI = {
 
  list: () => api.get('/players/'),
  
  
  create: (data) => api.post('/players/', data),
  
  
  update: (id, data) => api.put(`/players/${id}`, data),
  
  
  delete: (id) => api.delete(`/players/${id}`)
}