<script setup lang="ts">
import NavBarComponent from "@/components/NavBarComponent.vue"
import FooterComponent from "@/components/FooterComponent.vue"
</script>

<template>
  <div class="public-layout">
    <header class="public-header"><NavBarComponent /></header>
    <main id="main-content" class="public-content" tabindex="-1"><slot /></main>
    <FooterComponent />
  </div>
</template>
