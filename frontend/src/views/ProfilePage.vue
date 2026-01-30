// ============================================
// FICHIER : frontend/src/views/ProfilePage.vue
// ============================================

<template>
  <div class="min-h-screen px-4 py-12 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <div class="max-w-4xl mx-auto">
      <div class="mb-8 text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 mb-4 shadow-lg bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl">
          <span class="text-3xl">👤</span>
        </div>
        <h1 class="mb-2 text-3xl font-bold text-gray-900">Mon Profil</h1>
        <p class="text-sm text-gray-600">Gérez vos informations personnelles</p>
      </div>

      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block w-12 h-12 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
        <p class="mt-4 text-gray-600">Chargement du profil...</p>
      </div>

      <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div v-if="profile?.player" class="lg:col-span-1">
          <div class="p-6 bg-white border border-gray-100 shadow-xl rounded-3xl">
            <h2 class="mb-4 text-lg font-semibold text-center text-gray-800">Photo de profil</h2>
            
            <div class="mb-4">
              <div class="w-48 h-48 mx-auto overflow-hidden bg-gray-100 border-4 border-gray-200 rounded-full">
                <!--<img 
                  v-if="profile.player.photo_url" 
                  :src="`http://localhost:8000${profile.player.photo_url}`" 
                  alt="Photo de profil"
                  class="object-cover w-full h-full"
                />-->
                <img 
                  v-if="profile.player.photo_url" 
                  :src="profile.player.photo_url" 
                  alt="Photo de profil"
                  class="object-cover w-full h-full"
                />
                <div v-else class="flex items-center justify-center w-full h-full text-6xl text-gray-400">
                  👤
                </div>
              </div>
            </div>

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
            <div class="flex flex-col items-center space-y-4">
          </div>
        </div>
      </div>
        <div :class="profile?.player ? 'lg:col-span-2' : 'lg:col-span-3'">
          <div class="overflow-hidden bg-white border border-gray-100 shadow-xl rounded-3xl">
            <div class="px-6 py-3 bg-gray-50">
              <nav class="flex justify-center gap-2">
                <button
                  @click="activeTab = 'info'"
                  :class="[
                    'px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                    activeTab === 'info' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-gray-100'
                  ]"
                >
                  <span>📝</span><span>Informations</span>
                </button>
                <button
                  @click="activeTab = 'password'"
                  :class="[
                    'px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                    activeTab === 'password' ? 'bg-orange-600 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-gray-100'
                  ]"
                >
                  <span>🔒</span><span>Mot de passe</span>
                </button>
              </nav>
            </div>

            <div class="p-8">
              <div v-if="activeTab === 'info'">
                <h2 class="mb-6 text-xl font-semibold text-gray-800">Mes informations</h2>
                
                <div v-if="infoMessage" :class="[
                  'mb-4 p-4 rounded-xl border-l-4',
                  infoMessage.type === 'success' ? 'bg-green-50 border-green-500 text-green-700' : 'bg-red-50 border-red-500 text-red-700'
                ]">
                  {{ infoMessage.text }}
                </div>

                <form @submit.prevent="handleUpdateProfile" class="space-y-5">
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Email</label>
                    <input v-model="profileForm.email" type="email" required class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-sm" />
                  </div>

                  <template v-if="profile?.player">
                    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                      <div>
                        <label class="block mb-2 text-sm font-semibold text-gray-700">Prénom</label>
                        <input v-model="profileForm.first_name" type="text" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm" />
                      </div>
                      <div>
                        <label class="block mb-2 text-sm font-semibold text-gray-700">Nom</label>
                        <input v-model="profileForm.last_name" type="text" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm" />
                      </div>
                    </div>
                    <div>
                      <label class="block mb-2 text-sm font-semibold text-gray-700">Date de naissance</label>
                      <input v-model="profileForm.birth_date" type="date" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm" />
                    </div>
                  </template>

                  <button
                    type="submit"
                    :disabled="updatingProfile"
                    class="w-full px-6 py-3 font-medium text-white transition-all bg-blue-600 shadow-md rounded-xl hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {{ updatingProfile ? '⏳ Enregistrement...' : '💾 Enregistrer les modifications' }}
                  </button>
                </form>
              </div>

              <div v-if="activeTab === 'password'">
                <h2 class="mb-6 text-xl font-semibold text-gray-800">Changer mon mot de passe</h2>
                
                <div v-if="passwordMessage" :class="[
                  'mb-4 p-4 rounded-xl border-l-4',
                  passwordMessage.type === 'success' ? 'bg-green-50 border-green-500 text-green-700' : 'bg-red-50 border-red-500 text-red-700'
                ]">
                  {{ passwordMessage.text }}
                </div>

                <form @submit.prevent="handleChangePassword" class="space-y-5">
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Mot de passe actuel</label>
                    <input v-model="passwordForm.current_password" type="password" required class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 text-sm" />
                  </div>
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Nouveau mot de passe</label>
                    <input v-model="passwordForm.new_password" type="password" required minlength="8" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 text-sm" />
                    <p class="mt-1 text-xs text-gray-500">Min. 8 caractères, 1 majuscule, 1 chiffre, 1 spécial</p>
                  </div>
                  <div>
                    <label class="block mb-2 text-sm font-semibold text-gray-700">Confirmer le nouveau mot de passe</label>
                    <input v-model="passwordForm.confirm_password" type="password" required minlength="8" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 text-sm" />
                  </div>

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

