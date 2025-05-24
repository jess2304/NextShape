<script setup lang="ts">
import { RouterView } from "vue-router"
import NavBarComponent from "./components/NavBarComponent.vue"
import FooterComponent from "./components/FooterComponent.vue"
import { useAuthStore } from "@/stores/authStore"
import Toast from "primevue/toast"
// Appel du store d'authentification pour charger l'utilisateur en cours.
const authStore = useAuthStore()
</script>

<template>
  <div class="flex flex-column min-h-screen">
    <header class="z-3">
      <NavBarComponent class="shadow-3 m-1" />
    </header>
    <main class="flex-grow-1 overflow-auto p-4">
      <router-view />
    </main>
    <footer class="surface-100 z-3 shadow-2 text-center">
      <FooterComponent />
    </footer>
    <Toast />
  </div>
</template>
<style scoped></style>
