<script setup lang="ts">
import { isCancel } from "axios"
import { computed, ref } from "vue"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import NsCard from "@/components/ui/NsCard.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsDialog from "@/components/ui/NsDialog.vue"
import NsInput from "@/components/ui/NsInput.vue"
import NsPasswordInput from "@/components/ui/NsPasswordInput.vue"
import NsDatePicker from "@/components/ui/NsDatePicker.vue"
import NsInputMask from "@/components/ui/NsInputMask.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import PageHeader from "@/components/layout/PageHeader.vue"
import ConfirmPopup from "primevue/confirmpopup"
import { useConfirm } from "primevue/useconfirm"
import {
  resolveApiErrorMessage,
  resolveApiMessage,
  showToast,
} from "@/assets/js/utils"
import NsSelectButton from "@/components/ui/NsSelectButton.vue"
import { GENDER } from "@/assets/js/constants"

const toast = useToast()
const confirm = useConfirm()
const today = new Date()

const authStore = useAuthStore()
const userData = computed(() => authStore.user)

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
    const response = await authStore.updateProfileField(
      fieldToEdit.value,
      fieldValue.value
    )
    showToast(toast, "success", "Succès", resolveApiMessage(response))
    cancelEdit()
  } catch (error: any) {
    if (isCancel(error)) return
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(error, String(error || "Erreur de mise à jour."))
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
        const response = await authStore.deleteAccount()
        showToast(toast, "success", "Succès", resolveApiMessage(response))
      } catch (error: any) {
        if (isCancel(error)) return
        showToast(
          toast,
          "error",
          "Erreur",
          resolveApiErrorMessage(
            error,
            String(error || "Échec de la suppression du compte.")
          )
        )
      }
    },
    reject: () => {},
  })
}
</script>

<template>
  <section class="profile-page">
    <PageHeader
      eyebrow="MON COMPTE"
      title="Votre profil"
      description="Vos informations personnelles, réunies au même endroit."
    />
    <NsCard class="profile-card">
      <div class="profile-summary">
        <span class="profile-avatar" aria-hidden="true"
          >{{ userData?.first_name?.charAt(0)
          }}{{ userData?.last_name?.charAt(0) }}</span
        >
        <div>
          <h2>{{ userData?.first_name }} {{ userData?.last_name }}</h2>
          <p>{{ userData?.email }}</p>
        </div>
      </div>
      <div class="section-heading">
        <h3>Informations personnelles</h3>
        <p>Mettez à jour les informations de votre compte.</p>
      </div>
      <dl class="profile-fields">
        <div
          v-for="field in editableFields"
          :key="field.key"
          class="profile-row"
        >
          <div class="field-value">
            <dt>{{ field.label }}</dt>
            <dd v-if="field.key === 'birth_date'">{{ formattedBirthDate }}</dd>
            <dd v-else-if="field.key === 'gender'">{{ formattedGender }}</dd>
            <dd v-else>{{ userData?.[field.key] || "Non renseigné" }}</dd>
          </div>
          <NsButton
            label="Modifier"
            icon="pi pi-pencil"
            :aria-label="`Modifier : ${field.label}`"
            text
            size="small"
            @click="openEditDialog(field.key)"
          />
        </div>
      </dl>
    </NsCard>
    <NsCard class="account-card">
      <div class="account-row">
        <div>
          <h3>Mot de passe</h3>
          <p>Modifiez le mot de passe de votre compte.</p>
        </div>
        <NsButton
          label="Changer le mot de passe"
          icon="pi pi-lock"
          severity="secondary"
          outlined
          @click="openEditDialog('password')"
        />
      </div>
      <div class="account-row danger-row">
        <div>
          <h3>Supprimer mon compte</h3>
          <p>Cette action supprime définitivement votre compte.</p>
        </div>
        <NsButton
          label="Supprimer mon compte"
          icon="pi pi-trash"
          severity="danger"
          outlined
          @click="confirmDeleteAccount($event)"
        />
      </div>
    </NsCard>
    <ConfirmPopup />
    <NsDialog
      v-model:visible="editDialogVisible"
      :header="getDialogHeader(fieldToEdit)"
      modal
      :closable="false"
      :style="{ width: '30rem', maxWidth: 'calc(100vw - 2rem)' }"
    >
      <form
        id="profile-edit-form"
        class="edit-form"
        @submit.prevent="saveEdit"
        novalidate
      >
        <div v-if="fieldToEdit === 'gender'" class="gender-field">
          <span id="profile-gender-label" class="field-label">Genre</span>
          <NsSelectButton
            v-model="fieldValue"
            aria-labelledby="profile-gender-label"
            :options="GENDER"
            optionLabel="label"
            optionValue="value"
            :defaultValue="userData?.gender"
          />
        </div>
        <NsFormField
          v-else
          id="profile-edit-value"
          :label="
            editableFields.find((field) => field.key === fieldToEdit)?.label ||
            'Nouveau mot de passe'
          "
        >
          <NsPasswordInput
            v-if="fieldToEdit === 'password'"
            inputId="profile-edit-value"
            v-model="fieldValue"
            :inputProps="{ autocomplete: 'new-password' }"
            toggleMask
            fluid
          />
          <NsDatePicker
            v-else-if="fieldToEdit === 'birth_date'"
            inputId="profile-edit-value"
            v-model="fieldValue as unknown as Date"
            showIcon
            dateFormat="dd/mm/yy"
            :maxDate="today"
            fluid
          />
          <NsInputMask
            v-else-if="fieldToEdit === 'phone_number'"
            id="profile-edit-value"
            v-model="fieldValue"
            autocomplete="tel"
            mask="(+33) 9-99-99-99-99"
            placeholder="(+33) 0-00-00-00-00"
            fluid
          />
          <NsInput
            v-else
            id="profile-edit-value"
            v-model="fieldValue"
            :type="fieldToEdit === 'email' ? 'email' : 'text'"
            fluid
          />
        </NsFormField>
      </form>
      <template #footer>
        <div class="dialog-actions">
          <NsButton
            label="Annuler"
            severity="secondary"
            text
            @click="cancelEdit"
          /><NsButton
            label="Enregistrer"
            icon="pi pi-check"
            type="submit"
            form="profile-edit-form"
          />
        </div>
      </template>
    </NsDialog>
  </section>
