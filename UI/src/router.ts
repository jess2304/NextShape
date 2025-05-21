import { createWebHistory, createRouter } from "vue-router"

import HomeView from "@/views/HomeView.vue"
import CalculatriceIMCView from "@/views/CalculatriceIMCView.vue"
import CalculatriceCaloriesView from "@/views/CalculatriceCaloriesView.vue"
import HistoriqueView from "@/views/HistoriqueView.vue"
import EvolutionView from "@/views/EvolutionView.vue"
import ContactView from "@/views/ContactView.vue"
import NotFoundView from "@/views/NotFoundView.vue"
import ConnexionView from "@/views/ConnexionView.vue"
import InscriptionView from "@/views/InscriptionView.vue"
import ProfilView from "@/views/ProfilView.vue"
import { useAuthStore } from "@/stores/authStore"

const routes = [
  { path: "/", name: "home", component: HomeView },
  {
    path: "/calculatrice-imc",
    name: "calculatrice-imc",
    component: CalculatriceIMCView,
    meta: { requiresAuth: true },
  },
  {
    path: "/calculatrice-calories",
    name: "calculatrice-calories",
    component: CalculatriceCaloriesView,
    meta: { requiresAuth: true },
  },
  {
    path: "/historique",
    name: "historique",
    component: HistoriqueView,
    meta: { requiresAuth: true },
  },

  {
    path: "/evolution",
    name: "evolution",
    component: EvolutionView,
    meta: { requiresAuth: true },
  },
  { path: "/contact", name: "contact", component: ContactView },
  { path: "/inscription", component: InscriptionView },
  { path: "/connexion", component: ConnexionView },
  { path: "/profil", component: ProfilView, meta: { requiresAuth: true } },
  { path: "/:pathMatch(.*)*", component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Protection des routes privées
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.token) {
    next({ path: "/connexion", query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
