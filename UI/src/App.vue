<script setup lang="ts">
import { RouterView } from "vue-router"
import PublicLayout from "@/components/layout/PublicLayout.vue"
import AppLayout from "@/components/layout/AppLayout.vue"
import { useAuthStore } from "@/stores/authStore"
import Toast from "primevue/toast"
const authStore = useAuthStore()
</script>

<template>
  <a class="skip-link" href="#main-content">Aller au contenu</a>
  <component :is="authStore.user ? AppLayout : PublicLayout">
    <RouterView v-slot="{ Component, route }">
      <component
        :is="Component"
        v-if="!route.meta.requiresAuth || authStore.user"
        :key="authStore.user?.email ?? 'anonymous'"
      />
    </RouterView>
  </component>
  <Toast :key="authStore.user?.email ?? 'anonymous'" />
</template>