</template>

<style scoped>
.profile-page {
  max-width: 880px;
  margin: 0 auto;
}
.profile-card {
  padding: clamp(1.2rem, 3vw, 2rem);
}
.profile-summary {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  padding-bottom: 1.8rem;
  border-bottom: 1px solid #e7ebe5;
}
.profile-avatar {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  flex-shrink: 0;
  background: #e7eee7;
  color: #1d4d40;
  border: 1px solid #dce6d9;
  border-radius: 16px;
  font-size: 1.15rem;
  font-weight: 650;
  text-transform: uppercase;
}
.profile-summary > div {
  min-width: 0;
}
h2 {
  font-size: 1.3rem;
  margin: 0 0 0.25rem;
  letter-spacing: -0.025em;
  overflow-wrap: anywhere;
}
.profile-summary p {
  margin: 0;
  color: #69766f;
  font-size: 0.85rem;
  overflow-wrap: anywhere;
}
.section-heading {
  margin: 1.8rem 0 0.5rem;
}
h3 {
  font-size: 0.97rem;
  margin: 0;
  font-weight: 650;
}
.section-heading p,
.account-row p {
  margin: 0.45rem 0 0;
  font-size: 0.81rem;
  color: #69766f;
  line-height: 1.6;
}
.profile-fields {
  margin: 0;
}
.profile-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 0;
}
.profile-row + .profile-row {
  border-top: 1px solid #edf0eb;
}
.field-value {
  min-width: 0;
}
dt {
  color: #69766f;
  font-size: 0.76rem;
  margin-bottom: 0.35rem;
}
dd {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 500;
  overflow-wrap: anywhere;
}
.profile-row :deep(.p-button) {
  flex-shrink: 0;
}
.account-card {
  margin-top: 1.3rem;
  padding: 0 clamp(1.2rem, 3vw, 2rem);
}
.account-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  padding: 1.6rem 0;
}
.account-row :deep(.p-button) {
  flex-shrink: 0;
  font-size: 0.8rem;
}
.danger-row {
  border-top: 1px solid #e7ebe5;
}
.danger-row h3 {
  color: #a54435;
}
.edit-form {
  padding: 0.5rem 0 1rem;
}
.gender-field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.65rem;
}
.field-label {
  font-size: 0.84rem;
  font-weight: 600;
}
.dialog-actions {
  display: flex;
  gap: 0.7rem;
  justify-content: flex-end;
  flex-wrap: wrap;
}
@media (max-width: 600px) {
  .account-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .profile-avatar {
    width: 48px;
    height: 48px;
    border-radius: 13px;
  }
  .profile-summary {
    gap: 0.8rem;
  }
  h2 {
    font-size: 1.1rem;
  }
}
</style>
