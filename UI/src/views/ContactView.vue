<script setup lang="ts">
import { isCancel } from "axios"
import { ref } from "vue"
import { useToast } from "primevue/usetoast"
import NsInput from "@/components/ui/NsInput.vue"
import NsTextarea from "@/components/ui/NsTextarea.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsCard from "@/components/ui/NsCard.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import { sendMail } from "@/services/apiService"
import {
  resolveApiErrorMessage,
  resolveApiMessage,
  showToast,
} from "@/assets/js/utils"

const name = ref("")
const email = ref("")
const message = ref("")

const toast = useToast()

const sendMessage = async () => {
  if (!name.value || !email.value || !message.value) {
    showToast(
      toast,
      "error",
      "Champs requis",
      "Veuillez remplir tous les champs."
    )
    return
  }
  try {
    const response = await sendMail({
      name: name.value,
      email: email.value,
      message: message.value,
    })
    showToast(
      toast,
      "success",
      "Message envoyé",
      resolveApiMessage(response, "Nous vous répondrons bientôt !")
    )
    name.value = ""
    email.value = ""
    message.value = ""
  } catch (error: any) {
    if (isCancel(error)) return
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(error, "Échec de l'envoi de votre message.")
    )
  }
}
</script>

<template>
  <section class="contact-page">
    <div class="contact-intro">
      <span class="eyebrow">ON VOUS ÉCOUTE</span>
      <h1>Parlons de votre expérience.</h1>
      <p>
        Une question, une idée ou un problème rencontré sur NextShape ?
        Laissez-nous un message.
      </p>
      <div class="contact-note">
        <span class="pi pi-envelope" aria-hidden="true"></span>
        <p>
          Votre retour nous aide à améliorer votre quotidien sur l'application.
        </p>
      </div>
    </div>
    <NsCard class="contact-card">
      <h2>Envoyer un message</h2>
      <p class="card-description">
        Tous les champs sont nécessaires pour vous répondre.
      </p>
      <form class="contact-form" @submit.prevent="sendMessage" novalidate>
        <NsFormField id="contact-name" label="Votre nom" required>
          <NsInput
            id="contact-name"
            v-model="name"
            autocomplete="name"
            placeholder="Prénom et nom"
            fluid
          />
        </NsFormField>
        <NsFormField id="contact-email" label="Adresse e-mail" required>
          <NsInput
            id="contact-email"
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="vous@exemple.fr"
            fluid
          />
        </NsFormField>
        <NsFormField id="contact-message" label="Votre message" required>
          <NsTextarea
            id="contact-message"
            v-model="message"
            rows="6"
            autoResize
            maxlength="1000"
            placeholder="Dites-nous comment nous pouvons vous aider…"
            aria-describedby="contact-character-count"
            fluid
          />
          <span
            id="contact-character-count"
            class="character-count"
            :class="{ 'at-limit': message.length >= 1000 }"
            >{{ message.length }} / 1 000 caractères</span
          >
        </NsFormField>
        <div class="form-actions">
          <NsButton
            label="Envoyer le message"
            icon="pi pi-arrow-up-right"
            iconPos="right"
            type="submit"
          />
        </div>
      </form>
    </NsCard>
  </section>
</template>

<style scoped>
.contact-page {
  display: grid;
  grid-template-columns: 0.85fr 1.15fr;
  gap: clamp(2rem, 6vw, 6rem);
  max-width: 1040px;
  margin: 0 auto;
  padding: clamp(1rem, 4vw, 3rem) 0;
  align-items: start;
}
.contact-intro {
  padding-top: 1.8rem;
}
.eyebrow {
  color: #1d4d40;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
}
h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  letter-spacing: -0.05em;
  line-height: 1.12;
  margin: 1rem 0 1.3rem;
}
.contact-intro > p {
  color: #69766f;
  line-height: 1.8;
  font-size: 0.95rem;
}
.contact-note {
  margin-top: 2.5rem;
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  border-top: 1px solid #dee4dd;
  padding-top: 1.5rem;
}
.contact-note > span {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  background: #e7eee7;
  color: #1d4d40;
  border-radius: 10px;
}
.contact-note p {
  margin: 0.1rem 0;
  color: #69766f;
  font-size: 0.82rem;
  line-height: 1.65;
}
.contact-card {
  padding: clamp(1.3rem, 4vw, 2.2rem);
}
h2 {
  margin: 0;
  font-size: 1.3rem;
  letter-spacing: -0.03em;
}
.card-description {
  color: #69766f;
  font-size: 0.83rem;
  line-height: 1.6;
  margin: 0.6rem 0 1.7rem;
}
.contact-form {
  display: grid;
  gap: 1.3rem;
}
.character-count {
  display: block;
  text-align: right;
  font-size: 0.7rem;
  font-variant-numeric: tabular-nums;
  color: #69766f;
  margin-top: 0.45rem;
}
.at-limit {
  color: #a54435;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.3rem;
}
@media (max-width: 760px) {
  .contact-page {
    grid-template-columns: minmax(0, 1fr);
    gap: 1.6rem;
    max-width: 540px;
  }
  .contact-intro {
    padding-top: 0;
  }
  .contact-note {
    display: none;
  }
}
@media (max-width: 480px) {
  .form-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
