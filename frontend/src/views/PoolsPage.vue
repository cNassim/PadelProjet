<template>
  <div class="min-h-screen px-4 py-8 bg-gray-50">
    <div class="max-w-6xl mx-auto">
      
      <div class="flex flex-col items-center justify-between mb-8 md:flex-row">
        <h1 class="mb-4 text-3xl font-bold text-gray-800 md:mb-0">🎱 Poules</h1>
        
        <div v-if="authStore.isAdmin">
          <button 
            @click="openAddModal"
            class="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 rounded-lg shadow-md hover:bg-blue-700 transition"
          >
            <span>➕</span> Nouvelle Poule
          </button>
        </div>
      </div>

      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block w-12 h-12 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
      </div>

      <div v-else-if="pools.length === 0" class="p-8 text-center bg-white shadow-lg rounded-xl text-gray-500">
        Aucune poule n'a été créée pour le moment.
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="pool in pools" :key="pool.id" class="bg-white shadow-lg rounded-xl overflow-hidden flex flex-col">
          <div class="bg-blue-600 p-4 flex justify-between items-center text-white">
            <h2 class="text-xl font-bold">{{ pool.name }}</h2>
            <div v-if="authStore.isAdmin">
              <button @click="openEditModal(pool)" class="text-white hover:text-blue-200 p-1 mr-2 rounded transition" title="Modifier la poule">✏️</button>
              <button @click="deletePool(pool.id)" class="text-white hover:text-red-200 p-1 rounded transition" title="Supprimer la poule">🗑️</button>
            </div>
          </div>

          <div class="p-4 flex-grow bg-white">
            <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              {{ pool.teams ? pool.teams.length : 0 }} Équipes
            </div>
            <ul v-if="pool.teams && pool.teams.length > 0" class="space-y-2">
              <li v-for="team in pool.teams" :key="team.id" class="flex items-center gap-3 p-2 rounded hover:bg-gray-50 border border-transparent hover:border-gray-100 transition">
                <span class="w-2 h-2 rounded-full bg-green-500"></span>
                <div class="flex flex-col">
                  <span class="font-medium text-gray-800">{{ team.company }}</span>
                  <span class="text-xs text-gray-500">
                    {{ team.players[0]?.last_name }} & {{ team.players[1]?.last_name }}
                  </span>
                </div>
              </li>
            </ul>
            <div v-else class="text-sm text-gray-400 italic py-4 text-center">
              Aucune équipe assignée.
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="flex flex-col w-full max-w-2xl m-4 overflow-hidden bg-white shadow-2xl rounded-2xl max-h-[90vh]">
        <div class="p-6 text-white bg-blue-600 border-b">
          <h2 class="text-xl font-bold">{{ isEditing ? 'Modifier la poule' : 'Créer une nouvelle poule' }}</h2>
        </div>

        <div class="p-6 overflow-y-auto">
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">Nom de la poule</label>
              <input v-model="poolForm.name" type="text" placeholder="Ex: Poule A"  required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500">
            </div>

            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="block text-sm font-semibold text-gray-700">Sélectionner les équipes libres</label>
                <span :class="poolForm.team_ids.length === 6 ? 'text-green-600 font-bold' : 'text-blue-600'">
                  {{ poolForm.team_ids.length }} / 6 sélectionnées
                </span>
              </div>
              
              <div class="border rounded-lg max-h-60 overflow-y-auto p-2 bg-gray-50 grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div v-for="team in availableTeamsDisplay" :key="team.id" class="flex items-center p-2 bg-white border rounded hover:bg-blue-50 cursor-pointer">
                  <input 
                    type="checkbox" 
                    :value="team.id" 
                    v-model="poolForm.team_ids"
                    :disabled="poolForm.team_ids.length >= 6 && !poolForm.team_ids.includes(team.id)"
                    class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  >
                  <div class="ml-2 text-sm">
                    <div class="font-medium">{{ team.company }}</div>
                    <div class="text-xs text-gray-500">{{ team.players[0]?.last_name }} / {{ team.players[1]?.last_name }}</div>
                  </div>
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                * Une poule doit contenir exactement 6 équipes (Règle métier).
              </p>
            </div>

            <div v-if="formError" class="p-3 text-sm text-red-600 rounded-lg bg-red-50">
              {{ formError }}
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t">
              <button type="button" @click="showModal = false" class="px-4 py-2 text-gray-600 rounded-lg hover:bg-gray-100">Annuler</button>
              <button 
                type="submit" 
                :disabled="submitting || poolForm.team_ids.length !== 6" 
                class="px-6 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {{ submitting ? 'Enregistrement...' : (isEditing ? 'Enregistrer les modifications' : 'Créer la poule') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import poolService from '../services/pools'
