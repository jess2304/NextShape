<script setup lang="ts">
import { ref } from "vue"
import InputText from "primevue/inputtext"
import InputMask from "primevue/inputmask"
import Password from "primevue/password"
import Button from "primevue/button"
import DatePicker from "primevue/datepicker"
import Toast from "primevue/toast"
import { useToast } from "primevue/usetoast"
import { useAuthStore } from "@/stores/authStore"
import router from "@/router"
import CodeVerificationModalComponent from "@/components/CodeVerificationModalComponent.vue"
import { validateRequiredFields, showToast } from "@/assets/js/utils"

interface RegistrationForm {
  first_name: string | null
  last_name: string | null
  birth_date: Date | null
  email: string | null
  confirmEmail: string | null
  phone_number: string | null
  password: string | null
  confirmPassword: string | null
}

// Constante de la date d'aujourd'hui (contrôle calendrier)
const today = new Date()

// Appel des stores
const toast = useToast()
const authStore = useAuthStore()

// Constante pour faire apparaître la fenêtre modale de vérification de mail.
const showModal = ref(false)
const codeFromUser = ref("")
const loading = ref(false)
// Init des données insérées et invalides
const invalidFields = ref<Record<string, boolean>>({})

// Init du formulaire
const formData = ref<RegistrationForm>({
  first_name: null,
  last_name: null,
  birth_date: null,
  email: null,
  confirmEmail: null,
  phone_number: null,
  password: null,
  confirmPassword: null,
})

// Valider les données et passer l'inscription au Backend
const validateAndProceed = async () => {
  invalidFields.value = {}

  // Checker si les champs obligatoires sont renseignés
  let requiredFields = [
    "first_name",
    "last_name",
    "birth_date",
    "email",
    "confirmEmail",
    "password",
    "confirmPassword",
  ]
  const missingFields = validateRequiredFields(formData.value, requiredFields)
  missingFields.forEach((field: string) => (invalidFields.value[field] = true))
  if (missingFields.length) {
    showToast(
      toast,
      "error",
      "Erreur",
      "Veuillez remplir les champs obligatoires"
    )
    return
  }
  // Checker si les mails sont identiques
  if (formData.value.email !== formData.value.confirmEmail) {
    invalidFields.value.email = true
    invalidFields.value.confirmEmail = true
    return showToast(
      toast,
      "error",
      "Erreur",
      "Les emails ne correspondent pas"
    )
  }

  // Checker si les mots de passes sont identiques
  if (formData.value.password !== formData.value.confirmPassword) {
    invalidFields.value.password = true
    invalidFields.value.confirmPassword = true
    return showToast(
      toast,
      "error",
      "Erreur",
      "Les mots de passe ne correspondent pas"
    )
  }

  // Si tout est validé on passe à l'enregistrement
  await sendCode()
}

const sendCode = async () => {
  try {
    await authStore.sendVerificationCode(formData.value.email, "registration")
    showModal.value = true
    showToast(
      toast,
      "info",
      "Code envoyé",
      "Un email contenant un code vous a été envoyé."
    )
  } catch (err) {
    const detail =
      err?.response?.data?.email?.[0] || "Échec de l'envoi du code."
    showToast(toast, "error", "Erreur", detail)
  } finally {
    loading.value = false
  }
}

const handleCodeValidation = async (code: string) => {
  codeFromUser.value = code
  loading.value = true

  try {
    const response = await authStore.verifyCode(formData.value.email, code)
    if (!response.success) {
      showToast(toast, "error", "Erreur", response.message)
      return
    }
    try {
      await authStore.register(formData.value)
      showToast(
        toast,
        "success",
        "Succès",
        "Votre inscription a été un succès. Bienvenue sur NextShape !"
      )
      resetForm()
      router.push("/connexion")
    } catch (registrationError) {
      showToast(toast, "error", "Erreur", String(registrationError))
    }
  } catch (verificationError) {
    showToast(toast, "error", "Erreur", "Erreur lors de la vérification")
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.value = {
    first_name: null,
    last_name: null,
    birth_date: null,
    email: null,
    confirmEmail: null,
    phone_number: null,
    password: null,
    confirmPassword: null,
  }
  showModal.value = false
}
</script>

<template>
  <div class="card p-4 surface-card shadow-2 border-round-lg w-6 mx-auto">
    <h2 class="text-5xl text-center text-primary">Inscription</h2>
    <div class="formgrid grid">
      <div class="field col-12 md:col-6">
        <label>Prénom *</label>
        <InputText
          class="w-full"
          v-model="formData.first_name"
          placeholder="Votre prénom"
          :invalid="invalidFields.first_name"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Nom *</label>
        <InputText
          class="w-full"
          v-model="formData.last_name"
          placeholder="Votre nom"
          :invalid="invalidFields.last_name"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Date de naissance *</label>
        <DatePicker
          class="w-full"
          v-model="formData.birth_date"
          showIcon
          dateFormat="dd/mm/yy"
          :invalid="invalidFields.birth_date"
          :maxDate="today"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Téléphone</label>
        <InputMask
          id="phone_number"
          v-model="formData.phone_number"
          mask="(+33) 9-99-99-99-99"
          placeholder="(+33) 0-00-00-00-00"
          fluid
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Adresse Email *</label>
        <InputText
          class="w-full"
          type="email"
          v-model="formData.email"
          placeholder="Votre email"
          :invalid="invalidFields.email"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Confirmez votre adresse email *</label>
        <InputText
          class="w-full"
          type="email"
          v-model="formData.confirmEmail"
          placeholder="Confirmez l'email"
          :invalid="invalidFields.confirmEmail"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label for="password">Mot de passe *</label>
        <Password
          class="w-full"
          v-model="formData.password"
          toggleMask
          :invalid="invalidFields.password"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label for="confirmPassword">Confirmez votre mot de passe *</label>
        <Password
          class="w-full"
          v-model="formData.confirmPassword"
          toggleMask
          :invalid="invalidFields.confirmPassword"
        />
      </div>
      <div>
        <Button
          class="mx-2"
          label="Confirmer l'inscription"
          icon="pi pi-arrow-right"
          @click="validateAndProceed"
          :loading="loading"
        />
      </div>
      <CodeVerificationModalComponent
        :visible="showModal"
        @update:visible="showModal = $event"
        @validated="handleCodeValidation"
        @sendBack="sendCode"
      />
    </div>
    <Toast />
  </div>
</template>
<style>
.p-password-input {
  width: 100% !important;
}
</style>
