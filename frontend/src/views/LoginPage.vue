// ============================================
// FICHIER : frontend/src/views/LoginPage.vue
// ============================================

<template>
  <div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="w-full max-w-md">
      <div class="p-8 bg-white rounded-lg shadow-2xl">
        <!-- Header -->
        <div class="mb-8 text-center">
          <div class="mb-4 text-6xl">🎾</div>
          <h1 class="text-3xl font-bold text-gray-800">Corpo Padel</h1>
          <p class="mt-2 text-gray-600">Connectez-vous à votre compte</p>
        </div>

        <!-- Formulaire -->
        <form @submit.prevent="handleLogin">
          <!-- Email -->
          <div class="mb-4">
            <label for="email" class="block mb-2 text-sm font-medium text-gray-700">
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
            <label for="password" class="block mb-2 text-sm font-medium text-gray-700">
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
          <div v-if="errorMessage" class="p-3 mb-4 border border-red-200 rounded-lg bg-red-50">
            <p class="text-sm text-red-700">{{ errorMessage }}</p>
            <p v-if="attemptsRemaining !== null" class="mt-1 text-sm font-semibold text-red-600">
              Tentatives restantes : {{ attemptsRemaining }}
            </p>
            <p v-if="minutesRemaining !== null" class="mt-1 text-sm font-semibold text-red-600">
              Compte bloqué pendant {{ minutesRemaining }} minutes
            </p>
          </div>

          <!-- Bouton de connexion -->
          <button
            type="submit"
            :disabled="loading || minutesRemaining !== null"
            class="w-full py-3 font-semibold text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Connexion...</span>
            <span v-else-if="minutesRemaining !== null">Compte bloqué</span>
            <span v-else>Se connecter</span>
          </button>
        </form>

        <!-- Informations de test -->
        <div class="p-4 mt-6 rounded-lg bg-blue-50">
          <p class="text-xs text-center text-gray-600">
            <strong>Compte de test :</strong><br>
            admin@padel.com / Admin@2025!
          </p>
          <p class="text-xs text-center text-gray-600">
            <strong>Compte de test JOUEUR :</strong><br>
            pierre.dubois@datalab.com / I!H9"5"l}4R)m<^h
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