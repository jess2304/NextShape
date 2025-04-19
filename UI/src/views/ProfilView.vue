<script setup lang="ts">
import { computed, ref } from "vue"
import { useAuthStore } from "@/stores/authStore"
import Toast from "primevue/toast"
import { useToast } from "primevue/usetoast"
import Card from "primevue/card"
import Button from "primevue/button"
import Dialog from "primevue/dialog"
import InputText from "primevue/inputtext"
import Password from "primevue/password"
import Calendar from "primevue/calendar"
import InputMask from "primevue/inputmask"
import ConfirmPopup from "primevue/confirmpopup"
import { useConfirm } from "primevue/useconfirm"

const toast = useToast()
const today = new Date()
const confirm = useConfirm()

// Appel du profil
const authStore = useAuthStore()
const userData = computed(() => authStore.user)

const formattedBirthDate = computed(() => {
  // Donne la date bien formatée
  const rawDate = authStore.user?.birth_date
  if (rawDate) {
    const date = new Date(rawDate)
    return date.toLocaleDateString("fr-FR", {
      day: "numeric",
      month: "long",
      year: "numeric",
    })
  }
  return "N/A"
})

// Variables pour la modale d'édition
const editDialogVisible = ref(false)
const fieldToEdit = ref("")
const fieldValue = ref("")

// Titre du dialog en fonction du champ à éditer
const dialogHeader = computed(() => {
  switch (fieldToEdit.value) {
    case "name":
      return "Modifier Nom & Prénom"
    case "birth_date":
      return "Modifier la date de naissance"
    case "email":
      return "Modifier l'Email"
    case "phone_number":
      return "Modifier le Numéro de téléphone"
    case "password":
      return "Saisissez votre nouveau mot de passe"
    default:
      return ""
  }
})

// Ouvre le dialog en fonction du champ à modifier
const openEditDialog = (field: string) => {
  fieldToEdit.value = field
  // Initialiser la valeur à éditer depuis userData
  if (field === "last_name") {
    fieldValue.value = userData.value.last_name
  } else if (field === "first_name") {
    fieldValue.value = userData.value.first_name
  } else if (field === "birth_date") {
    fieldValue.value = userData.value.birth_date || ""
  } else if (field === "email") {
    fieldValue.value = userData.value.email || ""
  } else if (field === "phone_number") {
    fieldValue.value = userData.value.phone_number || ""
  } else if (field === "password") {
    fieldValue.value = ""
  }
  editDialogVisible.value = true
}

// Annuler la modification
const cancelEdit = () => {
  editDialogVisible.value = false
}

// Sauvegarder les modifications
const saveEdit = async () => {
  try {
    await authStore.updateProfileField(fieldToEdit.value, fieldValue.value)
    // Fermer dialog
    editDialogVisible.value = false
    toast.add({
      severity: "success",
      summary: "Modification réalisée avec succès",
      life: 5000,
    })
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Erreur Lors de la modification de votre profil",
      life: 5000,
    })
  }
}

const confirmDeleteAccount = (event) => {
  confirm.require({
    target: event.currentTarget,
    message:
      "Êtes vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.",
    icon: "pi pi-exclamation-triangle",
    rejectProps: {
      label: "Annuler",
      severity: "secondary",
      outlined: true,
    },
    acceptProps: {
      label: "Supprimer définitivement",
    },
    accept: async () => {
      try {
        await authStore.deleteAccount()
        toast.add({
          severity: "success",
          summary: "Vous avez supprimé définitivement votre compte. Au revoir.",
          life: 5000,
        })
      } catch (error) {
        toast.add({
          severity: "error",
          summary: "Erreur Lors de la suppression du compte.",
          life: 5000,
        })
      }
    },
    reject: () => {},
  })
}
</script>

