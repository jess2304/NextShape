<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import InputText from "primevue/inputtext"
import Password from "primevue/password"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import Button from "primevue/button"
import Toast from "primevue/toast"
import ResetPasswordModalComponent from "@/components/ResetPasswordModalComponent.vue"
import { showToast, validateRequiredFields } from "@/assets/js/utils"

interface Credentials {
  email: string | null
  password: string | null
}

// Initialisation des credentials et les données invalides.
const credentials = ref<Credentials>({ email: null, password: null })
const invalidFields = ref<Record<string, boolean>>({
  email: false,
  password: false,
})
const resetPasswordVisible = ref(false)

// Appel des stores et des routers
const authStore = useAuthStore()
const toast = useToast()
const router = useRouter()

// Valider l'insertion et passer la connexion au Backend.
const validateAndProceed = async () => {
  // Checker si les champs obligatoires sont renseignés
  const missingFields = validateRequiredFields(credentials.value, [
    "email",
    "password",
  ])

  // Alerte champs obligatoires
  if (missingFields.length) {
    showToast(
      toast,
      "error",
      "Erreur",
      "Veuillez remplir les champs obligatoires"
    )
    return
  }
  // Tout est reseigné, on passe à la connexion
  try {
    await authStore.login({
      email: credentials.value.email || "",
      password: credentials.value.password || "",
    })
    const redirectPath = router.currentRoute.value.query.redirect || "/"
    router.push(redirectPath as string)
    credentials.value = { email: null, password: null }
  } catch (error) {
    showToast(toast, "error", "Erreur lors de la connexion")
  }
}

const openResetPasswordModal = () => {
  resetPasswordVisible.value = true
}
</script>

<template>
  <div class="card p-4 surface-card shadow-2 border-round-lg w-6 mx-auto">
    <h2 class="text-5xl text-center text-primary">Connexion</h2>
    <form class="formgrid grid" @submit.prevent="validateAndProceed">
      <div class="field col-12 md:col-6">
        <label>Adresse Email</label>
        <InputText
          class="w-full"
          type="email"
          v-model="credentials.email"
          placeholder="Votre email"
          :invalid="invalidFields.email"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label for="password">Mot de passe</label>
        <Password
          class="w-full"
          v-model="credentials.password"
          :invalid="invalidFields.password"
          :feedback="false"
        />
        <a
          @click="openResetPasswordModal"
          class="text-sm text-primary cursor-pointer"
          >Mot de passe oublié ?</a
        >
      </div>
      <div>
        <Button
          class="mx-2"
          label="Se connecter"
          icon="pi pi-arrow-right"
          type="submit"
        />
      </div>
      <ResetPasswordModalComponent
        :visible="resetPasswordVisible"
        @update:visible="resetPasswordVisible = $event"
      />
    </form>
    <Toast />
  </div>
</template>
