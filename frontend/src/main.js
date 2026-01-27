// ============================================
// FICHIER : frontend/src/main.js
// ============================================

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// On initialise la session avant que le routeur ne soit activé
const authStore = useAuthStore()
authStore.checkAuth()

app.use(router)
app.mount('#app')