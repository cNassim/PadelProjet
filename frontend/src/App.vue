// ============================================
// FICHIER : frontend/src/App.vue
// ============================================

<template>
  <div id="app">
    <NavBar v-if="authStore.isAuthenticated" />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import NavBar from './components/NavBar.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Vérifier si un token existe au démarrage
  authStore.checkAuth()
})
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #f9fafb;
}
</style>