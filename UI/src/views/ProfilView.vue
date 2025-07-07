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
import DatePicker from "primevue/datepicker"
import InputMask from "primevue/inputmask"
import ConfirmPopup from "primevue/confirmpopup"
import { useConfirm } from "primevue/useconfirm"
import { showToast } from "@/assets/js/utils"
import SelectButton from "primevue/selectbutton"
import { GENDER } from "@/assets/js/constants"

const toast = useToast()
const confirm = useConfirm()
const today = new Date()

const authStore = useAuthStore()
const userData = computed(() => authStore.user)

// Gestion des modifications
const editDialogVisible = ref(false)
const fieldToEdit = ref("")
const fieldValue = ref("")

const editableFields = [
  { key: "last_name", label: "Nom" },
  { key: "first_name", label: "Prénom" },
  { key: "gender", label: "Genre" },
  { key: "birth_date", label: "Date de naissance" },
  { key: "email", label: "Adresse Email" },
  { key: "phone_number", label: "Téléphone" },
]

const formattedBirthDate = computed(() => {
  const rawDate = userData.value?.birth_date
  if (!rawDate) return "N/A"
  return new Date(rawDate).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
})

const formattedGender = computed(() => {
  const rawDate = userData.value?.gender
  if (!rawDate) return "N/A"
  return rawDate == GENDER[0].value ? GENDER[0].label : GENDER[1].label
})

const getDialogHeader = (field: string): string => {
  const label = editableFields.find((f) => f.key === field)?.label
  return label
    ? `Modifier votre ${label.toLowerCase()}`
    : field === "password"
    ? "Saisissez votre nouveau mot de passe"
    : ""
}

const openEditDialog = (field: string) => {
  fieldToEdit.value = field
  fieldValue.value =
    userData.value?.[field as keyof typeof userData.value] ?? ""
  editDialogVisible.value = true
}

const cancelEdit = () => {
  editDialogVisible.value = false
  fieldToEdit.value = ""
  fieldValue.value = ""
}

const saveEdit = async () => {
  try {
    await authStore.updateProfileField(fieldToEdit.value, fieldValue.value)
    showToast(toast, "success", "Succès", "Modification enregistrée.")
    cancelEdit()
  } catch (error) {
    showToast(
      toast,
      "error",
      "Erreur",
      "Erreur lors de la mise à jour du profil."
    )
  }
}

const confirmDeleteAccount = (event: Event) => {
  confirm.require({
    target: event.currentTarget as HTMLElement | undefined,
    message:
      "Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.",
    icon: "pi pi-exclamation-triangle",
    rejectProps: {
      label: "Annuler",
      severity: "secondary",
      outlined: true,
    },
    acceptProps: {
      label: "Supprimer définitivement",
      severity: "danger",
    },
    accept: async () => {
      try {
        await authStore.deleteAccount()
        showToast(toast, "success", "Succès", "Votre compte a été supprimé.")
      } catch (error) {
        showToast(
          toast,
          "error",
          "Erreur",
          "Échec de la suppression du compte."
        )
      }
    },
    reject: () => {},
  })
}
</script>

<template>
  <Card class="w-6 mx-auto">
    <template #title>
      <span class="text-3xl font-bold">
        Profil de {{ userData?.first_name || "N/A" }}
        {{ userData?.last_name || "N/A" }}
      </span>
    </template>

    <template #content>
      <div class="flex flex-column gap-2 mt-3">
        <div
          v-for="field in editableFields"
          :key="field.key"
          class="flex align-items-center justify-content-between"
        >
          <div>
            <strong>{{ field.label }} : </strong>
            <span v-if="field.key === 'birth_date'">{{
              formattedBirthDate
            }}</span>
            <span v-else-if="field.key === 'gender'">{{
              formattedGender
            }}</span>
            <span v-else>{{ userData?.[field.key] || "N/A" }}</span>
          </div>
          <Button
            label="Modifier"
            icon="pi pi-pencil"
            rounded
            text
            @click="openEditDialog(field.key)"
          />
        </div>
        <hr class="w-full" />
        <div class="flex align-items-center justify-content-end mt-3 gap-2">
          <Button
            label="Changer le mot de passe"
            size="small"
            icon="pi pi-lock"
            severity="secondary"
            @click="openEditDialog('password')"
          />
          <ConfirmPopup />
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
    :header="getDialogHeader(fieldToEdit)"
    modal
    :closable="false"
  >
    <div class="field">
      <label class="block mb-2">{{ getDialogHeader(fieldToEdit) }}</label>

      <SelectButton
        v-if="fieldToEdit === 'gender'"
        class="w-full"
        v-model="fieldValue"
        :options="GENDER"
        optionLabel="label"
        optionValue="value"
        :defaultValue="userData?.gender"
      />
      <Password
        v-else-if="fieldToEdit === 'password'"
        v-model="fieldValue"
        toggleMask
        class="w-full"
      />
      <DatePicker
        v-else-if="fieldToEdit === 'birth_date'"
        v-model="fieldValue as unknown as Date"
        class="w-full"
        showIcon
        dateFormat="dd/mm/yy"
        :maxDate="today"
      />
      <InputMask
        v-else-if="fieldToEdit === 'phone_number'"
        id="phone_number"
        v-model="fieldValue"
        mask="(+33) 9-99-99-99-99"
        placeholder="(+33) 0-00-00-00-00"
        class="w-full"
      />
      <InputText v-else v-model="fieldValue" class="w-full" />
    </div>

    <template #footer>
      <Button label="Annuler" icon="pi pi-times" text @click="cancelEdit" />
      <Button label="Sauvegarder" icon="pi pi-check" text @click="saveEdit" />
    </template>
  </Dialog>

  <Toast />
</template>
