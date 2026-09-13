<script setup lang="ts">
import { ref } from "vue"
import InputText from "primevue/inputtext"
import InputMask from "primevue/inputmask"
import Password from "primevue/password"
import Button from "primevue/button"
import DatePicker from "primevue/datepicker"
import SelectButton from "primevue/selectbutton"
import Toast from "primevue/toast"
import { useToast } from "primevue/usetoast"
import { useAuthStore } from "@/stores/authStore"
import router from "@/router"
import CodeVerificationModalComponent from "@/components/CodeVerificationModalComponent.vue"
import {
  resolveApiErrorMessage,
  resolveApiMessage,
  validateRequiredFields,
  showToast,
} from "@/assets/js/utils"
import { GENDER } from "@/assets/js/constants"
import { RegistrationForm } from "@/assets/js/interfaces"

const today = new Date()

const toast = useToast()
const authStore = useAuthStore()

const showModal = ref(false)
const loading = ref(false)
const invalidFields = ref<Record<string, boolean>>({})

const formData = ref<RegistrationForm>({
  first_name: null,
  last_name: null,
  gender: "H",
  birth_date: null,
  email: null,
  confirmEmail: null,
  phone_number: null,
  password: null,
  confirmPassword: null,
})

const validateAndProceed = async () => {
  invalidFields.value = {}

  const requiredFields = [
    "first_name",
    "last_name",
    "gender",
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

  if (formData.value.email !== formData.value.confirmEmail) {
    invalidFields.value.email = true
    invalidFields.value.confirmEmail = true
    showToast(toast, "error", "Erreur", "Les emails ne correspondent pas")
    return
  }

  if (formData.value.password !== formData.value.confirmPassword) {
    invalidFields.value.password = true
    invalidFields.value.confirmPassword = true
    showToast(
      toast,
      "error",
      "Erreur",
      "Les mots de passe ne correspondent pas"
    )
    return
  }

  await sendCode()
}

const sendCode = async () => {
  loading.value = true
  try {
    const response = await authStore.sendVerificationCode(
      formData.value.email || "",
      "registration"
    )
    showModal.value = true
    showToast(
      toast,
      "info",
      "Code envoyé",
      resolveApiMessage(
        response,
        "Un email contenant un code vous a été envoyé."
      )
    )
  } catch (err: any) {
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(err, String(err || "Échec de l'envoi du code."))
    )
  } finally {
    loading.value = false
  }
}

const handleCodeValidation = async (code: string) => {
  loading.value = true

  try {
    const verification = await authStore.verifyCode(
      formData.value.email || "",
      code
    )
    if (!verification.success) {
      showToast(toast, "error", "Erreur", resolveApiMessage(verification))
      return
    }

    const registration = await authStore.register(formData.value)
    showToast(
      toast,
      "success",
      "Succès",
      resolveApiMessage(registration, "Votre inscription a été un succès.")
    )
    resetForm()
    router.push("/connexion")
  } catch (error: any) {
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(
        error,
        String(error || "Erreur lors de la vérification")
      )
    )
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.value = {
    first_name: null,
    last_name: null,
    gender: "H",
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
  <div
    class="card p-4 surface-card shadow-2 border-round-lg w-full md:w-6 mx-auto"
  >
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
        <label>Genre*</label>
        <SelectButton
          class="w-full"
          v-model="formData.gender"
          :invalid="invalidFields.gender"
          :options="GENDER"
          optionLabel="label"
          optionValue="value"
          defaultValue="H"
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
        <label for="email">Adresse Email *</label>
        <InputText
          class="w-full"
          id="email"
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
      <CodeVerificationModalComponent
        :visible="showModal"
        @update:visible="showModal = $event"
        @validated="handleCodeValidation"
        @sendBack="sendCode"
      />
    </div>
    <Toast />
    <div>
      <Button
        label="Confirmer l'inscription"
        icon="pi pi-arrow-right"
        @click="validateAndProceed"
        :loading="loading"
      />
    </div>
  </div>
</template>
<style>
.p-password-input {
  width: 100% !important;
}
</style>
