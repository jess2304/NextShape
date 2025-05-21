<script setup>
import { ref } from "vue"
import Dialog from "primevue/dialog"
import Button from "primevue/button"
import InputText from "primevue/inputtext"
import InputOtp from "primevue/inputotp"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import { showToast } from "@/assets/js/utils"

const props = defineProps({
  visible: Boolean,
})

const emits = defineEmits(["update:visible", "validated", "cancelled"])

const authStore = useAuthStore()
const toast = useToast()

// Étape 1 : email | Étape 2 : code | Étape 3 : nouveau mot de passe
const step = ref(1)
const email = ref("")
const code = ref("")
const newPassword = ref("")
const confirmPassword = ref("")
const loading = ref(false)
const invalidFields = ref({
  email: false,
  code: false,
  newPassword: false,
  confirmPassword: false,
})

// Fermer le modal
const closeModal = () => {
  step.value = 1
  email.value = ""
  code.value = ""
  newPassword.value = ""
  confirmPassword.value = ""
  emits("update:visible", false)
  emits("cancelled")
}

// Envoi du code vers l'email
const sendCode = async () => {
  // Vérifier si une adresse mail a été entrée
  invalidFields.value.email = false
  if (!email.value) {
    invalidFields.value.email = true
    showToast(toast, "error", "Erreur", "Veuillez entrer votre adresse e-mail")
    return
  }
  loading.value = true

  // Envoyer le code de vérification
  try {
    await authStore.sendVerificationCode(email.value, "reset-password")
    step.value = 2
    showToast(
      toast,
      "info",
      "Code envoyé",
      "Un code vous a été envoyé par e-mail."
    )
  } catch (err) {
    const detail =
      err?.response?.data?.email?.[0] ||
      "Échec de l'envoi du code. Veuillez réessayer."
    showToast(toast, "error", "Erreur", detail)
  } finally {
    loading.value = false
  }
}

// Vérification du code
const verifyCode = async () => {
  invalidFields.value.code = false
  // Vérifier que le code est bien inséré et qu'il a 6 chiffres
  if (!code.value || code.value.length !== 6) {
    invalidFields.value.code = true
    showToast(toast, "error", "Erreur", "Veuillez entrer un code valide")
    return
  }
  loading.value = true

  // Vérifier le code
  try {
    const response = await authStore.verifyCode(email.value, code.value)
    if (response.success) {
      step.value = 3
      showToast(toast, "success", "Succès", response.message)
    } else {
      showToast(toast, "error", "Erreur", response.message)
    }
  } catch {
    showToast(toast, "error", "Erreur", "Erreur lors de la vérification")
  } finally {
    loading.value = false
  }
}

const updatePassword = async () => {
  invalidFields.value.newPassword = false
  invalidFields.value.confirmPassword = false

  if (!newPassword.value || !confirmPassword.value) {
    invalidFields.value.newPassword = !newPassword.value
    invalidFields.value.confirmPassword = !confirmPassword.value
    showToast(toast, "error", "Erreur", "Veuillez remplir les deux champs")
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    invalidFields.value.newPassword = true
    invalidFields.value.confirmPassword = true
    showToast(
      toast,
      "error",
      "Erreur",
      "Les mots de passe ne correspondent pas."
    )
    return
  }
  loading.value = true

  // Remettre à jour le mot de passe
  try {
    const response = await authStore.resetPassword(
      email.value,
      newPassword.value,
      code.value
    )
    showToast(toast, "success", "Succès", response.message)
    emits("validated", { email: email.value })
    closeModal()
  } catch (err) {
    showToast(
      toast,
      "error",
      "Erreur",
      "Erreur lors de la mise à jour du mot de passe."
    )
  } finally {
    loading.value = false
  }
}

const cancel = () => {
  step.value = 1
  email.value = ""
  code.value = ""
  newPassword.value = ""
  confirmPassword.value = ""
  emits("cancelled")
  emits("update:visible", false)
}
</script>

<template>
  <Dialog
    v-model:visible="props.visible"
    header="Réinitialisation du mot de passe"
    :modal="true"
    :closable="false"
  >
    <div v-if="step === 1">
      <div class="field">
        <label for="email">Adresse Email</label>
        <InputText
          id="email"
          type="email"
          v-model="email"
          autocomplete="email"
          class="w-full"
          :invalid="invalidFields.email"
        />
      </div>
      <div class="flex justify-content-end mt-3 gap-2">
        <Button label="Annuler" severity="secondary" @click="cancel" />
        <Button
          type="submit"
          label="Envoyer le code"
          :loading="loading"
          @click="sendCode"
        />
      </div>
    </div>

    <div v-else-if="step === 2">
      <div class="field">
        <label for="code">Entrez le code reçu par email :</label>
        <InputOtp
          id="code"
          v-model="code"
          integerOnly
          size="small"
          :length="6"
          :invalid="invalidFields.code"
        />
      </div>
      <div class="flex justify-content-end mt-3 gap-2">
        <Button label="Retour" severity="secondary" @click="() => (step = 1)" />
        <Button
          label="Valider le code"
          :loading="loading"
          @click="verifyCode"
        />
      </div>
    </div>

    <div v-else-if="step === 3">
      <div class="field">
        <label for="newPassword">Nouveau mot de passe</label>
        <InputText
          id="newPassword"
          type="password"
          v-model="newPassword"
          class="w-full"
          autocomplete="new-password"
          :invalid="invalidFields.newPassword"
        />
      </div>
      <div class="field">
        <label for="confirmPassword">Confirmez le mot de passe</label>
        <InputText
          id="confirmPassword"
          type="password"
          v-model="confirmPassword"
          class="w-full"
          autocomplete="new-password"
          :invalid="invalidFields.confirmPassword"
        />
      </div>
      <div class="flex justify-content-end mt-3 gap-2">
        <Button label="Annuler" severity="secondary" @click="cancel" />
        <Button
          label="Mettre à jour"
          :loading="loading"
          @click="updatePassword"
        />
      </div>
    </div>
  </Dialog>
</template>
