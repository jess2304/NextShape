<script setup lang="ts">
import { isCancel } from "axios"
import NsDialog from "@/components/ui/NsDialog.vue"
import NsNumberInput from "@/components/ui/NsNumberInput.vue"
import NsSelect from "@/components/ui/NsSelect.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import { ACTIVITY_LEVELS, ACTIVITY_DESCRIPTIONS } from "@/assets/js/constants"
import { useProgressRecords } from "@/stores/progressRecordsStore"
import {
  resolveApiErrorMessage,
  resolveApiMessage,
  showToast,
} from "@/assets/js/utils"
import { useToast } from "primevue"
import { ref, watch } from "vue"

const toast = useToast()
const store = useProgressRecords()

const visible = defineModel<boolean>("visible")
const recordId = defineModel<number | null>("recordId")

const weight_kg = ref<number | null>(null)
const height_cm = ref<number | null>(null)
const activity_level = ref("")

const goal = ref("")
const isSaving = ref(false)
const goalOptions: Array<Record<string, string>> = [
  { label: "Maintien", value: "maintien" },
  { label: "Perte de poids", value: "perte" },
  { label: "Prise de masse", value: "prise" },
]
// Load fields when opening the modal
const load = () => {
  const record = store.progressRecords.find((r) => r.id === recordId.value)
  if (record) {
    weight_kg.value = record.weight_kg
    height_cm.value = record.height_cm
    activity_level.value = record.activity_level ?? ""
    goal.value = record.goal ?? ""
  }
}

watch(visible, (val) => {
  if (val) load()
})

const save = async () => {
  if (
    weight_kg.value === null ||
    height_cm.value === null ||
    activity_level.value === "" ||
    goal.value === ""
  ) {
    showToast(
      toast,
      "error",
      "Champs requis",
      "Veuillez remplir tous les champs."
    )
    return
  }

  isSaving.value = true
  try {
    const response = await store.updateRecord(recordId.value!, {
      weight_kg: weight_kg.value,
      height_cm: height_cm.value,
      activity_level: activity_level.value,
      goal: goal.value,
    })
    showToast(toast, "success", "Succès", resolveApiMessage(response))
    visible.value = false
  } catch (err: any) {
    if (isCancel(err)) return
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(err, "Impossible de modifier l'enregistrement.")
    )
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <NsDialog
    v-model:visible="visible"
    modal
    header="Modifier le calcul"
    class="record-edit-dialog"
    :style="{ width: '30rem', maxWidth: 'calc(100vw - 2rem)' }"
  >
    <p class="record-edit-intro">
      Mettez à jour vos mesures et votre objectif pour cet enregistrement.
    </p>
    <form id="record-edit-form" class="record-edit-form" @submit.prevent="save">
      <div class="record-edit-measures">
        <NsFormField id="record-weight" label="Poids" required>
          <NsNumberInput
            inputId="record-weight"
            v-model="weight_kg"
            suffix=" kg"
            showButtons
            :min="0"
            :minFractionDigits="1"
            :maxFractionDigits="1"
            fluid
          />
        </NsFormField>
        <NsFormField id="record-height" label="Taille" required>
          <NsNumberInput
            inputId="record-height"
            v-model="height_cm"
            suffix=" cm"
            showButtons
            :min="0"
            :minFractionDigits="1"
            :maxFractionDigits="1"
            fluid
          />
        </NsFormField>
      </div>
      <NsFormField id="record-activity" label="Activité physique" required>
        <NsSelect
          inputId="record-activity"
          v-model="activity_level"
          :options="ACTIVITY_LEVELS"
          optionLabel="label"
          optionValue="value"
          fluid
        >
          <template #option="slotProps">
            <div class="record-activity-option">
              <span>{{ slotProps.option.label }}</span
              ><small>{{
                ACTIVITY_DESCRIPTIONS[slotProps.option.value]
              }}</small>
            </div>
          </template>
        </NsSelect>
      </NsFormField>
      <NsFormField id="record-goal" label="Objectif" required>
        <NsSelect
          inputId="record-goal"
          v-model="goal"
          :options="goalOptions"
          optionLabel="label"
          optionValue="value"
          fluid
        />
      </NsFormField>
    </form>
    <template #footer>
      <NsButton
        label="Annuler"
        severity="secondary"
        outlined
        @click="visible = false"
      />
      <NsButton
        type="submit"
        form="record-edit-form"
        label="Enregistrer"
        icon="pi pi-check"
        :loading="isSaving"
        :disabled="isSaving"
      />
    </template>
  </NsDialog>
</template>

<style scoped>
.record-edit-intro {
  margin: 0 0 1.5rem;
  color: var(--ns-muted);
  font-size: 0.875rem;
  line-height: 1.6;
}
.record-edit-form {
  display: grid;
  gap: 1.25rem;
}
.record-edit-measures {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
.record-activity-option {
  display: grid;
  gap: 0.3rem;
  max-width: min(20rem, 75vw);
  white-space: normal;
}
.record-activity-option > span {
  font-weight: 600;
}
.record-activity-option small {
  color: var(--ns-muted);
  line-height: 1.4;
}
@media (max-width: 420px) {
  .record-edit-measures {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