<template>
  <Card class="w-6 mx-auto">
    <template #title>
      <span class="text-3xl font-bold"
        ><strong
          >Profil de {{ userData?.first_name || "N/A" }}
          {{ userData?.last_name || "N/A" }}</strong
        ></span
      >
    </template>
    <template #content>
      <div class="flex flex-column gap-2 mt-3">
        <div class="flex align-items-center justify-content-between">
          <!-- Nom -->
          <div><strong>Nom :</strong> {{ userData?.last_name || "N/A" }}</div>
          <Button
            label="Modifier"
            icon="pi pi-pencil"
            rounded
            text
            @click="openEditDialog('last_name')"
          />
        </div>
        <hr />
        <!-- Prénom -->
        <div class="flex align-items-center justify-content-between">
          <div>
            <strong>Prénom :</strong> {{ userData?.first_name || "N/A" }}
          </div>
          <Button
            label="Modifier"
            icon="pi pi-pencil"
            rounded
            text
            @click="openEditDialog('first_name')"
          />
        </div>
        <hr />
        <!-- Date de naissance -->
        <div class="flex align-items-center justify-content-between">
          <div>
            <strong>Date de naissance :</strong>
            {{ formattedBirthDate }}
          </div>
          <Button
            label="Modifier"
            icon="pi pi-pencil"
            rounded
            text
            @click="openEditDialog('birth_date')"
          />
        </div>
        <hr />
        <!-- Email -->
        <div class="flex align-items-center justify-content-between">
          <div>
            <strong>Email :</strong>
            {{ userData?.email || "N/A" }}
          </div>
          <Button
            label="Modifier"
            icon="pi pi-pencil"
            rounded
            text
            @click="openEditDialog('email')"
          />
        </div>
        <hr />
        <!-- Téléphone -->
        <div class="flex align-items-center justify-content-between">
          <div>
            <strong>Téléphone :</strong>
            {{ userData?.phone_number || "N/A" }}
          </div>
          <Button
            label="Modifier"
            icon="pi pi-pencil"
            rounded
            text
            @click="openEditDialog('phone_number')"
          />
        </div>
        <hr />
        <!-- Bouton Changer de mot de passe -->
        <div class="flex align-items-center justify-content-end mt-3 gap-2">
          <Button
            label="Changer le mot de passe"
            size="small"
            icon="pi pi-lock"
            severity="secondary"
            @click="openEditDialog('password')"
          />
          <ConfirmPopup></ConfirmPopup>
          <Button
            label="Supprimer mon compte"
            size="small"
            icon="pi pi-trash"
            severity="danger"
            @click="confirmDeleteAccount($event)"
          />
        </div>
      </div>
    </template>
  </Card>
  <!-- Dialog de modification -->
  <Dialog
    v-model:visible="editDialogVisible"
    :header="dialogHeader"
    modal
    :closable="false"
  >
    <div v-if="fieldToEdit === 'password'">
      <label class="block mb-2">{{ dialogHeader }}</label>
      <Password v-model="fieldValue" toggleMask class="w-full" />
    </div>
    <div v-else-if="fieldToEdit === 'birth_date'">
      <label class="block mb-2">{{ dialogHeader }}</label>
      <Calendar
        class="w-full"
        v-model="fieldValue"
        showIcon
        dateFormat="dd/mm/yy"
        :maxDate="today"
      />
    </div>
    <div v-else-if="fieldToEdit === 'phone_number'">
      <label class="block mb-2">{{ dialogHeader }}</label>
      <InputMask
        id="phone_number"
        v-model="fieldValue"
        mask="(+33) 9-99-99-99-99"
        placeholder="(+33) 0-00-00-00-00"
        fluid
      />
    </div>
    <div v-else>
      <label class="block mb-2">{{ dialogHeader }}</label>
      <InputText v-model="fieldValue" class="w-full" />
    </div>
    <template #footer>
      <Button
        label="Annuler"
        icon="pi pi-times"
        class="p-button-text"
        @click="cancelEdit"
      />
      <Button
        label="Sauvegarder"
        icon="pi pi-check"
        class="p-button-text"
        @click="saveEdit"
      />
    </template>
  </Dialog>
  <Toast />
</template>
