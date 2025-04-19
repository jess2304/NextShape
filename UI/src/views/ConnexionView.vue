<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import InputText from "primevue/inputtext"
import Password from "primevue/password"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import Button from "primevue/button"
import Toast from "primevue/toast"

// Initialisation des credentials et les données invalides.
const credentials = ref({ email: null, password: null })
const invalidData = ref({ email: false, password: false })

// Appel des stores et des routers
const authStore = useAuthStore()
const toast = useToast()
const router = useRouter()

// Valider l'insertion et passer la connexion au Backend.
const validateAndProceed = async () => {
  Object.keys(invalidData.value).forEach(
    (key) => (invalidData.value[key] = false)
  )

  // Checker si les champs obligatoires sont renseignés
  let requiredHasError = false
  let requiredFields = ["email", "password"]
  requiredFields.forEach((field) => {
    if (!credentials.value[field]) {
      invalidData.value[field] = true
      requiredHasError = true
    }
  })
  // Alerte champs obligatoires
  if (requiredHasError) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Veuillez remplir les champs obligatoires",
      life: 5000,
    })
  }
  // Si tout est validé on passe à la connexion
  if (!requiredHasError) {
    try {
      await authStore.login(credentials.value)
      router.push("/")
      credentials.value = { email: null, password: null }
    } catch (error) {
      toast.add({
        severity: "error",
        summary: "Erreur Lors de la connexion",
        life: 5000,
      })
    }
  }
}
</script>

<template>
  <div class="card p-4 surface-card shadow-2 border-round-lg w-6 mx-auto">
    <h2 class="text-5xl text-center text-primary">Connexion</h2>
    <form class="formgrid grid" @submit.prevent="validateAndProceed">
      <div class="field col-12 md:col-6">
        <label>Email</label>
        <InputText
          class="w-full"
          type="email"
          v-model="credentials.email"
          placeholder="Votre email"
          :invalid="invalidData.email"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label for="password">Mot de passe</label>
        <Password
          class="w-full"
          v-model="credentials.password"
          :invalid="invalidData.password"
          :feedback="false"
        />
      </div>
      <div>
        <Button
          class="mx-2"
          label="Se connecter"
          icon="pi pi-arrow-right"
          type="submit"
        />
      </div>
    </form>
    <Toast />
  </div>
</template>
