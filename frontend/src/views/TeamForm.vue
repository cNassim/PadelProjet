<template>
  <div class="container mx-auto px-4 py-6">
    <div class="bg-white rounded-2xl shadow-lg border border-gray-100 max-w-3xl mx-auto">
      <div class="p-5 border-b">
        <h1 class="text-2xl font-bold text-gray-900">{{ isEdit ? 'Modifier une équipe' : 'Créer une équipe' }}</h1>
        <p class="text-sm text-gray-500">Company, joueurs (2) et pool optionnelle</p>
      </div>

      <form @submit.prevent="onSubmit" class="p-5 space-y-5">
        <div>
          <label class="block mb-1 font-semibold text-gray-800">Company</label>
          <input v-model="form.company" required class="w-full border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Company name" />
        </div>

        <div>
          <label class="block mb-1 font-semibold text-gray-800">Pool</label>
          <select v-model="selectedPoolId" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            <option :value="null">None</option>
            <option v-for="pool in pools" :key="pool.id" :value="pool.id">
              {{ pool.name || pool.label || ('Poule #' + pool.id) }}
            </option>
          </select>
          <p class="text-sm text-gray-500 mt-1">Optionnel: associer l'équipe à une pool.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block mb-1 font-semibold text-gray-800">Joueur 1</label>
            <select v-model="selectedPlayer1Id" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option :value="null" disabled>Choisir un joueur</option>
              <option v-for="p in players" :key="p.id" :value="p.id">
                {{ formatPlayer(p) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block mb-1 font-semibold text-gray-800">Joueur 2</label>
            <select v-model="selectedPlayer2Id" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option :value="null" disabled>Choisir un joueur</option>
              <option v-for="p in players" :key="p.id" :value="p.id">
                {{ formatPlayer(p) }}
              </option>
            </select>
          </div>
        </div>
        <p v-if="samePlayers" class="text-sm text-red-600">Les deux joueurs doivent être différents.</p>

        <div class="flex items-center gap-3">
          <button :disabled="saving" class="px-5 py-2.5 bg-blue-600 text-white rounded-xl shadow hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed">
            {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
          <router-link to="/teams" class="px-5 py-2.5 bg-gray-100 text-gray-800 rounded-xl border hover:bg-gray-200">Annuler</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { teamAPI } from '../services/teams'
import { playerAPI } from '../services/players'
import { poolAPI } from '../services/pools'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const form = ref({ company: '' })
const players = ref([])
const selectedPlayer1Id = ref(null)
const selectedPlayer2Id = ref(null)
const pools = ref([])
const selectedPoolId = ref(null)
const saving = ref(false)

const formatPlayer = (p) => `${p.first_name ?? ''} ${p.last_name ?? ''}`.trim() || p.email || `#${p.id}`
const samePlayers = computed(() => selectedPlayer1Id.value && selectedPlayer2Id.value && selectedPlayer1Id.value === selectedPlayer2Id.value)

const loadPlayers = async () => {
  const { data } = await playerAPI.list()
  // data peut être {players: [...]} ou [...] selon backend; normaliser
  players.value = Array.isArray(data) ? data : (data.players ?? [])
}

const loadPools = async () => {
  const { data } = await poolAPI.list()
  pools.value = data
}

const loadTeam = async () => {
  if (!isEdit.value) return
  try {
    const { data } = await teamAPI.get(route.params.id)
    form.value.company = data.company
    const playersArr = data.players || []
    selectedPlayer1Id.value = playersArr[0]?.id ?? null
    selectedPlayer2Id.value = playersArr[1]?.id ?? null
    selectedPoolId.value = data.pool_id ?? data.pool?.id ?? null
  } catch (e) {
    alert("Impossible de charger l'équipe (endpoint GET /teams/{id} manquant).")
    router.push('/teams')
  }
}

const onSubmit = async () => {
  saving.value = true
  try {
    const payload = {
      company: form.value.company,
      player1_id: selectedPlayer1Id.value,
      player2_id: selectedPlayer2Id.value,
      pool_id: selectedPoolId.value
    }
    if (samePlayers.value) return
    if (isEdit.value) {
      await teamAPI.update(route.params.id, payload)
    } else {
      await teamAPI.create(payload)
    }
    router.push('/teams')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadPlayers(), loadPools(), loadTeam()])
})
</script>
