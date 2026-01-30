// ============================================
// FICHIER : frontend/src/views/PlayerManagement.vue
// ============================================


<template>
  <div class="p-8 animate-fade-in">
    <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
      <h2 class="text-xl font-bold text-gray-800 uppercase tracking-wider">Gestion des joueurs</h2>
      <div class="flex items-center gap-3">
        <div class="relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Rechercher..." 
            class="pl-10 pr-4 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none w-48 transition-all focus:w-64"
          >
        </div>
<button @click="openCreateModal" class="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-blue-700 shadow-md transition-all">
  + Nouveau joueur
</button>

<div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
  <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in">
    <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
      <h3 class="text-xl font-bold text-gray-800">
        {{ isEditing ? 'Modifier le joueur' : 'Ajouter un joueur' }}
      </h3>
      <button @click="closeModal" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
    </div>
    
    <form @submit.prevent="isEditing ? handleUpdatePlayer() : handleCreatePlayer()" class="p-6 space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Prénom</label>
          <input v-model="newPlayer.first_name" type="text" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm">
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nom</label>
          <input v-model="newPlayer.last_name" type="text" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm">
        </div>
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Entreprise</label>
        <input v-model="newPlayer.company" type="text" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm">
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Numéro de licence</label>
        <input 
            v-model="newPlayer.license_number" 
            type="text" 
            :disabled="isEditing" 
            :class="[
            'w-full px-4 py-2 border rounded-xl text-sm outline-none transition-all',
            isEditing ? 'bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed' : 'bg-gray-50 border-gray-200 focus:ring-2 focus:ring-blue-500'
            ]"
            placeholder="Ex: L123456"
        >
      </div>

      <!--<div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Photo URL</label>
        <input v-model="newPlayer.photo_url" type="text"  class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm">
      </div>-->
      <div v-if="newPlayer.photo_url" class="w-10 h-10 rounded-full overflow-hidden border border-gray-200 bg-gray-50">
  <img :src="newPlayer.photo_url" class="w-full h-full object-cover">
</div>

<input type="file" ref="fileInput" @change="handleFileUpload" class="hidden" accept="image/*">

<button 
  type="button" 
  @click="$refs.fileInput.click()" 
  class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-xl text-xs font-bold hover:bg-gray-200"
>
  {{ newPlayer.photo_url ? '📷 Changer la photo' : '📁 Choisir une photo' }}
</button>



      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Date de naissance</label>
        <input v-model="newPlayer.birth_date" type="date":max="today" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm">
      </div>


      <div v-if="errorMessages && errorMessages.length > 0" class="p-4 bg-red-50 border-l-4 border-red-500 rounded-r-xl animate-shake">
  <div class="flex items-center mb-1">
    <span class="text-red-600 font-bold mr-2 text-xs">⚠️</span>
    <span class="text-[10px] font-bold text-red-800 uppercase tracking-widest">Erreur de validation</span>
  </div>
  <ul class="list-disc list-inside">
    <li v-for="(msg, index) in errorMessages" :key="index" class="text-xs text-red-700 font-medium">
      {{ msg }}
    </li>
  </ul>
</div>

      <div class="flex gap-3 mt-8">
        <button type="button" @click="closeModal" class="flex-1 py-3 bg-gray-100 text-gray-600 rounded-xl font-bold hover:bg-gray-200 transition-all text-sm">
          Annuler
        </button>
        <button type="submit" :disabled="createLoading" class="flex-1 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 shadow-lg transition-all text-sm disabled:bg-gray-300">>
            <span v-if="createLoading">Enregistrement...</span>
            <span v-else>{{ isEditing ? 'Mettre à jour' : 'Créer le joueur' }}</span>
        </button>
      </div>
    </form>
  </div>
</div>
      </div>
    </div>

    <div class="overflow-x-auto border border-gray-100 rounded-2xl shadow-sm">
      <table class="w-full text-left border-collapse">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase font-bold">
          <tr>
            <th class="px-6 py-4">Nom</th>
            <th class="px-6 py-4">Prénom</th>
            <th class="px-6 py-4">Entreprise</th>
            <th class="px-6 py-4 text-center">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="loading" class="text-center">
            <td colspan="4" class="py-10 text-gray-400 italic">Chargement des joueurs...</td>
          </tr>
          <tr v-for="player in filteredPlayers" :key="player.id" class="hover:bg-blue-50/50 transition-colors">
            <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ player.last_name }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ player.first_name }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ player.company }}</td>
            <td class="px-6 py-4">
              <div class="flex justify-center gap-3 text-lg">
                <button 
                @click="openEditModal(player)"
                class="hover:scale-125 transition-transform text-orange-500"
                >
                ✏️
                </button>
                <button @click="deletePlayer(player.id)" class="hover:scale-125 transition-transform text-red-500">❌</button>
              </div>
            </td>
          </tr>
          <tr v-if="!loading && filteredPlayers.length === 0">
            <td colspan="4" class="py-10 text-center text-gray-400 italic">Aucun joueur trouvé</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="mt-4 text-sm text-gray-500 font-medium">Total: {{ filteredPlayers.length }} joueurs</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { playerAPI } from '../services/players.js'

