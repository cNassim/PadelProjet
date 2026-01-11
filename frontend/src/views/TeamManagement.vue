<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-7xl">
      <!-- Header -->
      <div class="bg-white rounded-2xl shadow-lg border border-gray-100 mb-6">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between p-6 border-b">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Gestion des Équipes</h1>
            <p class="text-sm text-gray-500 mt-1">Créez et gérez les équipes du tournoi</p>
          </div>
          <button
            @click="openCreateModal"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl shadow-md hover:bg-blue-700 transition-all hover:shadow-lg"
          >
            <span class="text-xl">➕</span>
            <span class="font-medium">Créer une équipe</span>
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-2xl shadow-lg p-12 text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
        <p class="mt-4 text-gray-600">Chargement des équipes...</p>
      </div>

      <!-- Teams Table -->
      <div v-else class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div v-if="teams.length === 0" class="p-12 text-center">
          <div class="text-6xl mb-4">🗂️</div>
          <p class="text-gray-500 text-lg">Aucune équipe pour l'instant</p>
          <p class="text-gray-400 text-sm mt-2">Cliquez sur "Créer une équipe" pour commencer</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="bg-gray-50 text-gray-600 text-sm border-b">
                <th class="px-6 py-4 text-left font-semibold">Company</th>
                <th class="px-6 py-4 text-left font-semibold">Pool</th>
                <th class="px-6 py-4 text-left font-semibold">Joueurs</th>
                <th class="px-6 py-4 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="team in teams"
                :key="team.id"
                class="border-b hover:bg-gray-50 transition-colors"
              >
                <td class="px-6 py-4 font-medium text-gray-900">{{ team.company }}</td>
                <td class="px-6 py-4">
                  <span
                    v-if="team.pool || team.pool_id"
                    class="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full bg-purple-50 text-purple-700 border border-purple-100"
                  >
                    {{ getPoolName(team.pool_id) }}
                  </span>
                  <span v-else class="text-gray-400 text-sm">Aucun pool</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="player in (team.players || [])"
                      :key="player.id"
                      class="px-2 py-1 text-xs rounded-full bg-blue-50 text-blue-700 border border-blue-100"
                    >
                      {{ player.first_name }} {{ player.last_name }}
                    </span>
                    <span v-if="(team.players || []).length === 0" class="text-gray-400 text-sm">
                      Aucun joueur
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      @click="openEditModal(team)"
                      class="px-4 py-2 text-sm bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors font-medium"
                    >
                      Modifier
                    </button>
                    <button
                      @click="deleteTeam(team.id)"
                      class="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
                    >
                      Supprimer
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal -->
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
      >
        <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <!-- Modal Header -->
          <div class="flex items-center justify-between p-6 border-b">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingTeam ? 'Modifier l\'équipe' : 'Créer une équipe' }}
            </h2>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              ✕
            </button>
          </div>

          <!-- Modal Body -->
          <form @submit.prevent="saveTeam" class="p-6 space-y-6">
            <!-- Error Message -->
            <div
              v-if="error"
              class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg"
            >
              {{ error }}
            </div>

            <!-- Company -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Company <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.company"
                type="text"
                required
                class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                placeholder="Nom de l'entreprise"
              />
            </div>

            <!-- Pool -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Pool
              </label>
              <select
                v-model="form.pool_id"
                class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              >
                <option :value="null">Aucun pool</option>
                <option v-for="pool in pools" :key="pool.id" :value="pool.id">
                  {{ pool.name || pool.label || `Pool ${pool.id}` }}
                </option>
              </select>
            </div>

            <!-- Players -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Joueurs
              </label>
              <div class="border border-gray-300 rounded-lg p-4 max-h-48 overflow-y-auto space-y-2">
                <label
                  v-for="player in players"
                  :key="player.id"
                  class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :value="player.id"
                    v-model="form.player_ids"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span class="text-sm text-gray-700">
                    {{ player.first_name }} {{ player.last_name }}
                  </span>
                </label>
                <div v-if="players.length === 0" class="text-sm text-gray-400 text-center py-4">
                  Aucun joueur disponible
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center justify-end gap-3 pt-4 border-t">
              <button
                type="button"
                @click="closeModal"
                class="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Annuler
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { teamAPI } from '../services/teams'
import { poolAPI } from '../services/pools'
import { playerAPI } from '../services/players'