import teamService from '../services/teams'

const authStore = useAuthStore()

// --- ETAT ---
const loading = ref(true)
const pools = ref([])
const allTeams = ref([]) // Renommé pour plus de clarté
const showModal = ref(false)
const submitting = ref(false)
const formError = ref(null)
const isEditing = ref(false)
const editingPoolId = ref(null)

const poolForm = reactive({
  name: '',
  team_ids: []
})

const availableTeamsDisplay = computed(() => {
  return allTeams.value.filter(team => {
    return !team.pool_id || (isEditing.value && team.pool_id === editingPoolId.value);
  });
});

// --- CHARGEMENT ---
const loadData = async () => {
  loading.value = true
  try {
    //Charger les poules
    const poolsData = await poolService.getPools()
    // On gère si c'est un tableau direct ou un objet { pools: [...] }
    pools.value = Array.isArray(poolsData) ? poolsData : (poolsData.pools || [])

    // Charger les équipes (si Admin, pour la création)
    if (authStore.isAdmin) {
      console.log("🔄 Chargement des équipes pour la modale...")
      const result = await teamService.list()
      
      console.log("📦 Données reçues de l'API Team:", result)

      if (Array.isArray(result)) {
        // Cas 1 : L'API renvoie directement [Equipe1, Equipe2...]
        allTeams.value = result
      } else if (result.teams && Array.isArray(result.teams)) {
        // Cas 2 : L'API renvoie { teams: [Equipe1...] } (Standard JSONAPI)
        allTeams.value = result.teams
      } else if (result.data && Array.isArray(result.data)) {
        // Cas 3 : L'API renvoie { data: [Equipe1...] } (Parfois axios ou pagination)
        allTeams.value = result.data
      } else {
        // Cas 4 : Format inconnu, on met vide pour éviter le crash
        console.warn("⚠️ Format des équipes non reconnu", result)
        allTeams.value = []
      }
      
      console.log("✅ Équipes stockées dans le sélecteur :", availableTeams.value)
    }
  } catch (err) {
    console.error("❌ Erreur chargement:", err)
  } finally {
    loading.value = false
  }
}

// --- ACTIONS ---
const openAddModal = () => {
  isEditing.value = false;
  editingPoolId.value = null; 
  poolForm.name = ''
  poolForm.team_ids = []
  formError.value = null
  showModal.value = true
}

const openEditModal = (pool) => {
  isEditing.value = true;
  editingPoolId.value = pool.id;
  poolForm.name = pool.name;
  // On pré-remplit avec les IDs des équipes actuelles
  poolForm.team_ids = pool.teams.map(t => t.id);
  formError.value = null;
  showModal.value = true;
};


const handleSubmit = async () => {
  if (poolForm.team_ids.length !== 6) {
    formError.value = "Une poule doit contenir exactement 6 équipes.";
    return;
  }

  submitting.value = true;
  formError.value = null;

  try {
    if (isEditing.value) {
      await poolService.updatePool(editingPoolId.value, {
        name: poolForm.name,
        team_ids: poolForm.team_ids
      });
      console.log("✅ Mise à jour réussie");
    } else {
      await poolService.createPool(poolForm);
      console.log("✅ Création réussie");
    }
    
    //correction du problème de l'incohérence entre back et front (l'update se faisait que si je rafraichis la page)
    showModal.value = false; 
    await loadData();        
    alert(isEditing.value ? "Poule modifiée !" : "Poule créée !");

  } catch (err) {
    console.error("❌ Erreur lors du submit:", err);
    formError.value = err.response?.data?.detail || "Erreur de communication avec le serveur";
  } finally {
    submitting.value = false;
  }
};

const deletePool = async (id) => {
  if (!confirm("Attention : Supprimer une poule supprimera son lien avec les équipes. Continuer ?")) return
  
  try {
    await poolService.deletePool(id)
    loadData()
  } catch (err) {
    alert("Erreur suppression: " + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  loadData()
})
</script>