const searchQuery = ref('')
const allPlayers = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const errorMessage = ref(null)
const createLoading = ref(false)
const uploadingPhoto = ref(false)
const fileInput = ref(null)

const today = new Date().toISOString().split('T')[0];

// Récupération des données depuis la bd
const fetchAllPlayers = async () => {
  loading.value = true
  try {
    const response = await playerAPI.list()
    allPlayers.value = response.data.players 
  } catch (err) {
    console.error("Erreur lors du chargement des joueurs:", err)
  } finally {
    loading.value = false
  }
}

// Filtrage 
const filteredPlayers = computed(() => {
  if (!searchQuery.value) return allPlayers.value
  const q = searchQuery.value.toLowerCase()
  return allPlayers.value.filter(p => 
    p.last_name.toLowerCase().includes(q) || 
    p.first_name.toLowerCase().includes(q) || 
    p.company.toLowerCase().includes(q)
  )
})

const deletePlayer = async (id) => {
  if (confirm("Attention, cette action est irréversible. Voulez-vous vraiment supprimer ce joueur ?")) {
    try {
      await playerAPI.delete(id)
      await fetchAllPlayers() 
    } catch (err) {
      //alert("Erreur lors de la suppression")
      const errorMessage = err.response?.data?.detail 
                        || "Une erreur inconnue est survenue";

      //Msg du back
      alert(errorMessage);
      
      console.error("Détails de l'erreur:", err.response?.data);
    }
  }
}

onMounted(() => {
  fetchAllPlayers()
})


// Objet pour le formulaire
const newPlayer = ref({
  id: null,
  first_name: '',
  last_name: '',
  company: '',
  license_number: '',
  birth_date: '',
  email: null,
  photo_url: null
})

// --- OUVERTURE : CRÉATION ---
const openCreateModal = () => {
  isEditing.value = false
  errorMessage.value = null
  // Reset complet du formulaire
  newPlayer.value = { 
    id: null, first_name: '', last_name: '', company: '', 
    license_number: '', birth_date: '', email: null, photo_url: null 
  }
  showModal.value = true
}

// --- OUVERTURE : ÉDITION ---
const openEditModal = (player) => {
  isEditing.value = true
  errorMessage.value = null
  // Copie des données du joueur dans le formulaire
  newPlayer.value = { ...player } 
  showModal.value = true
}

// --- FERMETURE ---
const closeModal = () => {
  showModal.value = false
  errorMessages.value = [];
  errorMessage.value = null
  isEditing.value = false
}

// --- LOGIQUE : CRÉER ---
const handleCreatePlayer = async () => {
  createLoading.value = true
  errorMessage.value = null
  try {
    await playerAPI.create(newPlayer.value)
    closeModal()
    fetchAllPlayers() // Rfaraichir la  liste
  } catch (err) {
    handleError(err)
  } finally {
    createLoading.value = false
  }
}

// --- LOGIQUE : MODIFIER ---
const handleUpdatePlayer = async () => {
  createLoading.value = true
  errorMessage.value = null
  try {
   //on ne modifie ni licence ni mail)
    const payload = {
      first_name: newPlayer.value.first_name,
      last_name: newPlayer.value.last_name,
      company: newPlayer.value.company,
      birth_date: newPlayer.value.birth_date,
      photo_url: newPlayer.value.photo_url
    }
    await playerAPI.update(newPlayer.value.id, payload)
    closeModal()
    fetchAllPlayers()
  } catch (err) {
    handleError(err)
  } finally {
    createLoading.value = false
  }
}

const errorMessages = ref([]) // On passe à un tableau 

const handleError = (err) => {
  errorMessages.value = [] // On vide les erreurs précédentes
  
  if (err.response?.data?.detail) {
    const details = err.response.data.detail
    
    if (Array.isArray(details)) {
      // On extrait chaque message (soit votre ValueError, soit le message Pydantic par défaut)
      errorMessages.value = details.map(e => {
        //traduction pour user
        const fieldMap = {
          first_name: 'Prénom',
          last_name: 'Nom',
          company: 'Entreprise',
          license_number: 'Licence',
          birth_date: 'Date de naissance'
        }
        let msg = e.msg.replace('Value error, ', '');
        if (msg.includes("at least 2 characters")) msg = "doit contenir au moins 2 caractères.";
        const fieldName = fieldMap[e.loc[1]] || e.loc[1]
        return `${fieldName} : ${msg}`
      })
    } else {
      errorMessages.value = [details]
    }
  } else {
    errorMessages.value = ["Une erreur inattendue est survenue."]
  }
}
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Limite de sécurité (le base64 alourdit la DB, évite les fichiers de + de 1Mo)
  if (file.size > 1024 * 1024) {
    alert("Photo trop lourde pour la base de données (max 1Mo)")
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    // Stocke la chaîne "data:image/jpeg;base64,..."
    newPlayer.value.photo_url = e.target.result
  }
  reader.readAsDataURL(file)
}
</script>