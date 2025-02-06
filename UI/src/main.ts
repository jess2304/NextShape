import { createApp } from "vue"
import "./style.css"
import App from "./App.vue"
import PrimeVue from "primevue/config"
import Aura from "@primevue/themes/aura"
import "primeicons/primeicons.css"
import Ripple from "primevue/ripple"
import router from "./router"

const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
})
app.use(router)
app.directive("ripple", Ripple)
app.mount("#app")