// --- UTILITAIRES ---
const formatError = (error) => {
  const data = error.response?.data
  const detail = data?.detail

  const extractMessages = (items) => {
    if (!Array.isArray(items)) return null
    const messages = items
      .map((item) => item?.msg)
      .filter(Boolean)
    if (messages.length === 0) return null
    return messages.join(' | ')
  }

  const detailMessages = extractMessages(detail)
  if (detailMessages) return detailMessages

  const rootMessages = extractMessages(data)
  if (rootMessages) return rootMessages

  return detail || data?.message || 'Une erreur est survenue'
}

// --- ÉTAT ---
const loading = ref(true)
const profile = ref(null)
const activeTab = ref('info')

const profileForm = reactive({ email: '', first_name: '', last_name: '', birth_date: '' })
const updatingProfile = ref(false)
const infoMessage = ref(null)

const passwordForm = reactive({ current_password: '', new_password: '', confirm_password: '' })
const changingPassword = ref(false)
const passwordMessage = ref(null)
const uploadingPhoto = ref(false)
const deletingPhoto = ref(false)
const fileInput = ref(null)

// --- ACTIONS ---
const loadProfile = async () => {
  try {
    loading.value = true
    profile.value = await profileService.getMyProfile()
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

const handleUpdateProfile = async () => {
  try {
    updatingProfile.value = true
    infoMessage.value = null
    const data = { email: profileForm.email }
    if (profile.value.player) {
      data.first_name = profileForm.first_name
      data.last_name = profileForm.last_name
      data.birth_date = profileForm.birth_date
    }
    const result = await profileService.updateProfile(data)
    profile.value = result.profile
    infoMessage.value = { type: 'success', text: '✅ Profil mis à jour avec succès' }
  } catch (error) {
    infoMessage.value = { type: 'error', text: formatError(error) }
  } finally {
    updatingProfile.value = false
  }
}

const handleChangePassword = async () => {
  try {
    changingPassword.value = true
    passwordMessage.value = null
    await profileService.changePassword(passwordForm)
    passwordMessage.value = { type: 'success', text: '✅ Mot de passe changé avec succès' }
    passwordForm.current_password = ''; passwordForm.new_password = ''; passwordForm.confirm_password = ''
  } catch (error) {
    passwordMessage.value = { type: 'error', text: formatError(error) }
  } finally {
    changingPassword.value = false
  }
}

const handlePhotoSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      uploadingPhoto.value = true
      infoMessage.value = null 
      
      const base64Image = e.target.result
      
      // Envoi au serveur
      await profileService.uploadPhoto({ photo_url: base64Image })
      
      // MISE À JOUR LOCALE IMMÉDIATE
      if (profile.value && profile.value.player) {
        profile.value.player.photo_url = base64Image
      }
      await loadProfile() 
      
      infoMessage.value = { type: 'success', text: '✅ Photo mise à jour !' }
    } catch (error) {
      console.error("Erreur détaillée:", error.response?.data)
      infoMessage.value = { type: 'error', text: "Erreur lors de l'enregistrement" }
    } finally {
      uploadingPhoto.value = false
      event.target.value = '' 
    }
  }
  reader.readAsDataURL(file)
}

const handleDeletePhoto = async () => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer votre photo ?')) return
  try {
    deletingPhoto.value = true
    await profileService.deletePhoto()
    await loadProfile()
    infoMessage.value = { type: 'success', text: '✅ Photo supprimée avec succès' }
  } catch (error) {
    infoMessage.value = { type: 'error', text: formatError(error) }
  } finally {
    deletingPhoto.value = false
  }
}

onMounted(loadProfile)
</script>