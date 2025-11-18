// ============================================
// FICHIER : frontend/src/views/AdminPage.vue
// ============================================

<template>
  <div class="min-h-screen px-4 py-12 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <div class="max-w-2xl mx-auto">
      <!-- En-tête centré -->
      <div class="mb-8 text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 mb-4 shadow-lg bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl">
          <span class="text-3xl"></span>
        </div>
        <h1 class="mb-2 text-3xl font-bold text-gray-900">Administration</h1>
        <p class="text-sm text-gray-600">Gestion des comptes utilisateurs</p>
      </div>

      <!-- Carte principale centrée -->
      <div class="overflow-hidden bg-white border border-gray-100 shadow-2xl rounded-3xl">
        <!-- Onglets -->
        <div class="px-6 py-3 bg-gray-50">
          <nav class="flex justify-center gap-2">
            <button
              @click="switchTab('create')"
              :class="[
                'px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                activeTab === 'create'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              ]"
            >
              <span>➕</span>
              <span>Créer un compte</span>
            </button>
            <button
              @click="switchTab('reset')"
              :class="[
                'px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                activeTab === 'reset'
                  ? 'bg-orange-600 text-white shadow-md'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              ]"
            >
              <span>🔄</span>
              <span>Réinitialiser</span>
            </button>
          </nav>
        </div>

        <div class="p-8">
          <!-- Onglet Créer un compte -->
          <div v-if="activeTab === 'create'">
            <h2 class="mb-6 text-xl font-semibold text-center text-gray-800">
              Créer un compte utilisateur
            </h2>
            
            <form @submit.prevent="handleCreateAccount" class="space-y-5">
              <!-- Sélection du joueur -->
              <div>
                <label for="playerId" class="block mb-2 text-sm font-semibold text-gray-700">
                  Joueur
                </label>
                <select
                  id="playerId"
                  v-model="createForm.playerId"
                  required
                  :disabled="loadingPlayers"
                  class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all text-sm"
                >
                  <option :value="null" disabled>
                    {{ loadingPlayers ? '⏳ Chargement...' : 'Sélectionner un joueur' }}
                  </option>
                  <option
                    v-for="player in playersWithoutAccount"
                    :key="player.id"
                    :value="player.id"
                  >
                    {{ player.full_name }} · {{ player.company }} · {{ player.license_number }}
                  </option>
                </select>
                <p class="mt-1.5 text-xs text-gray-500">
                  Seuls les joueurs sans compte apparaissent
                </p>
              </div>

              <!-- Sélection du rôle -->
              <div>
                <label for="role" class="block mb-2 text-sm font-semibold text-gray-700">
                  Rôle
                </label>
                <select
                  id="role"
                  v-model="createForm.role"
                  class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all text-sm"
                >
                  <option value="JOUEUR">Joueur</option>
                  <option value="ADMINISTRATEUR">Administrateur</option>
                </select>
              </div>

              <!-- Bouton de soumission -->
              <button
                type="submit"
                :disabled="createLoading || !createForm.playerId"
                class="w-full px-6 py-3 mt-6 font-medium text-white transition-all bg-blue-600 shadow-md rounded-xl hover:bg-blue-700 hover:shadow-lg disabled:bg-gray-300 disabled:cursor-not-allowed disabled:shadow-none"
              >
                <span v-if="createLoading" class="flex items-center justify-center gap-2">
                  <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Création...</span>
                </span>
                <span v-else>Créer le compte</span>
              </button>
            </form>

            <!-- Message de succès -->
            <transition name="fade">
              <div
                v-if="createSuccess"
                class="p-5 mt-6 border-l-4 border-green-500 rounded-lg bg-green-50"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0 text-2xl">✅</div>
                  <div class="flex-1">
                    <h3 class="mb-3 text-sm font-bold text-green-900">
                      {{ createResult.message }}
                    </h3>
                    <div class="space-y-2.5 text-sm">
                      <div class="flex items-center gap-2 text-green-800">
                        <span class="font-medium">Email :</span>
                        <span class="font-mono text-xs">{{ createResult.email }}</span>
                      </div>
                      <div>
                        <p class="mb-2 font-medium text-green-800">Mot de passe temporaire :</p>
                        <div class="relative">
                          <div class="p-3 font-mono text-xs text-gray-800 break-all bg-white border border-green-200 rounded-lg select-all">
                            {{ createResult.temporary_password }}
                          </div>
                          <button
                            @click="copyToClipboard(createResult.temporary_password)"
                            class="absolute top-2 right-2 px-2.5 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700 transition-colors"
                            title="Copier"
                          >
                            📋
                          </button>
                        </div>
                      </div>
                      <div class="flex items-start gap-2 p-2.5 bg-amber-50 border border-amber-200 rounded-lg">
                        <span class="text-amber-600">⚠️</span>
                        <p class="text-xs font-medium text-amber-800">
                          {{ createResult.warning }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </transition>

            <!-- Message d'erreur -->
            <transition name="fade">
              <div
                v-if="createError"
                class="p-4 mt-6 border-l-4 border-red-500 rounded-lg bg-red-50"
              >
                <div class="flex items-center gap-3">
                  <span class="text-xl">❌</span>
                  <div>
                    <h3 class="text-sm font-bold text-red-900">Erreur</h3>
                    <p class="mt-0.5 text-sm text-red-700">{{ createError }}</p>
                  </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- Onglet Réinitialiser mot de passe -->
          <div v-if="activeTab === 'reset'">
            <h2 class="mb-6 text-xl font-semibold text-center text-gray-800">
              Réinitialiser un mot de passe
            </h2>
            
            <form @submit.prevent="handleResetPassword" class="space-y-5">
              <!-- Sélection de l'utilisateur -->
              <div>
                <label for="userId" class="block mb-2 text-sm font-semibold text-gray-700">
                  Utilisateur
                </label>
                <select
                  id="userId"
                  v-model="resetForm.userId"
                  required
                  :disabled="loadingUsers"
                  class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 focus:bg-white transition-all text-sm"
                >
                  <option :value="null" disabled>
                    {{ loadingUsers ? '⏳ Chargement...' : 'Sélectionner un utilisateur' }}
                  </option>
                  <option
                    v-for="user in users"
                    :key="user.id"
                    :value="user.id"
                  >
                    {{ user.email }} · {{ user.role === 'ADMINISTRATEUR' ? 'Admin' : 'Joueur' }}
                    {{ !user.is_active ? ' · Inactif' : '' }}
                  </option>
                </select>
                <p class="mt-1.5 text-xs text-gray-500">
                  Vous ne pouvez pas réinitialiser le mot de passe d'un autre admin
                </p>
              </div>

              <!-- Bouton de soumission -->
              <button
                type="submit"
                :disabled="resetLoading || !resetForm.userId"
                class="w-full px-6 py-3 mt-6 font-medium text-white transition-all bg-orange-600 shadow-md rounded-xl hover:bg-orange-700 hover:shadow-lg disabled:bg-gray-300 disabled:cursor-not-allowed disabled:shadow-none"
              >
                <span v-if="resetLoading" class="flex items-center justify-center gap-2">
                  <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Réinitialisation...</span>
                </span>
                <span v-else>Réinitialiser le mot de passe</span>
              </button>
            </form>

            <!-- Message de succès -->
            <transition name="fade">
              <div
                v-if="resetSuccess"
                class="p-5 mt-6 border-l-4 border-green-500 rounded-lg bg-green-50"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0 text-2xl">✅</div>
                  <div class="flex-1">
                    <h3 class="mb-3 text-sm font-bold text-green-900">
                      {{ resetResult.message }}
                    </h3>
                    <div class="space-y-2.5 text-sm">
                      <div>
                        <p class="mb-2 font-medium text-green-800">Nouveau mot de passe temporaire :</p>
                        <div class="relative">
                          <div class="p-3 font-mono text-xs text-gray-800 break-all bg-white border border-green-200 rounded-lg select-all">
                            {{ resetResult.temporary_password }}
                          </div>
                          <button
                            @click="copyToClipboard(resetResult.temporary_password)"
                            class="absolute top-2 right-2 px-2.5 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700 transition-colors"
                            title="Copier"
                          >
                            📋
                          </button>
                        </div>
                      </div>
                      <div class="flex items-start gap-2 p-2.5 bg-amber-50 border border-amber-200 rounded-lg">
                        <span class="text-amber-600">⚠️</span>
                        <p class="text-xs font-medium text-amber-800">
                          {{ resetResult.warning }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </transition>

            <!-- Message d'erreur -->
            <transition name="fade">
              <div
                v-if="resetError"
                class="p-4 mt-6 border-l-4 border-red-500 rounded-lg bg-red-50"
              >
                <div class="flex items-center gap-3">
                  <span class="text-xl">❌</span>
                  <div>
                    <h3 class="text-sm font-bold text-red-900">Erreur</h3>
                    <p class="mt-0.5 text-sm text-red-700">{{ resetError }}</p>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '../services/admin'

// État des onglets
const activeTab = ref('create')

// Listes de données
const playersWithoutAccount = ref([])
const users = ref([])
const loadingPlayers = ref(false)
const loadingUsers = ref(false)

// Formulaire de création de compte
const createForm = ref({
  playerId: null,
  role: 'JOUEUR'
})
const createLoading = ref(false)
const createSuccess = ref(false)
const createError = ref(null)
const createResult = ref(null)

// Formulaire de réinitialisation de mot de passe
const resetForm = ref({
  userId: null
})
const resetLoading = ref(false)
const resetSuccess = ref(false)
const resetError = ref(null)
const resetResult = ref(null)

/**
 * Charger les joueurs sans compte
 */
const loadPlayersWithoutAccount = async () => {
  loadingPlayers.value = true
  try {
    const response = await adminAPI.getPlayersWithoutAccount()
    playersWithoutAccount.value = response.data.players
  } catch (err) {
    console.error('Erreur lors du chargement des joueurs:', err)
  } finally {
    loadingPlayers.value = false
  }
}

/**
 * Charger tous les utilisateurs
 */
const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await adminAPI.getUsers()
    users.value = response.data.users
  } catch (err) {
    console.error('Erreur lors du chargement des utilisateurs:', err)
  } finally {
    loadingUsers.value = false
  }
}

