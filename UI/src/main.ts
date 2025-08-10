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
import piniaPluginPersistedstate from "pinia-plugin-persistedstate"
import ConfirmationService from "primevue/confirmationservice"

axios.defaults.withCredentials = true

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: "",
    },
  },
})
app.use(router)
app.use(ToastService)
app.use(pinia)
app.use(ConfirmationService)
app.directive("ripple", Ripple)
app.mount("#app")
