<script setup lang="ts">
import { computed } from "vue"
import SelectButton from "primevue/selectbutton"
import Toast from "primevue/toast"
import { useProgressRecord } from "@/stores/progressRecordStore"
import {
  ACTIVITY_LEVELS,
  ACTIVITY_DESCRIPTIONS,
  GOALS,
} from "@/assets/js/constants"

// Appel des stores
const progressRecordStore = useProgressRecord()

// Champs invalides pour validation visuelle
const props = defineProps<{
  invalidFields: Record<string, boolean>
}>()

// Description dynamique à droite
const activityDescription = computed(() => {
  return (
    ACTIVITY_DESCRIPTIONS[
      progressRecordStore.progressRecord.activity_level || ""
    ] || ""
  )
})
</script>

<template>
  <div>
    <h2 class="text-5xl text-center text-primary">
      Activité physique & Objectif
    </h2>
    <div class="grid mt-5">
      <div class="col-12 md:col-6">
        <label class="block mb-2 font-medium"
          >Niveau d'activité physique*</label
        >
        <SelectButton
          v-model="progressRecordStore.progressRecord.activity_level"
          :options="ACTIVITY_LEVELS"
          optionLabel="label"
          optionValue="value"
          :invalid="props.invalidFields.activity_level"
          class="w-full"
        />
      </div>
      <div class="col-12 md:col-6">
        <label class="block mb-2 font-medium">Description</label>
        <div
          class="p-3 border-round bg-surface-100 text-sm shadow-1 min-h-[6rem]"
        >
          {{
            activityDescription ||
            "Sélectionnez un niveau pour voir les détails."
          }}
        </div>
      </div>
    </div>
    <div class="mt-5">
      <label class="block mb-2 font-medium">Objectif*</label>
      <SelectButton
        v-model="progressRecordStore.progressRecord.goal"
        :options="GOALS"
        optionLabel="label"
        optionValue="value"
        :invalid="props.invalidFields.goal"
        class="w-full"
      />
    </div>
    <Toast />
  </div>
</template>