/**
 * Changer d'onglet et charger les données nécessaires
 */
const switchTab = (tab) => {
  activeTab.value = tab
  
  // Réinitialiser les messages
  createSuccess.value = false
  createError.value = null
  resetSuccess.value = false
  resetError.value = null
  
  // Charger les données selon l'onglet
  if (tab === 'create' && playersWithoutAccount.value.length === 0) {
    loadPlayersWithoutAccount()
  } else if (tab === 'reset' && users.value.length === 0) {
    loadUsers()
  }
}

/**
 * Créer un compte utilisateur
 */
const handleCreateAccount = async () => {
  createLoading.value = true
  createSuccess.value = false
  createError.value = null
  createResult.value = null

  try {
    const response = await adminAPI.createAccount(
      createForm.value.playerId,
      createForm.value.role
    )
    
    createResult.value = response.data
    createSuccess.value = true
    
    // Réinitialiser le formulaire
    createForm.value = {
      playerId: null,
      role: 'JOUEUR'
    }
    
    // Recharger la liste des joueurs sans compte
    await loadPlayersWithoutAccount()
  } catch (err) {
    createError.value = err.response?.data?.detail || 'Une erreur est survenue'
  } finally {
    createLoading.value = false
  }
}

/**
 * Réinitialiser un mot de passe
 */
const handleResetPassword = async () => {
  resetLoading.value = true
  resetSuccess.value = false
  resetError.value = null
  resetResult.value = null

  try {
    const response = await adminAPI.resetPassword(resetForm.value.userId)
    
    resetResult.value = response.data
    resetSuccess.value = true
    
    // Réinitialiser le formulaire
    resetForm.value = {
      userId: null
    }
  } catch (err) {
    resetError.value = err.response?.data?.detail || 'Une erreur est survenue'
  } finally {
    resetLoading.value = false
  }
}

/**
 * Copier du texte dans le presse-papier
 */
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('✅ Mot de passe copié dans le presse-papier !')
  } catch (err) {
    console.error('Erreur lors de la copie:', err)
    // Fallback pour les navigateurs plus anciens
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      console.log('✅ Mot de passe copié dans le presse-papier !')
    } catch (e) {
      console.log('❌ Impossible de copier le mot de passe')
    }
    document.body.removeChild(textarea)
  }
}

// Charger les données au montage du composant
onMounted(() => {
  loadPlayersWithoutAccount()
})
</script>

<style scoped>
/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Animations du spinner */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
