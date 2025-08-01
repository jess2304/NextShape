<script setup lang="ts">
import Dialog from "primevue/dialog"
import InputNumber from "primevue/inputnumber"
import Select from "primevue/select"
import Button from "primevue/button"
import { ACTIVITY_LEVELS, ACTIVITY_DESCRIPTIONS } from "@/assets/js/constants"
import { useProgressRecords } from "@/stores/progressRecordsStore"
import { showToast } from "@/assets/js/utils"
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
const goalOptions: Array<Record<string, string>> = [
  { label: "Maintien", value: "maintien" },
  { label: "Perte de poids", value: "perte" },
  { label: "Prise de masse", value: "prise" },
]
// Préremplir quand on ouvre la modale
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

  try {
    await store.updateRecord(recordId.value!, {
      weight_kg: weight_kg.value,
      height_cm: height_cm.value,
      activity_level: activity_level.value,
      goal: goal.value,
    })
    showToast(toast, "success", "Succès", "Enregistrement modifié avec succès.")
    visible.value = false
  } catch (err) {
    showToast(
      toast,
      "error",
      "Erreur",
      "Impossible de modifier l’enregistrement."
    )
  }
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Modifier l'enregistrement"
    class="mx-1 w-full sm:w-10 md:w-6"
  >
    <div class="formgrid grid">
      <div class="field col-12">
        <label>Poids (kg)</label>
        <InputNumber
          v-model="weight_kg"
          suffix=" kg"
          showButtons
          class="w-full"
          :min="0"
          :minFractionDigits="1"
          :maxFractionDigits="1"
        />
      </div>

      <div class="field col-12">
        <label>Taille (cm)</label>
        <InputNumber
          v-model="height_cm"
          suffix=" cm"
          showButtons
          class="w-full"
          :min="0"
          :minFractionDigits="1"
          :maxFractionDigits="1"
        />
      </div>

      <div class="field col-12">
        <label>Activité physique</label>
        <Select
          v-model="activity_level"
          :options="ACTIVITY_LEVELS"
          optionLabel="label"
          optionValue="value"
          class="w-full"
        >
          <template #option="slotProps">
            <div class="flex flex-col gap-1">
              <span class="font-semibold">{{ slotProps.option.label }}</span>
              <small class="text-xs text-gray-500">
                {{ ACTIVITY_DESCRIPTIONS[slotProps.option.value] }}
              </small>
            </div>
          </template>
        </Select>
      </div>

      <div class="field col-12">
        <label>Objectif</label>
        <Select
          v-model="goal"
          :options="goalOptions"
          optionLabel="label"
          optionValue="value"
          class="w-full"
        />
      </div>
    </div>

    <div class="flex justify-end gap-2 mt-4">
      <Button label="Annuler" severity="secondary" @click="visible = false" />
      <Button
        label="Enregistrer"
        icon="pi pi-check"
        severity="success"
        @click="save"
      />
    </div>
  </Dialog>
</template>
