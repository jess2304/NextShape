<script setup lang="ts">
import NavBarComponent from "./components/NavBarComponent.vue"
</script>

<template>
  <div class="min-h-screen flex flex-column">
    <header class="z-3">
      <NavBarComponent class="shadow-2 m-1" />
    </header>
    <main class="flex-grow-1 flex flex-column p-4"></main>
    <footer class="z-3 shadow-2 text-center"></footer>
  </div>
</template>

<style scoped></style>
