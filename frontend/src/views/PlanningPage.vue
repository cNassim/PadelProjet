// ============================================
// FICHIER : frontend/src/views/PlanningPage.vue
// ============================================

<template>
  <div class="min-h-screen px-4 py-8 bg-gray-50">
    <div class="max-w-6xl mx-auto">
      
      <div class="flex flex-col items-center justify-between mb-8 md:flex-row">
        <h1 class="mb-4 text-3xl font-bold text-gray-800 md:mb-0">📅 Planning</h1>
        
        <div class="flex items-center gap-4 p-2 bg-white rounded-lg shadow">
          <button @click="changeMonth(-1)" class="p-2 rounded-full hover:bg-gray-100">◀️</button>
          <span class="text-lg font-semibold capitalize min-w-[150px] text-center">
            {{ currentMonthLabel }}
          </span>
          <button @click="changeMonth(1)" class="p-2 rounded-full hover:bg-gray-100">▶️</button>
        </div>

        <div v-if="authStore.isAdmin">
          <button 
            @click="openAddModal"
            class="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 rounded-lg shadow-md hover:bg-blue-700"
          >
            <span>➕</span> Nouvel événement
          </button>
        </div>
      </div>

      <div v-if="!authStore.isAdmin && authStore.isAuthenticated" class="flex justify-end mb-6">
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" v-model="showAllEvents" class="w-5 h-5 text-blue-600 rounded focus:ring-blue-500">
          <span class="text-gray-700">Voir tous les événements (pas que les miens)</span>
        </label>
      </div>

      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block w-12 h-12 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
      </div>

      <div v-else class="overflow-hidden bg-white shadow-lg rounded-xl">
        <div class="grid grid-cols-7 border-b bg-gray-100">
          <div v-for="day in weekDays" :key="day" class="py-3 font-semibold text-center text-gray-600">
            {{ day }}
          </div>
        </div>

        <div class="grid grid-cols-7 auto-rows-[120px]">
          <div 
            v-for="n in paddingDays" 
            :key="'pad-' + n" 
            class="border-r border-b bg-gray-50"
          ></div>

          <div 
            v-for="day in daysInMonth" 
            :key="day.date"
            @click="openDayDetails(day)"
            class="relative p-2 transition-colors border-r border-b cursor-pointer hover:bg-blue-50 group"
            :class="{ 'bg-blue-50': isToday(day.date) }"
          >
            <span 
              class="inline-flex items-center justify-center text-sm font-medium rounded-full w-7 h-7"
              :class="isToday(day.date) ? 'bg-blue-600 text-white' : 'text-gray-700'"
            >
              {{ day.dayNumber }}
            </span>

            <div class="mt-2 space-y-1">
              <div 
                v-for="event in filterEvents(day.events)" 
                :key="event.id"
                class="text-xs px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700 truncate border border-indigo-200"
              >
                {{ event.event_time.slice(0, 5) }} - {{ event.matches.length }} match(s)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedDay" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="selectedDay = null">
      <div class="w-full max-w-lg m-4 overflow-hidden bg-white shadow-2xl rounded-2xl">
        <div class="flex items-center justify-between p-6 border-b bg-gray-50">
          <h2 class="text-xl font-bold text-gray-800">
            {{ formatDateFull(selectedDay.date) }}
          </h2>
          <button @click="selectedDay = null" class="text-gray-500 hover:text-gray-700">✖️</button>
        </div>
        
        <div class="p-6 max-h-[60vh] overflow-y-auto">
          <div v-if="filterEvents(selectedDay.events).length === 0" class="py-8 text-center text-gray-500">
            Aucun événement prévu ce jour.
          </div>

          <div v-else class="space-y-6">
            <div v-for="event in filterEvents(selectedDay.events)" :key="event.id" class="p-4 border shadow-sm bg-white rounded-xl">
              <div class="flex items-center justify-between mb-3 pb-2 border-b">
                <span class="text-lg font-bold text-blue-600">🕒 {{ event.event_time.slice(0, 5) }}</span>
                <span v-if="authStore.isAdmin" class="flex gap-3">
                  <button @click="openEditModal(event)" class="text-sm text-blue-600 hover:text-blue-800">✏️ Modifier</button>
                  <button @click="deleteEvent(event.id)" class="text-sm text-red-500 hover:text-red-700">🗑️ Supprimer</button>
                </span>
              </div>

              <div class="space-y-3">
                <div v-for="match in event.matches" :key="match.id" class="p-3 text-sm rounded-lg bg-gray-50">
                  <div class="flex justify-between mb-1 text-xs text-gray-500">
                    <span>🎾 Piste {{ match.court_number }}</span>
                    <span :class="getStatusColor(match.status)">{{ formatStatus(match.status) }}</span>
                  </div>
                  <div class="font-medium text-gray-800">
                    {{ match.team1?.company || 'Equipe 1' }} <span class="text-gray-400">vs</span> {{ match.team2?.company || 'Equipe 2' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="p-4 text-right border-t bg-gray-50">
          <button @click="selectedDay = null" class="px-4 py-2 text-gray-600 bg-white border rounded-lg hover:bg-gray-50">
            Fermer
          </button>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="flex flex-col w-full max-w-2xl m-4 overflow-hidden bg-white shadow-2xl rounded-2xl max-h-[90vh]">
        <div class="p-6 text-white bg-blue-600 border-b">
          <h2 class="text-xl font-bold">{{ isEditing ? 'Modifier l\'événement' : 'Ajouter un événement' }}</h2>
        </div>

        <div class="p-6 overflow-y-auto">
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block mb-1 text-sm font-semibold text-gray-700">Date</label>
                <input v-model="eventForm.event_date" type="date" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" :min="todayStr">
              </div>
              <div>
                <label class="block mb-1 text-sm font-semibold text-gray-700">Heure</label>
                <input v-model="eventForm.event_time" type="time" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500">
              </div>
            </div>

            <div v-if="!isEditing">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-semibold text-gray-800">Matchs (1 à 3)</h3>
                <button type="button" @click="addMatchSlot" :disabled="eventForm.matches.length >= 3" class="text-sm text-blue-600 hover:underline disabled:text-gray-400">
                  + Ajouter un match
                </button>
              </div>

              <div v-for="(match, index) in eventForm.matches" :key="index" class="relative p-4 mb-3 border border-gray-200 bg-gray-50 rounded-xl">
                <button v-if="eventForm.matches.length > 1" type="button" @click="removeMatchSlot(index)" class="absolute top-2 right-2 text-red-500 hover:text-red-700">✖</button>
                
                <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
                  <div>
                    <label class="block mb-1 text-xs font-medium text-gray-600">Piste</label>
                    <select v-model="match.court_number" required class="w-full px-2 py-1.5 text-sm border rounded">
                      <option v-for="n in 10" :key="n" :value="n">Piste {{ n }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block mb-1 text-xs font-medium text-gray-600">Équipe 1</label>
                    <select v-model="match.team1_id" required class="w-full px-2 py-1.5 text-sm border rounded">
                      <option value="" disabled>-- Choisir une équipe --</option>
                      <option v-for="team in teams" :key="team.id" :value="team.id">
                        {{ team.company }} ({{ team.players[0]?.last_name }})
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="block mb-1 text-xs font-medium text-gray-600">Équipe 2</label>
                    <select v-model="match.team2_id" required class="w-full px-2 py-1.5 text-sm border rounded">
                      <option value="" disabled>-- Choisir une équipe --</option>
                      <option v-for="team in teams" :key="team.id" :value="team.id">
                        {{ team.company }} ({{ team.players[0]?.last_name }})
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="p-4 text-sm text-blue-800 border border-blue-200 bg-blue-50 rounded-xl">
              ℹ️ Pour modifier les équipes ou les pistes d'un match existant, veuillez passer par la page <strong>Matchs</strong>. Ici, vous ne modifiez que le créneau horaire global.
            </div>

            <div v-if="formError" class="p-3 text-sm text-red-600 rounded-lg bg-red-50">
              {{ formError }}
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t">
              <button type="button" @click="showModal = false" class="px-4 py-2 text-gray-600 rounded-lg hover:bg-gray-100">Annuler</button>
              <button type="submit" :disabled="submitting" class="px-6 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-400">
                {{ submitting ? 'Enregistrement...' : (isEditing ? 'Modifier' : 'Créer') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import eventService from '../services/events'
import teamService from '../services/teams'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

// --- ETAT ---
const loading = ref(true)
const currentDate = ref(new Date())
const events = ref([])
const teams = ref([])
const showAllEvents = ref(false)
const selectedDay = ref(null)

// Formulaire
const showModal = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const formError = ref(null)
const editingId = ref(null)

// Données formulaire
const eventForm = reactive({
  event_date: '',
  event_time: '',
  matches: []
})

// --- CALENDRIER ---
const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
const todayStr = new Date().toISOString().split('T')[0]

const currentMonthLabel = computed(() => {
  return currentDate.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
})

const daysInMonth = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const nbDays = new Date(year, month + 1, 0).getDate()
  
  const days = []
  for (let i = 1; i <= nbDays; i++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`
    const dayEvents = events.value.filter(e => e.event_date === dateStr)
    days.push({ date: dateStr, dayNumber: i, events: dayEvents })
  }
  return days
})

const paddingDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  return firstDay === 0 ? 6 : firstDay - 1
})

// --- CHARGEMENT ---
const loadData = async () => {
  loading.value = true
  try {
    const year = currentDate.value.getFullYear()
    const month = String(currentDate.value.getMonth() + 1).padStart(2, '0')
    
    // Charger événements
    const result = await eventService.getEvents({ month: `${year}-${month}` })
    events.value = result.events

    // Charger équipes (Admin uniquement)
    if (authStore.isAdmin && teams.value.length === 0) {
      const teamRes = await teamService.getTeams()
      teams.value = teamRes.teams
    }
  } catch (err) {
    console.error("Erreur chargement:", err)
  } finally {
    loading.value = false
  }
}

const changeMonth = (delta) => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(newDate.getMonth() + delta)
  currentDate.value = newDate
  loadData()
}

// --- GESTION FORMULAIRE ---
const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  eventForm.event_date = ''
  eventForm.event_time = ''
  eventForm.matches = [ { court_number: 1, team1_id: '', team2_id: '' } ]
  formError.value = null
  showModal.value = true
}

const openEditModal = (event) => {
  isEditing.value = true
  editingId.value = event.id
  eventForm.event_date = event.event_date
  eventForm.event_time = event.event_time
  // En édition, on ne touche pas aux matchs ici (géré dans Matchs)
  eventForm.matches = [] 
  formError.value = null
  showModal.value = true
  selectedDay.value = null // Fermer le détail
}

const addMatchSlot = () => {
  if (eventForm.matches.length < 3) {
    eventForm.matches.push({ court_number: 1, team1_id: '', team2_id: '' })
  }
}

const removeMatchSlot = (index) => {
  eventForm.matches.splice(index, 1)
}

const handleSubmit = async () => {
  submitting.value = true
  formError.value = null
  try {
    if (isEditing.value) {
      // MODE MODIFICATION
      await eventService.updateEvent(editingId.value, {
        event_date: eventForm.event_date,
        event_time: eventForm.event_time
      })
      alert("✅ Événement modifié !")
    } else {
      // MODE CRÉATION
      await eventService.createEvent(eventForm)
      alert("✅ Événement créé !")
    }
    showModal.value = false
    loadData()
  } catch (err) {
    formError.value = err.response?.data?.detail || "Une erreur est survenue"
  } finally {
    submitting.value = false
  }
}

const deleteEvent = async (id) => {
  if (!confirm("Voulez-vous vraiment supprimer cet événement ?")) return
  try {
    await eventService.deleteEvent(id)
    loadData()
    if (selectedDay.value) {
      selectedDay.value.events = selectedDay.value.events.filter(e => e.id !== id)
      if (selectedDay.value.events.length === 0) selectedDay.value = null
    }
  } catch (err) {
    alert("Erreur: " + (err.response?.data?.detail || err.message))
  }
}

// --- HELPERS ---
const isToday = (d) => d === todayStr
const formatDateFull = (d) => new Date(d).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
const formatStatus = (s) => ({ 'A_VENIR': 'À venir', 'TERMINE': 'Terminé', 'ANNULE': 'Annulé' }[s] || s)
const getStatusColor = (s) => ({ 'A_VENIR': 'text-blue-600', 'TERMINE': 'text-green-600', 'ANNULE': 'text-red-600' }[s] || 'text-gray-600')

const filterEvents = (dayEvents) => {
  if (authStore.isAdmin || showAllEvents.value) return dayEvents
  const myPlayerId = authStore.user?.player?.id
  if (!myPlayerId) return dayEvents
  return dayEvents.filter(e => e.matches.some(m => 
    m.team1?.players.some(p => p.id === myPlayerId) || 
    m.team2?.players.some(p => p.id === myPlayerId)
  ))
}

const openDayDetails = (day) => {
  selectedDay.value = day
}

onMounted(() => {
  loadData()
})
</script>