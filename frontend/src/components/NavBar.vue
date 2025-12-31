// ============================================
// FICHIER : frontend/src/components/NavBar.vue
// ============================================

<template>
  <nav class="text-white bg-blue-600 shadow-lg">
    <div class="container px-4 mx-auto">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-xl font-bold hover:text-blue-200">
            🎾 Corpo Padel
          </router-link>
        </div>

        <div class="hidden space-x-4 md:flex">
          <router-link to="/" class="px-3 py-2 rounded hover:bg-blue-700">
            Accueil
          </router-link>
          <router-link to="/planning" class="px-3 py-2 rounded hover:bg-blue-700">
            Planning
          </router-link>
          <router-link to="/matches" class="px-3 py-2 rounded hover:bg-blue-700">
            Matchs
          </router-link>
          <router-link to="/results" class="px-3 py-2 rounded hover:bg-blue-700">
            Résultats
          </router-link>
          
          <router-link to="/pools" class="px-3 py-2 rounded hover:bg-blue-700">
            Poules
          </router-link>

          <router-link 
            v-if="authStore.isAdmin" 
            to="/teams" 
            class="px-3 py-2 rounded hover:bg-blue-700"
          >
            Équipes
          </router-link>
          <router-link 
            v-if="authStore.isAdmin" 
            to="/admin" 
            class="px-3 py-2 rounded hover:bg-blue-700"
          >
            Administration
          </router-link>
        </div>

        <div v-if="authStore.isAuthenticated" class="flex items-center space-x-4">
          <router-link to="/profile" class="flex items-center gap-2 px-3 py-2 rounded hover:bg-blue-700">
            <span>👤</span>
            <span class="hidden lg:inline">{{ authStore.user?.email }}</span>
          </router-link>
          <button 
            @click="handleLogout" 
            class="px-4 py-2 text-sm font-medium bg-red-500 rounded hover:bg-red-600"
          >
            Déconnexion
          </button>
        </div>
        <div v-else class="flex items-center space-x-4">
          <router-link to="/login" class="px-4 py-2 font-medium text-blue-600 bg-white rounded hover:bg-blue-50">
            Connexion
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>