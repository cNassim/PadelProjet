// ============================================
// FICHIER : frontend/src/views/ResultsPage.vue
// ============================================

<template>
  <div class="min-h-screen px-4 py-8 bg-gray-50">
    <div class="max-w-5xl mx-auto">
      
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold text-gray-800">📊 Résultats & Classement</h1>
        <p class="text-gray-600">Suivez les performances des entreprises</p>
      </div>

      <div class="flex justify-center mb-8">
        <div class="bg-white p-1 rounded-xl shadow-sm border border-gray-200 inline-flex">
          <button
            @click="activeTab = 'ranking'"
            :class="[
              'px-6 py-2.5 rounded-lg text-sm font-medium transition-all',
              activeTab === 'ranking' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'
            ]"
          >
            🏆 Classement Général
          </button>
          <button
            v-if="!authStore.isAdmin && authStore.isAuthenticated"
            @click="activeTab = 'history'"
            :class="[
              'px-6 py-2.5 rounded-lg text-sm font-medium transition-all',
              activeTab === 'history' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'
            ]"
          >
            👤 Mes Résultats
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block w-10 h-10 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
      </div>

      <div v-else-if="activeTab === 'ranking'" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Pos</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Entreprise</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Pts</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Joués</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider hidden md:table-cell">Gagnés</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider hidden md:table-cell">Perdus</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider hidden lg:table-cell">Diff Sets</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="row in rankings" :key="row.company" class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm"
                    :class="{
                      'bg-yellow-100 text-yellow-700': row.position === 1,
                      'bg-gray-100 text-gray-700': row.position === 2,
                      'bg-orange-100 text-orange-700': row.position === 3,
                      'text-gray-500': row.position > 3
                    }"
                  >
                    {{ row.position }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                  {{ row.company }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center font-bold text-blue-600">
                  {{ row.points }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-gray-600">
                  {{ row.played }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-green-600 hidden md:table-cell">
                  {{ row.wins }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-red-600 hidden md:table-cell">
                  {{ row.losses }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-gray-500 hidden lg:table-cell">
                  {{ row.sets_won - row.sets_lost }}
                </td>
              </tr>
              <tr v-if="rankings.length === 0">
                <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                  Aucun classement disponible pour le moment.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="space-y-6">
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
            <div class="p-3 bg-blue-100 text-blue-600 rounded-lg text-2xl">🎾</div>
            <div>
              <p class="text-sm text-gray-500">Matchs joués</p>
              <p class="text-2xl font-bold text-gray-800">{{ stats.total }}</p>
            </div>
          </div>
          <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
            <div class="p-3 bg-green-100 text-green-600 rounded-lg text-2xl">🏆</div>
            <div>
              <p class="text-sm text-gray-500">Victoires</p>
              <p class="text-2xl font-bold text-gray-800">{{ stats.wins }}</p>
            </div>
          </div>
          <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
            <div class="p-3 bg-red-100 text-red-600 rounded-lg text-2xl">📉</div>
            <div>
              <p class="text-sm text-gray-500">Défaites</p>
              <p class="text-2xl font-bold text-gray-800">{{ stats.losses }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="p-6 border-b border-gray-100">
            <h3 class="font-bold text-gray-800">Historique des matchs</h3>
          </div>
          <div v-if="myResults.length === 0" class="p-8 text-center text-gray-500">
            Vous n'avez pas encore joué de match.
          </div>
          <div v-else class="divide-y divide-gray-100">
            <div v-for="match in myResults" :key="match.id" class="p-4 flex items-center justify-between hover:bg-gray-50">
              <div class="flex flex-col">
                <span class="text-sm text-gray-500">{{ formatDate(match.date) }}</span>
                <span class="font-medium text-gray-800">vs {{ match.opponent }}</span>
              </div>
              
              <div class="flex items-center gap-4">
                <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">{{ match.score }}</span>
                <span 
                  class="text-xs font-bold px-2 py-1 rounded uppercase w-20 text-center"
                  :class="match.result === 'VICTOIRE' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                >
                  {{ match.result }}
                </span>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import resultService from '../services/results'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

// État
const activeTab = ref('ranking')
const loading = ref(true)
const rankings = ref([])
const myResults = ref([])
const stats = ref({ total: 0, wins: 0, losses: 0 })

// Chargement
const loadData = async () => {
  loading.value = true
  try {
    // 1. Classement (Pour tout le monde)
    const rankRes = await resultService.getRankings()
    rankings.value = rankRes.rankings

    // 2. Historique (Si joueur connecté)
    if (!authStore.isAdmin && authStore.isAuthenticated) {
      const myRes = await resultService.getMyResults()
      myResults.value = myRes.results
      stats.value = myRes.statistics
    }
  } catch (err) {
    console.error("Erreur chargement résultats", err)
  } finally {
    loading.value = false
  }
}

// Helpers
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => {
  loadData()
})
</script>