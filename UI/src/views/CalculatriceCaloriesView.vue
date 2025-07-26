<script setup lang="ts">
import Stepper from "primevue/stepper"
import StepList from "primevue/steplist"
import Step from "primevue/step"
import StepPanel from "primevue/steppanel"
import Button from "primevue/button"
import PersonalInformationsFormComponent from "@/components/PersonalInformationsFormComponent.vue"
import PhysicalActivityGoalFormComponent from "@/components/PhysicalActivityGoalFormComponent.vue"
import RecapComponent from "@/components/RecapComponent.vue"
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useProgressRecord } from "@/stores/progressRecordStore"
import { showToast } from "@/assets/js/utils"
import { useToast } from "primevue"

// Appel des stores
const progressRecordStore = useProgressRecord()
const toast = useToast()

// Vérifier si l'appareil est un smartphone ou pas (responsive design)
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}
onMounted(() => {
  checkMobile()
  window.addEventListener("resize", checkMobile)
})
onBeforeUnmount(() => {
  window.removeEventListener("resize", checkMobile)
})

const calculateCalories = async () => {
  try {
    const { success, message } = await progressRecordStore.calculateCalories()
    if (success) showToast(toast, "success", "Succès", message)
    else
      showToast(
        toast,
        "error",
        "Erreur",
        "Échec de l'enregistrement des besoins caloriques"
      )
  } catch (error: any) {
    showToast(
      toast,
      "error",
      "Erreur",
      error?.response?.data?.errors?.non_field_errors?.[0] ||
        error?.response?.data?.message ||
        "Échec de l'enregistrement des besoins caloriques"
    )
  }
}

// Init des données insérées et invalides
const invalidFields = ref<Record<string, boolean>>({})

const validatePersonalInformations = (): boolean => {
  const { gender, age, height_cm, weight_kg } =
    progressRecordStore.progressRecord
  invalidFields.value = {}

  if (!gender) invalidFields.value.gender = true
  if (!age || age <= 0) invalidFields.value.age = true
  if (!height_cm || height_cm <= 0) invalidFields.value.height_cm = true
  if (!weight_kg || weight_kg <= 0) invalidFields.value.weight_kg = true

  return Object.keys(invalidFields.value).length === 0
}

const validatePhysicalActivityGoal = (): boolean => {
  const { activity_level, goal } = progressRecordStore.progressRecord
  invalidFields.value = {}

  if (!activity_level) invalidFields.value.activity_level = true
  if (!goal) invalidFields.value.goal = true

  return Object.keys(invalidFields.value).length === 0
}

const handleForNextStep = async (
  step: string,
  validateFn: () => boolean | Promise<boolean>,
  activateCallback: (step: string) => void
) => {
  const isValid = await validateFn()
  if (isValid) {
    activateCallback(step)
  } else {
    showToast(
      toast,
      "error",
      "Champs invalides",
      "Veuillez corriger les erreurs."
    )
  }
}
</script>
<template>
  <!-- PC -->
  <Stepper v-if="!isMobile" value="1" linear class="basis-[50rem]">
    <StepList>
      <Step value="1">Informations personnelles</Step>
      <Step value="2">Activité physique et Objectif</Step>
      <Step value="3">Récapitulatif</Step>
    </StepList>
    <StepPanels>
      <StepPanel
        v-slot="{ activateCallback }"
        value="1"
        class="p-4 shadow-2 border-round-lg mx-auto"
      >
        <div class="w-8 mx-auto">
          <PersonalInformationsFormComponent :invalidFields="invalidFields" />
        </div>

        <div class="flex pt-6 justify-end">
          <Button
            label="Suivant"
            icon="pi pi-arrow-right"
            @click="
              handleForNextStep(
                '2',
                validatePersonalInformations,
                activateCallback
              )
            "
          />
        </div>
      </StepPanel>
      <StepPanel
        v-slot="{ activateCallback }"
        value="2"
        class="p-4 shadow-2 border-round-lg mx-auto"
      >
        <div class="w-8 mx-auto">
          <PhysicalActivityGoalFormComponent :invalidFields="invalidFields" />
        </div>

        <div class="flex pt-6 justify-between">
          <Button
            label="Retour"
            severity="secondary"
            icon="pi pi-arrow-left"
            @click="activateCallback('1')"
          />
          <Button
            label="Suivant"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="
              handleForNextStep(
                '3',
                validatePhysicalActivityGoal,
                activateCallback
              )
            "
          />
        </div>
      </StepPanel>
      <StepPanel
        v-slot="{ activateCallback }"
        value="3"
        class="p-4 shadow-2 border-round-lg mx-auto"
      >
        <div class="w-8 mx-auto">
          <RecapComponent />
        </div>
        <div class="pt-6">
          <Button
            label="Retour"
            severity="secondary"
            icon="pi pi-arrow-left"
            @click="activateCallback('2')"
          />
          <Button
            label="Calculer"
            icon="pi pi-calculator"
            @click="calculateCalories"
          />
        </div>
      </StepPanel>
    </StepPanels>
  </Stepper>

  <!-- Mobile -->
  <Stepper v-else value="1" linear class="basis-[50rem]">
    <StepItem>
      <Step value="1">Informations personnelles</Step>
      <StepPanel
        v-slot="{ activateCallback }"
        value="1"
        class="p-4 shadow-2 border-round-lg mx-auto"
      >
        <div class="w-8 mx-auto">
          <PersonalInformationsFormComponent :invalidFields="invalidFields" />
        </div>

        <div class="flex pt-6 justify-end">
          <Button
            label="Suivant"
            icon="pi pi-arrow-right"
            @click="activateCallback('2')"
          />
        </div>
      </StepPanel>
    </StepItem>
    <StepItem>
      <Step value="2">Activité physique et Objectif</Step>
      <StepPanel
        v-slot="{ activateCallback }"
        value="2"
        class="p-4 shadow-2 border-round-lg mx-auto"
      >
        <div class="w-8 mx-auto">
          <PhysicalActivityGoalFormComponent :invalidFields="invalidFields" />
        </div>

        <div class="flex pt-6 justify-between">
          <Button
            label="Retour"
            severity="secondary"
            icon="pi pi-arrow-left"
            @click="activateCallback('1')"
          />
          <Button
            label="Suivant"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="activateCallback('3')"
          />
        </div>
      </StepPanel>
    </StepItem>
    <StepItem>
      <Step value="3">Récapitulatif</Step>
      <StepPanel
        v-slot="{ activateCallback }"
        value="3"
        class="p-4 shadow-2 border-round-lg mx-auto"
      >
        <div class="w-8 mx-auto">
          <RecapComponent />
        </div>

        <div class="pt-6">
          <Button
            label="Retour"
            severity="secondary"
            icon="pi pi-arrow-left"
            @click="activateCallback('2')"
          />
          <Button
            label="Calculer"
            icon="pi pi-calculator"
            @click="calculateCalories"
          />
        </div>
      </StepPanel>
    </StepItem>
  </Stepper>
</template>