// State
const teams = ref([])
const pools = ref([])
const players = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingTeam = ref(null)
const error = ref(null)

// Form
const form = ref({
  company: '',
  pool_id: null,
  player_ids: []
})

// Helper functions
const getPoolName = (poolId) => {
  if (!poolId) return 'N/A'
  const pool = pools.value.find(p => p.id === poolId)
  return pool ? (pool.name || pool.label || `Pool ${poolId}`) : `Pool #${poolId}`
}

const getPlayerName = (playerId) => {
  const player = players.value.find(p => p.id === playerId)
  return player ? `${player.first_name} ${player.last_name}` : `Joueur #${playerId}`
}

// CRUD Operations
const loadTeams = async () => {
  loading.value = true
  try {
    const response = await teamAPI.list()
    teams.value = Array.isArray(response) ? response : (response.data || response.teams || [])
  } catch (err) {
    console.error('Erreur lors du chargement des équipes:', err)
    error.value = 'Impossible de charger les équipes'
  } finally {
    loading.value = false
  }
}

const loadPools = async () => {
  try {
    const response = await poolAPI.list()
    pools.value = Array.isArray(response.data) ? response.data : (response.data?.pools || [])
  } catch (err) {
    console.error('Erreur lors du chargement des pools:', err)
  }
}

const loadPlayers = async () => {
  try {
    const response = await playerAPI.list()
    players.value = Array.isArray(response.data) ? response.data : (response.data?.players || [])
  } catch (err) {
    console.error('Erreur lors du chargement des joueurs:', err)
  }
}

const openCreateModal = () => {
  editingTeam.value = null
  form.value = {
    company: '',
    pool_id: null,
    player_ids: []
  }
  error.value = null
  showModal.value = true
}

const openEditModal = (team) => {
  editingTeam.value = team
  form.value = {
    company: team.company || '',
    pool_id: team.pool_id || null,
    // Extraire les IDs des joueurs depuis le tableau d'objets players
    player_ids: (team.players || []).map(p => p.id)
  }
  error.value = null
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingTeam.value = null
  error.value = null
}

const saveTeam = async () => {
  saving.value = true
  error.value = null

  try {
    // Validation : exactement 2 joueurs requis
    if (!form.value.player_ids || form.value.player_ids.length !== 2) {
      error.value = 'Vous devez sélectionner exactement 2 joueurs pour former une équipe'
      saving.value = false
      return
    }

    // Transformer player_ids en player1_id et player2_id pour le backend
    const teamData = {
      company: form.value.company,
      pool_id: form.value.pool_id,
      player1_id: form.value.player_ids[0],
      player2_id: form.value.player_ids[1]
    }

    if (editingTeam.value) {
      await teamAPI.update(editingTeam.value.id, teamData)
    } else {
      await teamAPI.create(teamData)
    }
    await loadTeams()
    closeModal()
  } catch (err) {
    console.error('Erreur lors de l\'enregistrement:', err)
    error.value = err.response?.data?.detail || 'Erreur lors de l\'enregistrement de l\'équipe'
  } finally {
    saving.value = false
  }
}

const deleteTeam = async (id) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette équipe ?')) return

  try {
    await teamAPI.remove(id)
    await loadTeams()
  } catch (err) {
    console.error('Erreur lors de la suppression:', err)
    alert('Erreur lors de la suppression de l\'équipe')
  }
}

// Initialize
onMounted(async () => {
  await Promise.all([
    loadTeams(),
    loadPools(),
    loadPlayers()
  ])
})
</script>
