import { createApp } from "vue"
import "./style.css"
import App from "./App.vue"
import PrimeVue from "primevue/config"
import Aura from "@primevue/themes/aura"
import "primeicons/primeicons.css"
import Ripple from "primevue/ripple"
import router from "./router"
import ToastService from "primevue/toastservice"
import { createPinia } from "pinia"

const pinia = createPinia()
const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
})
app.use(router)
app.use(ToastService)
app.use(pinia)
app.directive("ripple", Ripple)
app.mount("#app")
