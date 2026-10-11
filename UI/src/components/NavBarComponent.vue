<script setup lang="ts">
import { ref, watch } from "vue"
import { useRoute } from "vue-router"
import BrandMark from "@/components/layout/BrandMark.vue"
import NavBarConnexionComponent from "@/components/NavBarConnexionComponent.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsDrawer from "@/components/ui/NsDrawer.vue"

const route = useRoute()
const menuOpen = ref(false)
watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
  }
)
const links = [
  { to: "/", label: "Accueil" },
  { to: "/calculatrice-imc", label: "Mon IMC" },
  { to: "/calculatrice-calories", label: "Mes calories" },
  { to: "/contact", label: "Contact" },
]
</script>

<template>
  <div class="public-nav">
    <BrandMark />
    <nav class="public-nav__links" aria-label="Navigation principale">
      <RouterLink v-for="link in links" :key="link.to" :to="link.to">{{
        link.label
      }}</RouterLink>
    </nav>
    <div class="public-nav__account"><NavBarConnexionComponent /></div>
    <NsButton
      class="public-nav__toggle"
      icon="pi pi-bars"
      text
      severity="secondary"
      aria-label="Ouvrir le menu"
      aria-controls="public-mobile-menu"
      :aria-expanded="menuOpen"
      @click="menuOpen = true"
    />
  </div>
  <NsDrawer
    id="public-mobile-menu"
    v-model:visible="menuOpen"
    header="NextShape"
    position="right"
  >
    <nav class="side-nav" aria-label="Navigation mobile">
      <RouterLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        @click="menuOpen = false"
        >{{ link.label }}</RouterLink
      >
      <RouterLink to="/connexion" @click="menuOpen = false"
        >Se connecter</RouterLink
      >
      <RouterLink to="/inscription" @click="menuOpen = false"
        >Créer mon compte</RouterLink
      >
    </nav>
  </NsDrawer>
</template>

<style scoped>
.public-nav {
  max-width: 1280px;
  margin: 0 auto;
  min-height: 88px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1rem 2.5rem;
}
.public-nav__links {
  display: flex;
  align-items: center;
  gap: 1.75rem;
}
.public-nav__links a {
  color: var(--ns-muted);
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.6rem 0;
  border-bottom: 2px solid transparent;
}
.public-nav__links a:hover,
.public-nav__links a.router-link-exact-active {
  color: var(--ns-primary);
}
.public-nav__links a.router-link-exact-active {
  border-color: var(--ns-primary);
}
.public-nav__toggle {
  display: none;
}
@media (max-width: 1000px) {
  .public-nav {
    gap: 1rem;
    padding-inline: 1.5rem;
  }
  .public-nav__links {
    gap: 1rem;
  }
}
@media (max-width: 800px) {
  .public-nav {
    min-height: 76px;
    padding: 1rem;
  }
  .public-nav__links,
  .public-nav__account {
    display: none;
  }
  .public-nav__toggle {
    display: inline-flex;
  }
}
</style>
