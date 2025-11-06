// ============================================
// FICHIER : frontend/src/views/LoginPage.vue
// ============================================

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-lg shadow-2xl p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="text-6xl mb-4">🎾</div>
          <h1 class="text-3xl font-bold text-gray-800">Corpo Padel</h1>
          <p class="text-gray-600 mt-2">Connectez-vous à votre compte</p>
        </div>

        <!-- Formulaire -->
        <form @submit.prevent="handleLogin">
          <!-- Email -->
          <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="votre@email.com"
            />
          </div>

          <!-- Mot de passe -->
          <div class="mb-6">
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          <!-- Message d'erreur -->
          <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-700 text-sm">{{ errorMessage }}</p>
            <p v-if="attemptsRemaining !== null" class="text-red-600 text-sm font-semibold mt-1">
              Tentatives restantes : {{ attemptsRemaining }}
            </p>
            <p v-if="minutesRemaining !== null" class="text-red-600 text-sm font-semibold mt-1">
              Compte bloqué pendant {{ minutesRemaining }} minutes
            </p>
          </div>

          <!-- Bouton de connexion -->
          <button
            type="submit"
            :disabled="loading || minutesRemaining !== null"
            class="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Connexion...</span>
            <span v-else-if="minutesRemaining !== null">Compte bloqué</span>
            <span v-else>Se connecter</span>
          </button>
        </form>

        <!-- Informations de test -->
        <div class="mt-6 p-4 bg-blue-50 rounded-lg">
          <p class="text-xs text-gray-600 text-center">
            <strong>Compte de test :</strong><br>
            admin@padel.com / Admin@2025!
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const attemptsRemaining = ref(null)
const minutesRemaining = ref(null)

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''
  attemptsRemaining.value = null
  minutesRemaining.value = null

  const result = await authStore.login(email.value, password.value)

  if (result.success) {
    router.push('/')
  } else {
    errorMessage.value = result.error || 'Erreur de connexion'
    attemptsRemaining.value = result.attemptsRemaining ?? null
    minutesRemaining.value = result.minutesRemaining ?? null
  }

  loading.value = false
}
</script>