// ============================================
// FICHIER : frontend/src/views/HomePage.vue
// ============================================

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-4xl mx-auto p-8 text-center">
      <!-- Image ou logo -->
      <div class="mb-8">
        <div class="w-48 h-48 mx-auto bg-blue-600 rounded-full flex items-center justify-center text-white text-8xl shadow-2xl">
          🎾
        </div>
      </div>

      <!-- Message de bienvenue -->
      <h1 class="text-5xl font-bold text-gray-800 mb-4">
        Bienvenue sur Corpo Padel
      </h1>
      
      <p class="text-xl text-gray-600 mb-8">
        Gérez vos tournois corporatifs de padel en toute simplicité
      </p>

      <!-- Contenu conditionnel -->
      <div v-if="!authStore.isAuthenticated" class="space-y-4">
        <p class="text-gray-700">
          Connectez-vous pour accéder à votre planning, vos matchs et vos résultats
        </p>
        <router-link 
          to="/login" 
          class="inline-block px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
        >
          Se connecter
        </router-link>
      </div>

      <div v-else class="space-y-6">
        <p class="text-2xl text-gray-700">
          Bonjour <span class="font-semibold text-blue-600">{{ authStore.user?.email }}</span> ! 👋
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <router-link 
            to="/planning" 
            class="p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow"
          >
            <div class="text-4xl mb-2">📅</div>
            <h3 class="text-xl font-semibold">Planning</h3>
            <p class="text-gray-600 text-sm">Consultez vos prochains matchs</p>
          </router-link>

          <router-link 
            to="/matches" 
            class="p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow"
          >
            <div class="text-4xl mb-2">⚽</div>
            <h3 class="text-xl font-semibold">Matchs</h3>
            <p class="text-gray-600 text-sm">Suivez vos rencontres</p>
          </router-link>

          <router-link 
            to="/results" 
            class="p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow"
          >
            <div class="text-4xl mb-2">📊</div>
            <h3 class="text-xl font-semibold">Résultats</h3>
            <p class="text-gray-600 text-sm">Classement et statistiques</p>
          </router-link>
        </div>

        <div v-if="authStore.isAdmin" class="mt-8">
          <router-link 
            to="/admin" 
            class="inline-block px-8 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors shadow-lg"
          >
            🔧 Accéder à l'administration
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>