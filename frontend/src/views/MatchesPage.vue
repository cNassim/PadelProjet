// ============================================
// FICHIER : frontend/src/views/MatchesPage.vue
// ============================================

<template>
  <div class="min-h-screen px-4 py-8 bg-gray-50">
    <div class="max-w-5xl mx-auto">
      
      <div class="flex flex-col md:flex-row justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-800 flex items-center gap-2">
            <span>⚽</span> Matchs
          </h1>
          <p class="text-gray-500 mt-1">Gérez les rencontres et consultez les scores</p>
        </div>

        <router-link 
          v-if="authStore.isAdmin"
          to="/planning" 
          class="mt-4 md:mt-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow flex items-center gap-2"
        >
          <span>➕</span> Planifier un match
        </router-link>
      </div>

      <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <label v-if="!authStore.isAdmin" class="flex items-center gap-2 cursor-pointer bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-100">
            <input type="checkbox" v-model="filters.my_matches" @change="loadMatches" class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500">
            <span class="text-sm font-medium text-blue-800">Mes matchs</span>
          </label>

          <label class="flex items-center gap-2 cursor-pointer px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50">
            <input type="checkbox" v-model="filters.upcoming" @change="loadMatches" class="w-4 h-4 text-green-600 rounded focus:ring-green-500">
            <span class="text-sm text-gray-700">À venir (30j)</span>
          </label>

          <select 
            v-if="authStore.isAdmin" 
            v-model="filters.status" 
            @change="loadMatches"
            class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option :value="null">Tous les statuts</option>
            <option value="A_VENIR">À venir</option>
            <option value="TERMINE">Terminé</option>
            <option value="ANNULE">Annulé</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block w-10 h-10 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
      </div>

      <div v-else-if="matches.length === 0" class="text-center py-12 bg-white rounded-xl shadow-sm">
        <div class="text-4xl mb-3">📭</div>
        <p class="text-gray-500">Aucun match trouvé pour ces critères.</p>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="match in matches" 
          :key="match.id" 
          class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
        >
          <div class="bg-gray-50 px-6 py-2 border-b flex justify-between items-center text-sm">
            <div class="flex items-center gap-2 text-gray-600">
              <span>📅 {{ formatDate(match.event.date) }}</span>
              <span>🕒 {{ match.event.time.slice(0, 5) }}</span>
              <span class="bg-gray-200 text-gray-700 px-2 py-0.5 rounded text-xs">Piste {{ match.court_number }}</span>
            </div>
            <span :class="getStatusClass(match.status)" class="px-2 py-0.5 rounded-full text-xs font-semibold uppercase">
              {{ formatStatus(match.status) }}
            </span>
          </div>

          <div class="p-6">
            <div class="flex flex-col md:flex-row items-center justify-between gap-6">
              
              <div class="flex-1 text-center md:text-right">
                <div class="font-bold text-lg text-gray-800">{{ match.team1.company }}</div>
                <div class="text-sm text-gray-500">
                  {{ match.team1.players.map(p => `${p.first_name} ${p.last_name}`).join(' & ') }}
                </div>
              </div>

              <div class="flex flex-col items-center justify-center min-w-[120px]">
                <div v-if="match.status === 'TERMINE'" class="text-2xl font-bold font-mono bg-slate-100 px-4 py-1 rounded-lg border">
                  <span :class="{'text-green-600': isWinner(match, 1), 'text-red-600': isWinner(match, 2)}">{{ match.score_team1 }}</span>
                  <span class="mx-2 text-gray-400">-</span>
                  <span :class="{'text-green-600': isWinner(match, 2), 'text-red-600': isWinner(match, 1)}">{{ match.score_team2 }}</span>
                </div>
                <div v-else class="text-xl font-bold text-gray-300">VS</div>
              </div>

              <div class="flex-1 text-center md:text-left">
                <div class="font-bold text-lg text-gray-800">{{ match.team2.company }}</div>
                <div class="text-sm text-gray-500">
                  {{ match.team2.players.map(p => `${p.first_name} ${p.last_name}`).join(' & ') }}
                </div>
              </div>

              <div v-if="authStore.isAdmin" class="flex md:flex-col gap-2 md:ml-4 border-t md:border-t-0 md:border-l pt-4 md:pt-0 md:pl-4 mt-4 md:mt-0 w-full md:w-auto justify-center">
                <button 
                  @click="openEditModal(match)" 
                  class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg text-sm font-medium flex items-center gap-1 justify-center"
                >
                  ✏️ Éditer
                </button>
                <button 
                  v-if="match.status === 'A_VENIR'"
                  @click="deleteMatch(match.id)" 
                  class="p-2 text-red-600 hover:bg-red-50 rounded-lg text-sm font-medium flex items-center gap-1 justify-center"
                >
                  🗑️ Suppr.
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="editingMatch" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md m-4 overflow-hidden">
        <div class="p-5 bg-blue-600 text-white flex justify-between items-center">
          <h3 class="font-bold text-lg">Mise à jour du match</h3>
          <button @click="editingMatch = null" class="text-white hover:text-blue-200">✕</button>
        </div>
        
        <form @submit.prevent="saveMatch" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Statut</label>
            <select v-model="editForm.status" class="w-full border rounded-lg p-2.5">
              <option value="A_VENIR">À venir</option>
              <option value="TERMINE">Terminé (Saisir scores)</option>
              <option value="ANNULE">Annulé</option>
            </select>
          </div>

          <div v-if="editForm.status === 'TERMINE'" class="space-y-3 bg-gray-50 p-4 rounded-lg border">
            <p class="text-xs text-gray-500 text-center mb-2">Format des sets : "6-4, 6-3"</p>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">{{ editingMatch.team1.company }}</label>
              <input v-model="editForm.score_team1" type="text" placeholder="Ex: 6-4, 6-3" class="w-full border rounded p-2 text-center font-mono">
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">{{ editingMatch.team2.company }}</label>
              <input v-model="editForm.score_team2" type="text" placeholder="Ex: 4-6, 3-6" class="w-full border rounded p-2 text-center font-mono">
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Numéro de Piste</label>
            <select v-model="editForm.court_number" class="w-full border rounded-lg p-2.5">
              <option v-for="n in 10" :key="n" :value="n">Piste {{ n }}</option>
            </select>
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button type="button" @click="editingMatch = null" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Annuler</button>
            <button type="submit" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import matchService from '../services/matches'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

