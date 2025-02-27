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

const routes = [
  { path: "/", name: "home", component: HomeView },
  {
    path: "/calculatrice-imc",
    name: "calculatrice-imc",
    component: CalculatriceIMCView,
  },
  {
    path: "/calculatrice-calories",
    name: "calculatrice-calories",
    component: CalculatriceCaloriesView,
  },
  { path: "/historique", name: "historique", component: HistoriqueView },
  { path: "/evolution", name: "evolution", component: EvolutionView },
  { path: "/contact", name: "contact", component: ContactView },
  { path: "/inscription", component: InscriptionView },
  { path: "/connexion", component: ConnexionView },
  { path: "/:pathMatch(.*)*", component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
