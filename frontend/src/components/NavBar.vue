// ============================================
// FICHIER : frontend/src/components/NavBar.vue
// ============================================

<template>
  <nav class="bg-blue-600 text-white shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <!-- Logo et titre -->
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-xl font-bold hover:text-blue-200">
            🎾 Corpo Padel
          </router-link>
        </div>

        <!-- Menu principal -->
        <div class="hidden md:flex space-x-4">
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
          <router-link 
            v-if="authStore.isAdmin" 
            to="/admin" 
            class="px-3 py-2 rounded hover:bg-blue-700"
          >
            Administration
          </router-link>
        </div>

        <!-- Menu utilisateur -->
        <div class="flex items-center space-x-4">
          <router-link to="/profile" class="px-3 py-2 rounded hover:bg-blue-700">
            👤 {{ authStore.user?.email }}
          </router-link>
          <button 
            @click="handleLogout" 
            class="px-4 py-2 bg-red-500 rounded hover:bg-red-600"
          >
            Déconnexion
          </button>
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