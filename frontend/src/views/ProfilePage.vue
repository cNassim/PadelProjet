// ============================================
// FICHIER : frontend/src/views/ProfilePage.vue
// ============================================

<template>
  <div class="min-h-screen px-4 py-12 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <div class="max-w-4xl mx-auto">
      <!-- En-tête -->
      <div class="mb-8 text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 mb-4 shadow-lg bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl">
          <span class="text-3xl">👤</span>
        </div>
        <h1 class="mb-2 text-3xl font-bold text-gray-900">Mon Profil</h1>
        <p class="text-sm text-gray-600">Gérez vos informations personnelles</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block w-12 h-12 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
        <p class="mt-4 text-gray-600">Chargement du profil...</p>
      </div>

      <!-- Contenu du profil -->
      <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Colonne gauche - Photo de profil (JOUEURS uniquement) -->
        <div v-if="profile?.player" class="lg:col-span-1">
          <div class="p-6 bg-white border border-gray-100 shadow-xl rounded-3xl">
            <h2 class="mb-4 text-lg font-semibold text-center text-gray-800">Photo de profil</h2>
            
            <!-- Photo actuelle -->
            <div class="mb-4">
              <div class="w-48 h-48 mx-auto overflow-hidden bg-gray-100 border-4 border-gray-200 rounded-full">
                <img 
                  v-if="profile.player.photo_url" 
                  :src="`http://localhost:8000${profile.player.photo_url}`" 
                  alt="Photo de profil"
                  class="object-cover w-full h-full"
                />
                <div v-else class="flex items-center justify-center w-full h-full text-6xl text-gray-400">
                  👤
                </div>
              </div>
            </div>

            <!-- Actions photo -->
            <div class="space-y-2">
              <label class="block">
                <input 
                  type="file" 
                  @change="handlePhotoSelect" 
                  accept="image/jpeg,image/png,image/jpg"
                  class="hidden"
                  ref="fileInput"
                />
                <button
                  @click="$refs.fileInput.click()"
                  :disabled="uploadingPhoto"
                  class="w-full px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-400 transition-all text-sm font-medium"
                >
                  {{ uploadingPhoto ? '⏳ Upload...' : '📸 Changer la photo' }}
                </button>
              </label>

              <button
                v-if="profile.player.photo_url"
                @click="handleDeletePhoto"
                :disabled="deletingPhoto"
                class="w-full px-4 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 disabled:bg-gray-400 transition-all text-sm font-medium"
              >
                {{ deletingPhoto ? '⏳ Suppression...' : '🗑️ Supprimer' }}
              </button>
            </div>

            <p class="mt-4 text-xs text-center text-gray-500">
              Formats : JPG, PNG • Max : 2MB
            </p>
          </div>
        </div>

        <!-- Colonne droite - Informations -->
        <div :class="profile?.player ? 'lg:col-span-2' : 'lg:col-span-3'">
          <div class="overflow-hidden bg-white border border-gray-100 shadow-xl rounded-3xl">
            <!-- Onglets -->
            <div class="px-6 py-3 bg-gray-50">
              <nav class="flex justify-center gap-2">
                <button
                  @click="activeTab = 'info'"
                  :class="[
                    'px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                    activeTab === 'info'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  ]"
                >
                  <span>📝</span>
                  <span>Informations</span>
                </button>
                <button
                  @click="activeTab = 'password'"
                  :class="[
                    'px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                    activeTab === 'password'
                      ? 'bg-orange-600 text-white shadow-md'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  ]"
                >
                  <span>🔒</span>
                  <span>Mot de passe</span>
                </button>
              </nav>
            </div>

            <div class="p-8">
              <!-- Onglet Informations -->
              <div v-if="activeTab === 'info'">
                <h2 class="mb-6 text-xl font-semibold text-gray-800">Mes informations</h2>
                
                <!-- Messages -->
                <div v-if="infoMessage" :class="[
                  'mb-4 p-4 rounded-xl border-l-4',
                  infoMessage.type === 'success' ? 'bg-green-50 border-green-500 text-green-700' : 'bg-red-50 border-red-500 text-red-700'
                ]">
                  {{ infoMessage.text }}
                </div>

                <form @submit.prevent="handleUpdateProfile" class="space-y-5">
                  <!-- Email -->
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Email</label>
                    <input
                      v-model="profileForm.email"
                      type="email"
                      required
                      class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all text-sm"
                    />
                  </div>

                  <!-- Champs joueurs uniquement -->
                  <template v-if="profile?.player">
                    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                      <!-- Prénom -->
                      <div>
                        <label class="block mb-2 text-sm font-semibold text-gray-700">Prénom</label>
                        <input
                          v-model="profileForm.first_name"
                          type="text"
                          class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all text-sm"
                        />
                      </div>

                      <!-- Nom -->
                      <div>
                        <label class="block mb-2 text-sm font-semibold text-gray-700">Nom</label>
                        <input
                          v-model="profileForm.last_name"
                          type="text"
                          class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all text-sm"
                        />
                      </div>
                    </div>

                    <!-- Date de naissance -->
                    <div>
                      <label class="block mb-2 text-sm font-semibold text-gray-700">Date de naissance</label>
                      <input
                        v-model="profileForm.birth_date"
                        type="date"
                        class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all text-sm"
                      />
                    </div>

                    <!-- Entreprise (lecture seule) -->
                    <div>
                      <label class="block mb-2 text-sm font-semibold text-gray-700">Entreprise</label>
                      <input
                        :value="profile.player.company"
                        type="text"
                        disabled
                        class="w-full px-4 py-2.5 bg-gray-100 border border-gray-200 rounded-xl text-sm text-gray-500 cursor-not-allowed"
                      />
                      <p class="mt-1 text-xs text-gray-500">Champ non modifiable</p>
                    </div>

                    <!-- Licence (lecture seule) -->
                    <div>
                      <label class="block mb-2 text-sm font-semibold text-gray-700">Numéro de licence</label>
                      <input
                        :value="profile.player.license_number"
                        type="text"
                        disabled
                        class="w-full px-4 py-2.5 bg-gray-100 border border-gray-200 rounded-xl text-sm text-gray-500 cursor-not-allowed"
                      />
                      <p class="mt-1 text-xs text-gray-500">Champ non modifiable</p>
                    </div>
                  </template>

                  <!-- Bouton -->
                  <button
                    type="submit"
                    :disabled="updatingProfile"
                    class="w-full px-6 py-3 font-medium text-white transition-all bg-blue-600 shadow-md rounded-xl hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {{ updatingProfile ? '⏳ Enregistrement...' : '💾 Enregistrer les modifications' }}
                  </button>
                </form>
              </div>

              <!-- Onglet Mot de passe -->
              <div v-if="activeTab === 'password'">
                <h2 class="mb-6 text-xl font-semibold text-gray-800">Changer mon mot de passe</h2>
                
                <!-- Messages -->
                <div v-if="passwordMessage" :class="[
                  'mb-4 p-4 rounded-xl border-l-4',
                  passwordMessage.type === 'success' ? 'bg-green-50 border-green-500 text-green-700' : 'bg-red-50 border-red-500 text-red-700'
                ]">
                  {{ passwordMessage.text }}
                </div>

                <form @submit.prevent="handleChangePassword" class="space-y-5">
                  <!-- Mot de passe actuel -->
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Mot de passe actuel</label>
                    <input
                      v-model="passwordForm.current_password"
                      type="password"
                      required
                      class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 focus:bg-white transition-all text-sm"
                    />
                  </div>

                  <!-- Nouveau mot de passe -->
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Nouveau mot de passe</label>
                    <input
                      v-model="passwordForm.new_password"
                      type="password"
                      required
                      minlength="8"
                      class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 focus:bg-white transition-all text-sm"
                    />
                    <p class="mt-1 text-xs text-gray-500">Minimum 8 caractères, 1 majuscule, 1 chiffre, 1 caractère spécial</p>
                  </div>

                  <!-- Confirmation -->
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Confirmer le nouveau mot de passe</label>
                    <input
                      v-model="passwordForm.confirm_password"
                      type="password"
                      required
                      minlength="8"
                      class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 focus:bg-white transition-all text-sm"
                    />
                  </div>

                  <!-- Bouton -->
                  <button
                    type="submit"
                    :disabled="changingPassword"
                    class="w-full px-6 py-3 font-medium text-white transition-all bg-orange-600 shadow-md rounded-xl hover:bg-orange-700 disabled:bg-gray-400"
                  >
                    {{ changingPassword ? '⏳ Modification...' : '🔒 Changer le mot de passe' }}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import profileService from '../services/profile'

// État
const loading = ref(true)
const profile = ref(null)
const activeTab = ref('info')

// Formulaire informations
const profileForm = reactive({
  email: '',
  first_name: '',
  last_name: '',
  birth_date: ''
})
const updatingProfile = ref(false)
const infoMessage = ref(null)

// Formulaire mot de passe
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const changingPassword = ref(false)
const passwordMessage = ref(null)

// Photo
const uploadingPhoto = ref(false)
const deletingPhoto = ref(false)
const fileInput = ref(null)

// Charger le profil
const loadProfile = async () => {
  try {
    loading.value = true
    profile.value = await profileService.getMyProfile()
    
    // Remplir le formulaire
    profileForm.email = profile.value.user.email
    if (profile.value.player) {
      profileForm.first_name = profile.value.player.first_name || ''
      profileForm.last_name = profile.value.player.last_name || ''
      profileForm.birth_date = profile.value.player.birth_date || ''
    }
  } catch (error) {
    console.error('Erreur chargement profil:', error)
  } finally {
    loading.value = false
  }
}
