<script setup lang="ts">
import InputNumber from "primevue/inputnumber"
import SelectButton from "primevue/selectbutton"
import Toast from "primevue/toast"
import { GENDER } from "@/assets/js/constants"
import { useProgressRecord } from "@/stores/progressRecordStore"

// Appel des stores
const progressRecordStore = useProgressRecord()

const props = defineProps<{
  invalidFields: Record<string, boolean>
}>()
</script>

<template>
  <div>
    <h2 class="text-5xl text-center text-primary">Informations personnelles</h2>
    <div class="formgrid grid">
      <div class="field col-12 md:col-6">
        <label>Genre*</label>
        <SelectButton
          class="w-full"
          v-model="progressRecordStore.progressRecord.gender"
          :invalid="props.invalidFields.gender"
          :options="GENDER"
          optionLabel="label"
          optionValue="value"
          defaultValue="H"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Âge*</label>
        <InputNumber
          v-model="progressRecordStore.progressRecord.age"
          :invalid="props.invalidFields.age"
          inputId="age"
          suffix=" ans"
          showButtons
          class="w-full"
          fluid
          :minFractionDigits="0"
          :maxFractionDigits="0"
          :min="0"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Taille (cm)*</label>
        <InputNumber
          v-model="progressRecordStore.progressRecord.height_cm"
          :invalid="props.invalidFields.height_cm"
          inputId="height"
          suffix=" cm"
          showButtons
          class="w-full"
          fluid
          :minFractionDigits="1"
          :maxFractionDigits="1"
          :min="0"
        />
      </div>
      <div class="field col-12 md:col-6">
        <label>Poids (kg)*</label>
        <InputNumber
          v-model="progressRecordStore.progressRecord.weight_kg"
          inputId="weight"
          :invalid="props.invalidFields.weight_kg"
          suffix=" kg"
          showButtons
          class="w-full"
          fluid
          :minFractionDigits="1"
          :maxFractionDigits="1"
          :min="0"
        />
      </div>
    </div>
    <Toast />
  </div>
</template>
