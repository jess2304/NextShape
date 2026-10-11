<script setup lang="ts">
import { isCancel } from "axios"
import { ref } from "vue"
import NsDialog from "@/components/ui/NsDialog.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsInput from "@/components/ui/NsInput.vue"
import NsPasswordInput from "@/components/ui/NsPasswordInput.vue"
import NsInputOtp from "@/components/ui/NsInputOtp.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import {
  resolveApiErrorMessage,
  resolveApiMessage,
  showToast,
} from "@/assets/js/utils"

const props = defineProps({
  visible: Boolean,
})

const emits = defineEmits(["update:visible", "validated", "cancelled"])

const authStore = useAuthStore()
const toast = useToast()

// Step 1: email | Step 2: code | Step 3: new password
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

// Close modal
const closeModal = () => {
  step.value = 1
  email.value = ""
  code.value = ""
  newPassword.value = ""
  confirmPassword.value = ""
  emits("update:visible", false)
  emits("cancelled")
}

// Send the code by email
const sendCode = async () => {
  // Ensure an email address was entered
  invalidFields.value.email = false
  if (!email.value) {
    invalidFields.value.email = true
    showToast(toast, "error", "Erreur", "Veuillez entrer votre adresse e-mail")
    return
  }
  loading.value = true

  // Send verification code
  try {
    const response = await authStore.sendVerificationCode(
      email.value,
      "reset-password"
    )
    step.value = 2
    showToast(
      toast,
      "info",
      "Code envoyé",
      resolveApiMessage(response, "Un code vous a été envoyé par e-mail.")
    )
  } catch (err: any) {
    if (isCancel(err)) return
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

const verifyCode = async () => {
  invalidFields.value.code = false
  if (!code.value || code.value.length !== 6) {
    invalidFields.value.code = true
    showToast(toast, "error", "Erreur", "Veuillez entrer un code valide")
    return
  }
  loading.value = true

  try {
    const response = await authStore.verifyCode(email.value, code.value)
    if (response.success) {
      step.value = 3
      showToast(toast, "success", "Succès", resolveApiMessage(response))
    } else {
      showToast(toast, "error", "Erreur", resolveApiMessage(response))
    }
  } catch (error: any) {
    if (isCancel(error)) return
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

  try {
    const response = await authStore.resetPassword(
      email.value,
      newPassword.value,
      code.value
    )
    showToast(toast, "success", "Succès", resolveApiMessage(response))
    emits("validated", { email: email.value })
    closeModal()
  } catch (err: any) {
    if (isCancel(err)) return
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(
        err,
        String(err || "Erreur lors de la mise à jour du mot de passe.")
      )
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
  <NsDialog
    :visible="props.visible"
    @update:visible="emits('update:visible', $event)"
    header="Retrouver votre accès"
    modal
    :closable="false"
    :style="{ width: '30rem', maxWidth: 'calc(100vw - 2rem)' }"
  >
    <ol class="reset-steps" aria-label="Étapes de réinitialisation">
      <li
        v-for="(label, index) in ['E-mail', 'Vérification', 'Mot de passe']"
        :key="label"
        :class="{ current: step === index + 1, completed: step > index + 1 }"
        :aria-current="step === index + 1 ? 'step' : undefined"
      >
        <span>{{ index + 1 }}</span
        >{{ label }}
      </li>
    </ol>
    <form
      v-if="step === 1"
      class="reset-form"
      @submit.prevent="sendCode"
      novalidate
    >
      <p class="description">
        Indiquez l’adresse e-mail de votre compte. Nous vous enverrons un code
        de vérification.
      </p>
      <NsFormField id="reset-email" label="Adresse e-mail" required>
        <NsInput
          id="reset-email"
          v-model="email"
          type="email"
          autocomplete="email"
          placeholder="vous@exemple.fr"
          :invalid="invalidFields.email"
          fluid
        />
      </NsFormField>
      <div class="dialog-actions">
        <NsButton
          label="Annuler"
          type="button"
          severity="secondary"
          text
          @click="cancel"
        /><NsButton
          label="Envoyer le code"
          icon="pi pi-arrow-right"
          iconPos="right"
          type="submit"
          :loading="loading"
        />
      </div>
    </form>
    <form
      v-else-if="step === 2"
      class="reset-form"
      @submit.prevent="verifyCode"
      novalidate
    >
      <p class="description">
        Saisissez le code à six chiffres envoyé à <strong>{{ email }}</strong
        >.
      </p>
      <div class="otp-field">
        <span id="reset-code-label" class="field-label"
          >Code de vérification</span
        >
        <NsInputOtp
          v-model="code"
          role="group"
          aria-labelledby="reset-code-label"
          :pt="{
            pcInputText: {
              root: {
                'aria-label': 'Chiffre du code de vérification',
                autocomplete: 'one-time-code',
              },
            },
          }"
          integerOnly
          :length="6"
          :invalid="invalidFields.code"
        />
      </div>
      <div class="dialog-actions">
        <NsButton
          label="Retour"
          type="button"
          severity="secondary"
          text
          @click="() => (step = 1)"
        /><NsButton label="Valider le code" type="submit" :loading="loading" />
      </div>
    </form>
    <form
      v-else-if="step === 3"
      class="reset-form"
      @submit.prevent="updatePassword"
      novalidate
    >
      <p class="description">
        Choisissez votre nouveau mot de passe pour vous reconnecter.
      </p>
      <NsFormField
        id="reset-new-password"
        label="Nouveau mot de passe"
        required
      >
        <NsPasswordInput
          inputId="reset-new-password"
          v-model="newPassword"
          :inputProps="{ autocomplete: 'new-password' }"
          toggleMask
          :feedback="false"
          :invalid="invalidFields.newPassword"
          fluid
        />
      </NsFormField>
      <NsFormField
        id="reset-confirm-password"
        label="Confirmer le mot de passe"
        required
      >
        <NsPasswordInput
          inputId="reset-confirm-password"
          v-model="confirmPassword"
          :inputProps="{ autocomplete: 'new-password' }"
          toggleMask
          :feedback="false"
          :invalid="invalidFields.confirmPassword"
          fluid
        />
      </NsFormField>
      <div class="dialog-actions">
        <NsButton
          label="Annuler"
          type="button"
          severity="secondary"
          text
          @click="cancel"
        /><NsButton
          label="Mettre à jour"
          icon="pi pi-check"
          type="submit"
          :loading="loading"
        />
      </div>
    </form>
  </NsDialog>
</template>

<style scoped>
.reset-steps {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  list-style: none;
  padding: 0 0 1.3rem;
  margin: 0.3rem 0 1.3rem;
  border-bottom: 1px solid #e7ebe5;
}
.reset-steps li {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  color: #69766f;
  font-size: 0.68rem;
  text-align: center;
}
.reset-steps li > span {
  width: 27px;
  height: 27px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #f0f2ed;
  font-size: 0.73rem;
  font-weight: 600;
}
.reset-steps li.current {
  color: #1d4d40;
  font-weight: 650;
}
.reset-steps li.current > span {
  background: #1d4d40;
  color: white;
}
.reset-steps li.completed > span {
  color: #1d4d40;
  background: #e7eee7;
}
.reset-form {
  display: grid;
  gap: 1.3rem;
}
.description {
  margin: 0;
  color: #69766f;
  font-size: 0.86rem;
  line-height: 1.7;
  overflow-wrap: anywhere;
}
.description strong {
  color: #202b26;
  font-weight: 600;
}
.otp-field {
  display: grid;
  gap: 0.8rem;
}
.field-label {
  font-size: 0.82rem;
  font-weight: 600;
}
.otp-field :deep(.p-inputotp) {
  display: flex;
  gap: clamp(0.3rem, 1.5vw, 0.65rem);
}
.otp-field :deep(.p-inputotp-input) {
  width: clamp(2rem, 8.5vw, 2.9rem);
  height: 3rem;
  min-width: 0;
  font-size: 1.15rem;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  padding-top: 1.1rem;
  border-top: 1px solid #e7ebe5;
}
@media (max-width: 400px) {
  .dialog-actions {
    flex-direction: column-reverse;
  }
}
</style>
