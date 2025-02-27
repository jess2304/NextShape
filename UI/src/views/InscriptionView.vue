<script setup lang="ts">
import { ref } from "vue"
import InputText from "primevue/inputtext"
import InputMask from "primevue/inputmask"
import Password from "primevue/password"
import Button from "primevue/button"
import Calendar from "primevue/calendar"
import Toast from "primevue/toast"
import { useToast } from "primevue/usetoast"
import { useAuthStore } from "@/stores/authStore"

const toast = useToast()
const authStore = useAuthStore()

const formData = ref({
  firstName: null,
  lastName: null,
  birthDate: null,
  email: null,
  confirmEmail: null,
  phone: null,
  password: null,
  confirmPassword: null,
})

const invalidData = ref({
  firstName: false,
  lastName: false,
  birthDate: false,
  email: false,
  confirmEmail: false,
  password: false,
  confirmPassword: false,
})

const validateAndProceed = async () => {
  Object.keys(invalidData.value).forEach(
    (key) => (invalidData.value[key] = false)
  )

  // Checker si les champs obligatoires sont renseignés
  let requiredHasError = false
  let requiredFields = [
    "firstName",
    "lastName",
    "birthDate",
    "email",
    "confirmEmail",
    "password",
    "confirmPassword",
  ]
  requiredFields.forEach((field) => {
    if (!formData.value[field]) {
      invalidData.value[field] = true
      requiredHasError = true
    }
  })

  if (requiredHasError) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Veuillez remplir les champs obligatoires",
      life: 5000,
    })
  }

  // Checker si les mails sont identiques
  if (formData.value.email !== formData.value.confirmEmail) {
    invalidData.value.email = true
    invalidData.value.confirmEmail = true
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Les emails ne correspondent pas",
      life: 5000,
    })
  }

  // Checker si les mots de passes sont identiques
  if (formData.value.password !== formData.value.confirmPassword) {
    invalidData.value.password = true
    invalidData.value.confirmPassword = true
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Les mots de passe ne correspondent pas",
      life: 5000,
    })
  }

  // Si tout est validé on passe à l'enregistrement
  if (
    !requiredHasError &&
    formData.value.email == formData.value.confirmEmail &&
    formData.value.password == formData.value.confirmPassword
  ) {
    try {
      await authStore.register(formData.value)
      toast.add({
        severity: "success",
        summary: "Inscription finalisée",
        detail: "Félicitation ! Vous êtes inscrit à NextShape.",
        life: 5000,
      })
      formData.value = {
        firstName: null,
        lastName: null,
        birthDate: null,
        email: null,
        confirmEmail: null,
        phone: null,
        password: null,
        confirmPassword: null,
      }
    } catch (error) {
      toast.add({
        severity: "error",
        summary: "Erreur Lors de l'inscription",
        detail: String(error),
        life: 5000,
      })
    }
  }
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
          v-model="formData.firstName"
          placeholder="Votre prénom"
          :invalid="invalidData.firstName"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Nom *</label>
        <InputText
          class="w-full"
          v-model="formData.lastName"
          placeholder="Votre nom"
          :invalid="invalidData.lastName"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Date de naissance *</label>
        <Calendar
          class="w-full"
          v-model="formData.birthDate"
          showIcon
          dateFormat="dd/mm/yy"
          :invalid="invalidData.birthDate"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Téléphone</label>
        <InputMask
          id="phone"
          v-model="formData.phone"
          mask="(+33) 9-99-99-99-99"
          placeholder="(+33) 0-00-00-00-00"
          fluid
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Email *</label>
        <InputText
          class="w-full"
          type="email"
          v-model="formData.email"
          placeholder="Votre email"
          :invalid="invalidData.email"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Confirmez votre email *</label>
        <InputText
          class="w-full"
          type="email"
          v-model="formData.confirmEmail"
          placeholder="Confirmez l'email"
          :invalid="invalidData.confirmEmail"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label for="password">Mot de passe *</label>
        <Password
          class="w-full"
          v-model="formData.password"
          toggleMask
          :invalid="invalidData.password"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label for="confirmPassword">Confirmer Mot de passe *</label>
        <Password
          class="w-full"
          v-model="formData.confirmPassword"
          toggleMask
          :invalid="invalidData.confirmPassword"
        />
      </div>
      <div>
        <Button
          class="mx-2"
          label="Confirmer l'inscription"
          icon="pi pi-arrow-right"
          @click="validateAndProceed"
        />
      </div>
    </div>

    <Toast />
  </div>
</template>
<style>
.p-password-input {
  width: 100% !important;
}
</style>
