<script setup lang="ts">
import { ref, watch } from "vue"
import { useRoute } from "vue-router"
import BrandMark from "./BrandMark.vue"
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
  {
    to: "/calculatrice-calories",
    label: "Mes calories",
    icon: "pi pi-calculator",
  },
  { to: "/historique", label: "Mon historique", icon: "pi pi-history" },
  { to: "/evolution", label: "Mon programme", icon: "pi pi-sparkles" },
  { to: "/calculatrice-imc", label: "Mon IMC", icon: "pi pi-chart-bar" },
]
const mobileLinks = [
  { to: "/calculatrice-calories", label: "Calories", icon: "pi pi-calculator" },
  { to: "/historique", label: "Historique", icon: "pi pi-history" },
  { to: "/evolution", label: "Programme", icon: "pi pi-sparkles" },
  { to: "/profil", label: "Profil", icon: "pi pi-user" },
]
</script>

<template>
  <div class="app-layout">
    <aside class="app-sidebar" aria-label="Menu principal">
      <BrandMark />
      <div class="app-sidebar__nav">
        <p class="nav-caption">Mon espace</p>
        <nav class="side-nav" aria-label="Outils NextShape">
          <RouterLink v-for="link in links" :key="link.to" :to="link.to"
            ><i :class="link.icon" aria-hidden="true" /><span>{{
              link.label
            }}</span></RouterLink
          >
        </nav>
      </div>
      <div class="app-sidebar__bottom">
        <div class="sidebar-note">
          <span class="pi pi-sun" aria-hidden="true" />
          <p>Un pas à la fois.<br /><strong>À votre rythme.</strong></p>
        </div>
        <nav class="side-nav" aria-label="Liens utiles">
          <RouterLink to="/"
            ><i class="pi pi-home" aria-hidden="true" />Accueil</RouterLink
          >
          <RouterLink to="/contact"
            ><i class="pi pi-comment" aria-hidden="true" />Nous
            contacter</RouterLink
          >
        </nav>
      </div>
    </aside>

    <div class="app-workspace">
      <header class="app-topbar">
        <div class="app-topbar__mobile">
          <NsButton
            icon="pi pi-bars"
            text
            severity="secondary"
            aria-label="Ouvrir le menu"
            aria-controls="app-mobile-menu"
            :aria-expanded="menuOpen"
            @click="menuOpen = true"
          /><BrandMark />
        </div>
        <span class="app-topbar__label">Votre espace NextShape</span>
        <NavBarConnexionComponent />
      </header>
      <main id="main-content" class="app-content" tabindex="-1"><slot /></main>
      <footer class="app-footer">NextShape · Avancer, à votre rythme.</footer>
    </div>

    <nav class="mobile-tabbar" aria-label="Navigation principale">
      <RouterLink v-for="link in mobileLinks" :key="link.to" :to="link.to"
        ><i :class="link.icon" aria-hidden="true" /><span>{{
          link.label
        }}</span></RouterLink
      >
    </nav>
    <NsDrawer
      id="app-mobile-menu"
      v-model:visible="menuOpen"
      header="Votre espace"
    >
      <nav class="side-nav" aria-label="Tous les liens">
        <RouterLink to="/" @click="menuOpen = false"
          ><i class="pi pi-home" aria-hidden="true" />Accueil</RouterLink
        >
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          @click="menuOpen = false"
          ><i :class="link.icon" aria-hidden="true" />{{
            link.label
          }}</RouterLink
        >
        <RouterLink to="/profil" @click="menuOpen = false"
          ><i class="pi pi-user" aria-hidden="true" />Mon profil</RouterLink
        >
        <RouterLink to="/contact" @click="menuOpen = false"
          ><i class="pi pi-comment" aria-hidden="true" />Nous
          contacter</RouterLink
        >
      </nav>
    </NsDrawer>
  </div>
</template>
