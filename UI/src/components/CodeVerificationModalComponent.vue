<script setup>
import { ref } from "vue"
import Dialog from "primevue/dialog"
import Button from "primevue/button"
import InputOtp from "primevue/inputotp"

const props = defineProps({
  visible: Boolean,
})
const emits = defineEmits(["update:visible", "validated", "cancelled"])

const code = ref("")
const error = ref("")

const submit = () => {
  // Vérifie si le code est mentionné et s'il est validé.
  if (code.value.trim() === "") {
    error.value = "Le code est requis"
    return
  }
  emits("validated", code.value)
}

const cancel = () => {
  // Annule la vérification par code.
  emits("cancelled")
  emits("update:visible", false)
}

const sendAgainCode = () => {
  emits("sendBack")
}
</script>

<template>
  <Dialog
    v-model:visible="props.visible"
    header="Validez votre adresse e-mail"
    :modal="true"
    :closable="false"
  >
    <div class="formgrid">
      <div class="field">
        <label for="code">Entrez le code reçu par email :</label>
        <br />
        <a @click="sendAgainCode" class="text-sm text-primary cursor-pointer"
          >Renvoyer le code par mail</a
        >
        <InputOtp
          id="code"
          v-model="code"
          integerOnly
          size="small"
          :length="6"
        />
      </div>
    </div>
    <div class="flex justify-content-end mt-3 gap-2">
      <Button label="Annuler" severity="secondary" @click="cancel" />
      <Button label="Valider" @click="submit" />
    </div>

    <small v-if="error" class="text-red-500">{{ error }}</small>
  </Dialog>
</template>
