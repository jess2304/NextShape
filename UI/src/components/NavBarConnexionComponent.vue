<script setup lang="ts">
import Menu from "primevue/menu"
import Button from "primevue/button"
import Avatar from "primevue/avatar"
import { useRouter } from "vue-router"
import { ref, computed } from "vue"
import { useAuthStore } from "@/stores/authStore"

const router = useRouter()

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.user !== null)

const userMenu = ref()

const userMenuItems = computed(() => [
  {
    label: "Profil",
    icon: "pi pi-user",
    command: () => router.push("/profil"),
  },
  {
    label: "Déconnexion",
    icon: "pi pi-sign-out",
    command: async () => await authStore.logout(),
  },
])
</script>
<template>
  <div class="flex items-center gap-2">
    <template v-if="!isLoggedIn">
      <Button
        label="Connexion"
        severity="secondary"
        text
        @click="router.push('/connexion')"
      />
      <Button
        label="Inscription"
        severity="primary"
        raised
        @click="router.push('/inscription')"
      />
    </template>
    <template v-else>
      <div class="flex items-center gap-2">
        <Avatar
          icon="pi pi-user"
          class="bg-green-500 text-white"
          shape="circle"
          @click="userMenu.toggle($event)"
        />
        <span class="font-bold"
          >{{ authStore.user?.first_name }} <br />
          {{ authStore.user?.last_name }}</span
        >
        <Menu ref="userMenu" :model="userMenuItems" popup />
      </div>
    </template>
  </div>
</template>
<style></style>
