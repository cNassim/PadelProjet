<template>
  <div class="container mx-auto px-4 py-6">
    <div class="bg-white rounded-2xl shadow-lg border border-gray-100">
      <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between p-5 border-b">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Équipes</h1>
          <p class="text-sm text-gray-500">Gérez les équipes et leurs joueurs</p>
        </div>
        <router-link class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl shadow hover:bg-blue-700 transition-colors" to="/teams/new">
          <span>➕</span>
          <span>Créer une équipe</span>
        </router-link>
      </div>

      <div v-if="loading" class="p-6 text-gray-600">Chargement...</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-left">
          <thead>
            <tr class="bg-gray-50 text-gray-600 text-sm">
              <th class="px-4 py-3 font-semibold">Company</th>
              <th class="px-4 py-3 font-semibold">Pool</th>
              <th class="px-4 py-3 font-semibold">Joueurs</th>
              <th class="px-4 py-3 font-semibold w-48">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in teams" :key="t.id" class="border-t hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ t.company }}</td>
              <td class="px-4 py-3 text-gray-700">
                <span v-if="t.pool || t.pool_id" class="inline-flex items-center px-2 py-0.5 text-xs rounded-full bg-purple-50 text-purple-700 border border-purple-100">
                  {{ t.pool?.name || t.pool?.label || ('Pool #' + t.pool_id) }}
                </span>
                <span v-else class="text-gray-400 text-sm">None</span>
              </td>
              <td class="px-4 py-3 text-gray-700">
                <div class="flex flex-wrap gap-1">
                  <span v-for="p in (t.players || [])" :key="p.id" class="px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-700 border border-blue-100">
                    {{ (p.first_name || '') + ' ' + (p.last_name || '') }}
                  </span>
                  <span v-if="(t.players || []).length === 0" class="text-gray-400">Aucun joueur</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <router-link class="px-3 py-1.5 text-sm bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors" :to="`/teams/${t.id}/edit`">Modifier</router-link>
                  <button class="px-3 py-1.5 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors" @click="onDelete(t.id)">Supprimer</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="teams.length === 0" class="p-8 text-center text-gray-500">
          <div class="text-3xl mb-2">🗂️</div>
          <p>Aucune équipe pour l’instant.</p>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { teamAPI } from '../services/teams'

const loading = ref(false)
const teams = ref([])

const load = async () => {
  loading.value = true
  try {
    const { data } = await teamAPI.list()
    teams.value = Array.isArray(data) ? data : (data.teams ?? [])
  } finally {
    loading.value = false
  }
}
const onDelete = async (id) => {
  if (!confirm('Supprimer cette équipe ?')) return
  await teamAPI.remove(id)
  await load()
}
onMounted(load)
</script>