// Etat
const matches = ref([])
const loading = ref(true)
const filters = reactive({
  upcoming: false,
  my_matches: !authStore.isAdmin, // Par défaut "mes matchs" pour les joueurs
  status: null
})

// Etat Edition
const editingMatch = ref(null)
const editForm = reactive({
  status: '',
  score_team1: '',
  score_team2: '',
  court_number: 1
})

// Chargement
const loadMatches = async () => {
  loading.value = true
  try {
    const params = {
      upcoming: filters.upcoming,
      my_matches: filters.my_matches,
      status: filters.status || undefined
    }
    const res = await matchService.getMatches(params)
    matches.value = res.matches
  } catch (err) {
    console.error("Erreur chargement matchs", err)
  } finally {
    loading.value = false
  }
}

// Actions
const deleteMatch = async (id) => {
  if (!confirm("Supprimer ce match ? Attention, si c'est le seul match du créneau, le créneau sera aussi supprimé.")) return
  try {
    await matchService.deleteMatch(id)
    loadMatches()
  } catch (err) {
    alert("Erreur: " + (err.response?.data?.detail || err.message))
  }
}

const openEditModal = (match) => {
  editingMatch.value = match
  editForm.status = match.status
  editForm.score_team1 = match.score_team1 || ''
  editForm.score_team2 = match.score_team2 || ''
  editForm.court_number = match.court_number
}

const saveMatch = async () => {
  try {
    // Validation basique score
    if (editForm.status === 'TERMINE' && (!editForm.score_team1 || !editForm.score_team2)) {
      alert("Veuillez saisir les scores pour un match terminé")
      return
    }

    await matchService.updateMatch(editingMatch.value.id, editForm)
    editingMatch.value = null
    loadMatches() // Rafraîchir
  } catch (err) {
    alert("Erreur mise à jour: " + (err.response?.data?.detail || err.message))
  }
}

// Helpers
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
}

const formatStatus = (status) => {
  const map = { 'A_VENIR': 'À venir', 'TERMINE': 'Terminé', 'ANNULE': 'Annulé' }
  return map[status] || status
}

const getStatusClass = (status) => {
  const map = { 
    'A_VENIR': 'bg-blue-100 text-blue-700', 
    'TERMINE': 'bg-green-100 text-green-700', 
    'ANNULE': 'bg-red-100 text-red-700' 
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

// Logique simpliste pour colorer le score (à améliorer avec parsing réel des sets)
const isWinner = (match, teamNum) => {
  if (!match.score_team1 || !match.score_team2) return false
  // Pour l'instant on ne parse pas vraiment "6-4, 6-3", c'est juste visuel
  return false 
}

onMounted(() => {
  loadMatches()
})
</script>