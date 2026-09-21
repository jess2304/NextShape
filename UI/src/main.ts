import { createApp } from "vue"
import "./style.css"
import App from "./App.vue"
import PrimeVue from "primevue/config"
import Aura from "@primevue/themes/aura"
import "primeicons/primeicons.css"
import Ripple from "primevue/ripple"
import router from "./router"
import axios from "axios"
import ToastService from "primevue/toastservice"
import { createPinia } from "pinia"
import { startSessionSync } from "@/stores/authStore"
import ConfirmationService from "primevue/confirmationservice"

axios.defaults.withCredentials = true

try {
  localStorage.removeItem("auth")
  localStorage.removeItem("coach")
  localStorage.removeItem("progressRecords")
  localStorage.removeItem("progressRecord")
} catch (error) {
  console.warn("Impossible de nettoyer les anciennes données locales.", error)
}

const pinia = createPinia()
const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: "",
    },
  },
})
app.use(pinia)
const stopSessionSync = startSessionSync()
if (import.meta.hot) import.meta.hot.dispose(stopSessionSync)
app.use(router)
app.use(ToastService)
app.use(ConfirmationService)
app.directive("ripple", Ripple)
app.mount("#app")
