<script setup lang="ts">
import Fieldset from "primevue/fieldset"
import Avatar from "primevue/avatar"
import { useProgressRecords } from "@/stores/progressRecordsStore"
import { onMounted, ref } from "vue"
import { showToast, formatDate } from "@/assets/js/utils"
import { ACTIVITY_DESCRIPTIONS, ACTIVITY_LEVELS } from "@/assets/js/constants"
import { useToast } from "primevue"
import DataTable from "primevue/datatable"
import Column from "primevue/column"
import Button from "primevue/button"
import Select from "primevue/select"
import Tag from "primevue/tag"
import InputNumber from "primevue/inputnumber"

// Appel des stores
const progressRecordsStore = useProgressRecords()
const toast = useToast()
const editingRows = ref([])
// Appel du GET pour avoir nos données stockées.
onMounted(async () => {
  try {
    await progressRecordsStore.getProgressRecords()
  } catch (error: any) {
    showToast(
      toast,
      "error",
      "Erreur",
      error?.response?.data?.errors?.non_field_errors?.[0] ||
        error?.response?.data?.message ||
        "Échec du chargement de votre historique"
    )
  }
})

const goalOptions: Array<Record<string, string>> = [
  { label: "Maintien", value: "maintien" },
  { label: "Perte de poids", value: "perte" },
  { label: "Prise de masse", value: "prise" },
]
const goalLabels: Record<string, string> = {
  maintien: "Maintien",
  perte: "Perte de poids",
  prise: "Prise de masse",
}
const goalSeverity: Record<string, string> = {
  maintien: "info",
  perte: "warn",
  prise: "success",
}

const activityLabels = Object.fromEntries(
  ACTIVITY_LEVELS.map((lvl) => [lvl.value, lvl.label])
)

const activitySeverity: Record<string, string> = {
  sedentaire: "secondary",
  leger: "info",
  modere: "success",
  intense: "warn",
  tres_intense: "danger",
}

const onRowEditSave = async (event: any) => {
  const { newData } = event

  const requiredFields = ["weight_kg", "height_cm", "goal", "activity_level"]

  const hasEmpty = requiredFields.some((field) => {
    return (
      newData[field] === null ||
      newData[field] === "" ||
      newData[field] === undefined
    )
  })

  if (hasEmpty) {
    toast.add({
      severity: "warn",
      summary: "Champs invalides",
      detail: "Tous les champs doivent être remplis.",
      life: 3000,
    })
    event.originalEvent.preventDefault()
    return
  }

  try {
    await progressRecordsStore.updateRecord(newData.id, {
      weight_kg: newData.weight_kg,
      height_cm: newData.height_cm,
      goal: newData.goal,
      activity_level: newData.activity_level,
    })
    showToast(
      toast,
      "success",
      "Succès",
      "La mise à jour a été faite avec succès"
    )
  } catch (error: any) {
    showToast(
      toast,
      "error",
      "Erreur",
      error?.response?.data?.errors?.non_field_errors?.[0] ||
        error?.response?.data?.message ||
        "Échec de l'enregistrement"
    )
  }
}

const deleteRecord = async (id: number) => {
  try {
    await progressRecordsStore.deleteRecord(id)
    toast.add({
      severity: "success",
      summary: "Supprimé",
      detail: "Enregistrement supprimé",
      life: 3000,
    })
  } catch (err) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Impossible de supprimer l'enregistrement",
      life: 3000,
    })
  }
}
</script>
<template>
  <Fieldset
    :pt="{
      legend: { class: 'bg-transparent' },
      root: { class: 'shadow-2 border-round-lg p-4' },
    }"
  >
    <template #legend>
      <div class="flex items-center pl-2 gap-3">
        <Avatar image="/Historique.png" shape="circle" />
        <span class="font-bold text-2xl">Historique de calculs</span>
      </div>
    </template>

    <DataTable
      :value="progressRecordsStore.progressRecords"
      dataKey="id"
      responsiveLayout="scroll"
      editMode="row"
      v-model:editingRows="editingRows"
      @row-edit-save="onRowEditSave"
      paginator
      :rows="5"
      :rowsPerPageOptions="[5, 10, 20, 50]"
    >
      <Column field="date" header="Date">
        <template #body="{ data }">
          {{ formatDate(data.date) }}
        </template>
      </Column>

      <Column field="weight_kg" header="Poids (kg)">
        <template #body="{ data }"> {{ data.weight_kg }} kg </template>
        <template #editor="{ data, field }">
          <InputNumber
            v-model="data[field]"
            suffix=" kg"
            class="w-full"
            :minFractionDigits="1"
            :maxFractionDigits="1"
            :min="0"
            showButtons
            fluid
          />
        </template>
      </Column>

      <Column field="height_cm" header="Taille (cm)">
        <template #body="{ data }"> {{ data.height_cm }} cm </template>
        <template #editor="{ data, field }">
          <InputNumber
            v-model="data[field]"
            suffix=" cm"
            class="w-full"
            :minFractionDigits="1"
            :maxFractionDigits="1"
            :min="0"
            showButtons
            fluid
          />
        </template>
      </Column>

      <Column field="activity_level" header="Activité physique">
        <template #body="{ data }">
          <Tag
            :value="activityLabels[data.activity_level]"
            :severity="activitySeverity[data.activity_level]"
            rounded
          />
        </template>
        <template #editor="{ data, field }">
          <Select
            v-model="data[field]"
            :options="ACTIVITY_LEVELS"
            option-label="label"
            option-value="value"
            class="w-full"
            placeholder="Choisir"
          >
            <template #option="slotProps">
              <div class="flex flex-col gap-2">
                <span class="font-semibold">{{ slotProps.option.label }}</span>
                <small class="text-xs text-gray-500">
                  {{ ACTIVITY_DESCRIPTIONS[slotProps.option.value] }}
                </small>
              </div>
            </template>
          </Select>
        </template>
      </Column>

      <Column field="goal" header="Objectif">
        <template #body="{ data }">
          <Tag
            :value="goalLabels[data.goal]"
            :severity="goalSeverity[data.goal]"
            rounded
          />
        </template>
        <template #editor="{ data, field }">
          <Select
            v-model="data[field]"
            :options="goalOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </template>
      </Column>

      <Column field="imc" header="IMC">
        <template #body="{ data }">
          {{ data.imc.toFixed(1) }}
        </template>
      </Column>

      <Column field="bmr" header="BMR">
        <template #body="{ data }"> {{ data.bmr }} kcal </template>
      </Column>

      <Column field="tdee" header="TDEE">
        <template #body="{ data }"> {{ data.tdee }} kcal </template>
      </Column>

      <Column field="calories_recommandees" header="Calories">
        <template #body="{ data }">
          <span class="font-semibold text-primary"
            >{{ data.calories_recommandees }} kcal</span
          >
        </template>
      </Column>

      <Column header="">
        <template #body="{ data }">
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            @click="deleteRecord(data.id)"
          />
        </template>
      </Column>
      <Column
        :rowEditor="true"
        style="width: 5%; min-width: 8rem"
        bodyStyle="text-align:center"
      ></Column>
    </DataTable>
  </Fieldset>
</template>
