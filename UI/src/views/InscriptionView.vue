<script setup lang="ts">
import { isCancel } from "axios"
import { ref } from "vue"
import NsInput from "@/components/ui/NsInput.vue"
import NsInputMask from "@/components/ui/NsInputMask.vue"
import NsPasswordInput from "@/components/ui/NsPasswordInput.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsCard from "@/components/ui/NsCard.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import NsDatePicker from "@/components/ui/NsDatePicker.vue"
import NsSelectButton from "@/components/ui/NsSelectButton.vue"
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
  code: null,
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

const handleCodeValidation = async (code: string) => {
  loading.value = true

  try {
    formData.value.code = code
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
    code: null,
  }
  showModal.value = false
}
</script>

<template>
  <section class="signup-page">
    <div class="signup-intro">
      <span class="eyebrow">UN PREMIER PAS POUR VOUS</span>
      <h1>Votre parcours commence ici.</h1>
      <p>
        Créez votre espace pour retrouver vos calculs et suivre votre évolution.
      </p>
    </div>
    <NsCard class="signup-card">
      <form @submit.prevent="validateAndProceed" novalidate>
        <div class="form-title">
          <h2>Créer un compte</h2>
          <span>* Champs obligatoires</span>
        </div>
        <fieldset class="form-section">
          <legend>
            <span class="section-number">01</span> À propos de vous
          </legend>
          <div class="form-grid">
            <NsFormField id="signup-first-name" label="Prénom" required>
              <NsInput
                id="signup-first-name"
                v-model="formData.first_name"
                autocomplete="given-name"
                placeholder="Votre prénom"
                :invalid="invalidFields.first_name"
                fluid
              />
            </NsFormField>
            <NsFormField id="signup-last-name" label="Nom" required>
              <NsInput
                id="signup-last-name"
                v-model="formData.last_name"
                autocomplete="family-name"
                placeholder="Votre nom"
                :invalid="invalidFields.last_name"
                fluid
              />
            </NsFormField>
            <div class="gender-field">
              <span id="signup-gender-label" class="field-label"
                >Genre <span aria-hidden="true">*</span></span
              >
              <NsSelectButton
                v-model="formData.gender"
                aria-labelledby="signup-gender-label"
                :invalid="invalidFields.gender"
                :options="GENDER"
                optionLabel="label"
                optionValue="value"
                defaultValue="H"
              />
            </div>
            <NsFormField
              id="signup-birth-date"
              label="Date de naissance"
              required
            >
              <NsDatePicker
                inputId="signup-birth-date"
                v-model="formData.birth_date"
                showIcon
                dateFormat="dd/mm/yy"
                placeholder="JJ/MM/AAAA"
                :invalid="invalidFields.birth_date"
                :maxDate="today"
                fluid
              />
            </NsFormField>
          </div>
        </fieldset>
        <fieldset class="form-section">
          <legend>
            <span class="section-number">02</span> Vos coordonnées
          </legend>
          <div class="form-grid">
            <NsFormField id="signup-email" label="Adresse e-mail" required>
              <NsInput
                id="signup-email"
                type="email"
                autocomplete="email"
                v-model="formData.email"
                placeholder="vous@exemple.fr"
                :invalid="invalidFields.email"
                fluid
              />
            </NsFormField>
            <NsFormField
              id="signup-confirm-email"
              label="Confirmer l'adresse e-mail"
              required
            >
              <NsInput
                id="signup-confirm-email"
                type="email"
                autocomplete="email"
                v-model="formData.confirmEmail"
                placeholder="La même adresse e-mail"
                :invalid="invalidFields.confirmEmail"
                fluid
              />
            </NsFormField>
            <NsFormField id="signup-phone" label="Téléphone" hint="Facultatif">
              <NsInputMask
                id="signup-phone"
                v-model="formData.phone_number"
                autocomplete="tel"
                aria-describedby="signup-phone-hint"
                mask="(+33) 9-99-99-99-99"
                placeholder="(+33) 0-00-00-00-00"
                fluid
              />
            </NsFormField>
          </div>
        </fieldset>
        <fieldset class="form-section">
          <legend>
            <span class="section-number">03</span> Votre mot de passe
          </legend>
          <div class="form-grid">
            <NsFormField id="signup-password" label="Mot de passe" required>
              <NsPasswordInput
                inputId="signup-password"
                v-model="formData.password"
                :inputProps="{ autocomplete: 'new-password' }"
                toggleMask
                :invalid="invalidFields.password"
                fluid
              />
            </NsFormField>
            <NsFormField
              id="signup-confirm-password"
              label="Confirmer le mot de passe"
              required
            >
              <NsPasswordInput
                inputId="signup-confirm-password"
                v-model="formData.confirmPassword"
                :inputProps="{ autocomplete: 'new-password' }"
                toggleMask
                :invalid="invalidFields.confirmPassword"
                :feedback="false"
                fluid
              />
            </NsFormField>
          </div>
        </fieldset>
        <div class="signup-actions">
          <p>Nous vous enverrons un code pour vérifier votre adresse e-mail.</p>
          <NsButton
            label="Créer mon compte"
            icon="pi pi-arrow-right"
            iconPos="right"
            type="submit"
            :loading="loading"
          />
        </div>
      </form>
    </NsCard>
    <p class="auth-switch">
      Déjà un compte ? <RouterLink to="/connexion">Me connecter</RouterLink>
    </p>
    <CodeVerificationModalComponent
      :visible="showModal"
      @update:visible="showModal = $event"
      @validated="handleCodeValidation"
      @sendBack="sendCode"
    />
  </section>
