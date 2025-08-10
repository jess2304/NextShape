<script setup lang="ts">
import { ref } from "vue"
import { useToast } from "primevue/usetoast"
import InputText from "primevue/inputtext"
import Textarea from "primevue/textarea"
import Button from "primevue/button"
import Card from "primevue/card"
import { sendMail } from "@/services/apiService"
import { showToast } from "@/assets/js/utils"

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
    await sendMail({
      name: name.value,
      email: email.value,
      message: message.value,
    })
    showToast(
      toast,
      "success",
      "Message envoyé",
      "Nous vous répondrons bientôt !"
    )
    name.value = ""
    email.value = ""
    message.value = ""
  } catch (error: any) {
    showToast(
      toast,
      "error",
      "Erreur",
      error?.response?.data?.errors?.non_field_errors?.[0] ||
        error?.response?.data?.message ||
        "Échec de l'envoi de votre message." + error
    )
  }
}
</script>

<template>
  <Card class="w-full max-w-lg shadow-lg">
    <template #title>
      <h2 class="text-2xl font-semibold text-center text-gray-800">
        Contactez-nous
      </h2>
    </template>

    <template #content>
      <form class="formgrid grid gap-2" @submit.prevent="sendMessage">
        <div class="field col-8 md:col-4">
          <label for="name">Nom</label>
          <InputText id="name" v-model="name" class="w-full" />
        </div>
        <div class="field col-8 md:col-4">
          <label for="email">Email</label>
          <InputText id="email" v-model="email" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="message">Message</label>
          <Textarea
            id="message"
            v-model="message"
            rows="5"
            class="w-full"
            autoResize
            maxlength="1000"
          />
          <span
            class="text-sm text-gray-500"
            :class="{
              'text-gray-500': message.length < 1000,
              'text-red-500': message.length >= 1000,
            }"
          >
            {{ message.length }}/1000
          </span>
        </div>
        <div class="field col-4 md:col-1">
          <Button
            label="Envoyer"
            icon="pi pi-send"
            class="w-full"
            type="submit"
          />
        </div>
      </form>
    </template>
  </Card>
</template>

<style scoped></style>
