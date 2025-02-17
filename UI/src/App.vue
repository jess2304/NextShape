<script setup lang="ts">
import { RouterView } from "vue-router"
import NavBarComponent from "./components/NavBarComponent.vue"
import FooterComponent from "./components/FooterComponent.vue"
</script>

<template>
  <div class="h-screen flex flex-column">
    <header class="z-3 shadow-2 p-2 surface-100">
      <NavBarComponent class="shadow-2 m-1" />
    </header>
    <main class="flex-grow-1 overflow-auto p-4">
      <router-view />
    </main>
    <footer class="surface-100 z-3 shadow-2 text-center">
      <FooterComponent />
    </footer>
  </div>
</template>
<style scoped></style>
