<script setup lang="ts">
import { isCancel } from "axios"
import { ref } from "vue"
import { useRouter } from "vue-router"
import NsInput from "@/components/ui/NsInput.vue"
import NsPasswordInput from "@/components/ui/NsPasswordInput.vue"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import NsButton from "@/components/ui/NsButton.vue"
import NsCard from "@/components/ui/NsCard.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
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
    if (isCancel(error)) return
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
  <section class="auth-page">
    <div class="auth-intro">
      <span class="eyebrow">VOTRE ESPACE NEXTSHAPE</span>
      <h1>Heureux de vous retrouver.</h1>
      <p>Vos repères, votre progression, votre rythme.</p>
    </div>
    <NsCard class="login-card">
      <h2>Connexion</h2>
      <p class="card-description">
        Connectez-vous pour poursuivre votre parcours.
      </p>
      <form class="login-form" @submit.prevent="validateAndProceed" novalidate>
        <NsFormField id="login-email" label="Adresse e-mail" required>
          <NsInput
            id="login-email"
            v-model="credentials.email"
            type="email"
            autocomplete="email"
            placeholder="vous@exemple.fr"
            :invalid="invalidFields.email"
            fluid
          />
        </NsFormField>
        <NsFormField id="login-password" label="Mot de passe" required>
          <NsPasswordInput
            inputId="login-password"
            v-model="credentials.password"
            :inputProps="{ autocomplete: 'current-password' }"
            :invalid="invalidFields.password"
            :feedback="false"
            toggleMask
            fluid
          />
        </NsFormField>
        <button
          type="button"
          class="text-link forgot-link"
          @click="openResetPasswordModal"
        >
          Mot de passe oublié ?
        </button>
        <NsButton
          class="submit-button"
          label="Se connecter"
          icon="pi pi-arrow-right"
          iconPos="right"
          type="submit"
        />
      </form>
      <p class="auth-switch">
        Pas encore de compte ?
        <RouterLink to="/inscription">Créer mon compte</RouterLink>
      </p>
    </NsCard>
    <ResetPasswordModalComponent
      :visible="resetPasswordVisible"
      @update:visible="resetPasswordVisible = $event"
    />
  </section>
</template>

<style scoped>
.auth-page {
  width: min(100%, 470px);
  margin: 0 auto;
  padding: clamp(1rem, 5vw, 3rem) 0;
}
.auth-intro {
  text-align: center;
  margin-bottom: 2rem;
}
.eyebrow {
  color: #1d4d40;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
}
h1 {
  margin: 0.8rem 0;
  font-size: clamp(1.8rem, 4vw, 2.25rem);
  line-height: 1.2;
  letter-spacing: -0.045em;
}
.auth-intro p,
.card-description,
.auth-switch {
  color: #69766f;
  font-size: 0.92rem;
  line-height: 1.65;
}
.login-card {
  padding: clamp(1.4rem, 4vw, 2.25rem);
}
h2 {
  margin: 0;
  font-size: 1.25rem;
  letter-spacing: -0.025em;
}
.card-description {
  margin: 0.4rem 0 1.7rem;
}
.login-form {
  display: grid;
  gap: 1.2rem;
}
.text-link {
  padding: 0;
  border: 0;
  background: none;
  color: #1d4d40;
  font: inherit;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.forgot-link {
  justify-self: end;
  margin-top: -0.4rem;
}
.submit-button {
  width: 100%;
  margin-top: 0.35rem;
}
.auth-switch {
  text-align: center;
  margin: 1.6rem 0 0;
  padding-top: 1.4rem;
  border-top: 1px solid #e7ebe5;
  font-size: 0.82rem;
}
.auth-switch a {
  color: #1d4d40;
  font-weight: 600;
  text-underline-offset: 3px;
}
</style>
