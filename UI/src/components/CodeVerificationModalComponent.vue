<script setup lang="ts">
import { ref } from "vue"
import NsDialog from "@/components/ui/NsDialog.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsInputOtp from "@/components/ui/NsInputOtp.vue"

const props = defineProps({
  visible: Boolean,
})
const emits = defineEmits([
  "update:visible",
  "validated",
  "cancelled",
  "sendBack",
])

const code = ref("")
const error = ref("")

const submit = () => {
  // Ensure a code was entered before validating.
  if (code.value.trim() === "") {
    error.value = "Le code est requis"
    return
  }
  emits("validated", code.value)
}

const cancel = () => {
  // Cancel code verification.
  emits("cancelled")
  emits("update:visible", false)
}

const sendAgainCode = () => {
  emits("sendBack")
}
</script>

<template>
  <NsDialog
    :visible="props.visible"
    @update:visible="emits('update:visible', $event)"
    header="Vérifiez votre adresse e-mail"
    modal
    :closable="false"
    :style="{ width: '29rem', maxWidth: 'calc(100vw - 2rem)' }"
  >
    <form class="verification-form" @submit.prevent="submit" novalidate>
      <span class="verification-icon pi pi-envelope" aria-hidden="true"></span>
      <p class="description">
        Un code vous a été envoyé par e-mail. Saisissez ses six chiffres pour
        finaliser votre inscription.
      </p>
      <div class="otp-field">
        <span id="registration-code-label" class="field-label"
          >Code de vérification</span
        >
        <NsInputOtp
          v-model="code"
          role="group"
          aria-labelledby="registration-code-label"
          :aria-describedby="error ? 'registration-code-error' : undefined"
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
          :invalid="!!error"
        />
        <small
          v-if="error"
          id="registration-code-error"
          class="field-error"
          role="alert"
          >{{ error }}</small
        >
      </div>
      <div class="resend-note">
        <span>Vous n’avez rien reçu ?</span
        ><NsButton
          label="Renvoyer le code"
          type="button"
          text
          size="small"
          @click="sendAgainCode"
        />
      </div>
      <div class="dialog-actions">
        <NsButton
          label="Annuler"
          type="button"
          severity="secondary"
          text
          @click="cancel"
        /><NsButton
          label="Vérifier mon adresse"
          icon="pi pi-check"
          type="submit"
        />
      </div>
    </form>
  </NsDialog>
</template>

<style scoped>
.verification-form {
  display: grid;
  gap: 1.4rem;
  padding-top: 0.3rem;
}
.verification-icon {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 13px;
  color: #1d4d40;
  background: #e7eee7;
  font-size: 1.15rem;
}
.description {
  color: #69766f;
  font-size: 0.87rem;
  line-height: 1.7;
  margin: -0.3rem 0 0;
}
.otp-field {
  display: grid;
  gap: 0.8rem;
}
.field-label {
  color: #202b26;
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
.field-error {
  color: #a54435;
  font-size: 0.78rem;
}
.resend-note {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.2rem;
  color: #69766f;
  font-size: 0.78rem;
}
.resend-note :deep(.p-button) {
  padding: 0.4rem;
  font-size: 0.78rem;
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
