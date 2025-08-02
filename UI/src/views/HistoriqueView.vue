<script setup lang="ts">
import Fieldset from "primevue/fieldset"
import Avatar from "primevue/avatar"
import { useProgressRecords } from "@/stores/progressRecordsStore"
import { computed, onMounted, ref } from "vue"
import { showToast, formatDate } from "@/assets/js/utils"
import { ACTIVITY_DESCRIPTIONS, ACTIVITY_LEVELS } from "@/assets/js/constants"
import { useToast } from "primevue"
import DataTable from "primevue/datatable"
import Column from "primevue/column"
import Button from "primevue/button"
import Select from "primevue/select"
import Tag from "primevue/tag"
import InputNumber from "primevue/inputnumber"
import MobileEditModal from "@/components/MobileEditModal.vue"

const isMobile = computed(() => window.innerWidth <= 768)

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

const editMobileVisible = ref(false)
const editingId = ref<number | null>(null)

const openMobileEdit = (recordId: number) => {
  editingId.value = recordId
  editMobileVisible.value = true
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
        <Avatar image="Historique.png" shape="circle" class="w-1 h-1" />
        <span class="font-bold text-xl md:text-2xl text-gray-800"
          >Historique de calculs</span
        >
      </div>
    </template>

    <div v-if="isMobile" class="space-y-3">
      <div
        v-for="record in progressRecordsStore.progressRecords"
        :key="record.id"
        class="border border-gray-200 shadow-sm p-4 rounded-md"
      >
        <div class="text-xs text-gray-500 mb-1">
          Date : {{ formatDate(record.date ?? "") }}
        </div>

        <div class="mb-2">
          <div
            class="flex justify-between gap-2 whitespace-nowrap overflow-auto text-sm"
          >
            <strong>Poids :</strong> {{ record.weight_kg }} kg
          </div>
          <div
            class="flex justify-between gap-2 whitespace-nowrap overflow-auto text-sm"
          >
            <strong>Taille :</strong> {{ record.height_cm }} cm
          </div>
          <div
            class="flex justify-between gap-2 whitespace-nowrap overflow-auto text-sm"
          >
            <strong>Activité :</strong>
            <Tag
              :value="activityLabels[record.activity_level ?? '']"
              :severity="activitySeverity[record.activity_level ?? '']"
              rounded
              class="text-xs"
            />
          </div>
          <div
            class="flex justify-between gap-2 whitespace-nowrap overflow-auto text-sm"
          >
            <strong>Objectif :</strong>
            <Tag
              :value="goalLabels[record.goal ?? '']"
              :severity="goalSeverity[record.goal ?? '']"
              rounded
              class="text-xs"
            />
          </div>
          <div class="text-sm flex flex-column">
            <span><strong>IMC :</strong> {{ record.imc?.toFixed(1) }}</span>
            <span><strong>BMR :</strong> {{ record.bmr }} kcal</span>
            <span><strong>TDEE :</strong> {{ record.tdee }} kcal</span>
            <span
              ><strong>Calories recommandées :</strong>
              {{ record.calories_recommandees }} kcal</span
            >
          </div>
        </div>

        <div class="flex justify-end gap-2">
          <Button icon="pi pi-pencil" @click="openMobileEdit(record.id)" text />
          <Button
            icon="pi pi-trash"
            @click="deleteRecord(record.id)"
            text
            severity="danger"
          />
        </div>
        <div>
          <hr />
        </div>
      </div>
      <MobileEditModal
        v-model:visible="editMobileVisible"
        v-model:recordId="editingId"
      />
    </div>
    <DataTable
      v-else
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
