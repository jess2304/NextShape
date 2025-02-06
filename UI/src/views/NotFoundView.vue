<script setup lang="ts">
import Button from "primevue/button"
</script>
<template>
  <div class="text-center mt-10">
    <h1 class="text-4xl font-bold text-red-500">404 - Page non trouvée</h1>
    <p class="text-lg mt-4">La page que vous cherchez n'existe pas.</p>
    <Button
      as="router-link"
      label="Retour à l'accueil"
      to="/"
      class="mt-4 rounded no-underline"
    />
  </div>
</template>
