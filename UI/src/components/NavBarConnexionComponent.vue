<script setup lang="ts">
import { isCancel } from "axios"
import Menu from "primevue/menu"
import NsButton from "@/components/ui/NsButton.vue"
import { useRouter } from "vue-router"
import { ref, computed } from "vue"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"

const router = useRouter()
const toast = useToast()

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.user !== null)

const userMenu = ref()
const menuOpen = ref(false)
const initials = computed(
  () =>
    `${authStore.user?.first_name?.[0] ?? ""}${
      authStore.user?.last_name?.[0] ?? ""
    }`.toUpperCase() || "NS"
)

const userMenuItems = computed(() => [
  {
    label: "Profil",
    icon: "pi pi-user",
    command: () => router.push("/profil"),
  },
  {
    label: "Déconnexion",
    icon: "pi pi-sign-out",
    command: async () => {
      try {
        await authStore.logout()
      } catch (error) {
        if (isCancel(error)) return
        toast.add({
          severity: "error",
          summary: "Déconnexion impossible",
          detail:
            "La déconnexion n'a pas pu être confirmée. Réessaie quand le serveur est accessible.",
          life: 5000,
        })
      }
    },
  },
])
</script>
<template>
  <div class="account-nav">
    <template v-if="!isLoggedIn">
      <NsButton
        as="router-link"
        to="/connexion"
        label="Connexion"
        text
        severity="secondary"
      />
      <NsButton
        as="router-link"
        to="/inscription"
        label="Commencer"
        icon="pi pi-arrow-up-right"
        iconPos="right"
      />
    </template>
    <template v-else>
      <button
        type="button"
        class="account-button"
        aria-label="Menu de mon compte"
        aria-haspopup="menu"
        aria-controls="account-menu"
        :aria-expanded="menuOpen"
        @click="userMenu.toggle($event)"
      >
        <span class="account-button__avatar" aria-hidden="true">{{
          initials
        }}</span>
        <span class="account-button__name"
          >{{ authStore.user?.first_name }}
          {{ authStore.user?.last_name }}</span
        >
        <i class="pi pi-angle-down" aria-hidden="true" />
      </button>
      <Menu
        id="account-menu"
        ref="userMenu"
        :model="userMenuItems"
        popup
        @show="menuOpen = true"
        @hide="menuOpen = false"
      />
    </template>
  </div>
</template>

<style scoped>
.account-nav {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.account-nav :deep(.p-button) {
  font-size: 0.8rem;
}
.account-button {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.3rem 0.45rem;
  max-width: 280px;
  background: transparent;
  border: 0;
  border-radius: 8px;
  color: var(--ns-ink);
  cursor: pointer;
}
.account-button:hover {
  background: var(--ns-sage);
}
.account-button__avatar {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  background: var(--ns-sage);
  color: var(--ns-primary);
  font-size: 0.75rem;
  border: 1px solid #d4dfd5;
  border-radius: 50%;
  font-weight: 600;
}
.account-button__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8rem;
  font-weight: 500;
}
.account-button > .pi {
  font-size: 0.75rem;
  color: var(--ns-muted);
}
@media (max-width: 600px) {
  .account-button__name {
    display: none;
  }
  .account-button {
    gap: 0.4rem;
  }
}
</style>