</template>

<style scoped>
.signup-page {
  width: min(100%, 760px);
  margin: 0 auto;
  padding: 1.5rem 0 2rem;
}
.signup-intro {
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
  font-size: clamp(1.8rem, 4vw, 2.4rem);
  line-height: 1.2;
  letter-spacing: -0.045em;
}
.signup-intro p {
  color: #69766f;
  font-size: 0.95rem;
  line-height: 1.6;
}
.signup-card {
  padding: clamp(1.3rem, 4vw, 2.5rem);
}
.form-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}
h2 {
  margin: 0;
  font-size: 1.3rem;
  letter-spacing: -0.025em;
}
.form-title > span {
  font-size: 0.73rem;
  color: #69766f;
}
.form-section {
  min-width: 0;
  margin: 0;
  padding: 0 0 1.8rem;
  border: 0;
}
.form-section + .form-section {
  padding-top: 1.3rem;
  border-top: 1px solid #e7ebe5;
}
legend {
  float: left;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 1.3rem;
  font-size: 0.9rem;
  font-weight: 650;
}
.section-number {
  font-size: 0.7rem;
  color: #52735f;
  background: #eef3ed;
  border-radius: 7px;
  padding: 0.35rem 0.45rem;
  font-variant-numeric: tabular-nums;
}
.form-grid {
  clear: both;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1.2rem 1.4rem;
}
.gender-field {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.field-label {
  font-size: 0.84rem;
  font-weight: 600;
}
.field-label > span {
  color: #69766f;
}
.signup-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding-top: 1.2rem;
  border-top: 1px solid #e7ebe5;
}
.signup-actions p {
  max-width: 280px;
  margin: 0;
  color: #69766f;
  font-size: 0.78rem;
  line-height: 1.6;
}
.signup-actions :deep(.p-button) {
  flex-shrink: 0;
}
.auth-switch {
  text-align: center;
  color: #69766f;
  font-size: 0.86rem;
  margin-top: 1.5rem;
}
.auth-switch a {
  color: #1d4d40;
  font-weight: 600;
  text-underline-offset: 3px;
}
@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .form-title {
    align-items: start;
    flex-direction: column;
    gap: 0.4rem;
  }
  .signup-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .signup-actions p {
    max-width: none;
  }
}
</style>
