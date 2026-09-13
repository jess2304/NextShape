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
import {
  resolveApiErrorMessage,
  showToast,
  validateRequiredFields,
} from "@/assets/js/utils"
import { Credentials } from "@/assets/js/interfaces"

// Initialize credentials and invalid field state.
const credentials = ref<Credentials>({ email: null, password: null })
const invalidFields = ref<Record<string, boolean>>({
  email: false,
  password: false,
})
const resetPasswordVisible = ref(false)

// Store and router
const authStore = useAuthStore()
const toast = useToast()
const router = useRouter()

// Validate input and send login request to the backend.
const validateAndProceed = async () => {
  // Check required fields
  const missingFields = validateRequiredFields(credentials.value, [
    "email",
    "password",
  ])

  // Warn when required fields are missing
  if (missingFields.length) {
    showToast(
      toast,
      "error",
      "Erreur",
      "Veuillez remplir les champs obligatoires"
    )
    return
  }
  // All fields are set, continue with login
  try {
    await authStore.login({
      email: credentials.value.email || "",
      password: credentials.value.password || "",
    })
    const redirectPath = router.currentRoute.value.query.redirect || "/"
    router.push(redirectPath as string)
    credentials.value = { email: null, password: null }
  } catch (error: any) {
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(
        error,
        String(error || "Erreur lors de la connexion")
      )
    )
  }
}

const openResetPasswordModal = () => {
  resetPasswordVisible.value = true
}
</script>

<template>
  <div
    class="card p-4 surface-card shadow-2 border-round-lg w-full md:w-6 mx-auto"
  >
    <h2 class="text-5xl text-center text-primary">Connexion</h2>
    <form class="formgrid grid" @submit.prevent="validateAndProceed">
      <div class="field col-12 md:col-6">
        <label for="email">Adresse Email</label>
        <InputText
          id="email"
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
      <div class="field col-12 flex justify-content-end">
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
