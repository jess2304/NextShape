<script setup lang="ts">
import { isCancel } from "axios"
import Stepper from "primevue/stepper"
import StepList from "primevue/steplist"
import Step from "primevue/step"
import StepPanel from "primevue/steppanel"
import NsButton from "@/components/ui/NsButton.vue"
import NsCard from "@/components/ui/NsCard.vue"
import PageHeader from "@/components/layout/PageHeader.vue"
import StepPanels from "primevue/steppanels"
import StepItem from "primevue/stepitem"
import PersonalInformationsFormComponent from "@/components/PersonalInformationsFormComponent.vue"
import PhysicalActivityGoalFormComponent from "@/components/PhysicalActivityGoalFormComponent.vue"
import RecapComponent from "@/components/RecapComponent.vue"
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useProgressRecord } from "@/stores/progressRecordStore"
import { resolveApiErrorMessage, showToast } from "@/assets/js/utils"
import { useToast } from "primevue"

// Store
const progressRecordStore = useProgressRecord()
const toast = useToast()

// Detect mobile layout (responsive design)
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
    if (isCancel(error)) return
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(
        error,
        "Échec de l'enregistrement des besoins caloriques"
      )
    )
  }
}

// Initialize invalid field tracking
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
  <div class="calories-page">
    <PageHeader
      eyebrow="LES CALCULATRICES"
      title="Vos besoins, à votre rythme."
      description="Estimez vos besoins caloriques à partir de vos informations, de votre activité et de votre objectif."
    />
    <NsCard class="calculator-card">
      <Stepper v-if="!isMobile" value="1" linear class="calorie-stepper">
        <StepList class="calorie-step-list">
          <Step value="1">Votre profil</Step>
          <Step value="2">Votre objectif</Step>
          <Step value="3">Le récapitulatif</Step>
        </StepList>
        <StepPanels>
          <StepPanel v-slot="{ activateCallback }" value="1">
            <PersonalInformationsFormComponent :invalidFields="invalidFields" />
            <div class="step-actions step-actions-next">
              <NsButton
                label="Continuer"
                icon="pi pi-arrow-right"
                iconPos="right"
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
          <StepPanel v-slot="{ activateCallback }" value="2">
            <PhysicalActivityGoalFormComponent :invalidFields="invalidFields" />
            <div class="step-actions">
              <NsButton
                label="Retour"
                severity="secondary"
                outlined
                icon="pi pi-arrow-left"
                @click="activateCallback('1')"
              />
              <NsButton
                label="Continuer"
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
          <StepPanel v-slot="{ activateCallback }" value="3">
            <RecapComponent />
            <div class="step-actions">
              <NsButton
                label="Retour"
                severity="secondary"
                outlined
                icon="pi pi-arrow-left"
                @click="activateCallback('2')"
              />
              <NsButton
                label="Calculer mes besoins"
                icon="pi pi-calculator"
                @click="calculateCalories"
              />
            </div>
          </StepPanel>
        </StepPanels>
      </Stepper>

      <Stepper
        v-else
        value="1"
        linear
        class="calorie-stepper calorie-stepper-mobile"
      >
        <StepItem value="1">
          <Step value="1">Votre profil</Step>
          <StepPanel v-slot="{ activateCallback }" value="1">
            <PersonalInformationsFormComponent :invalidFields="invalidFields" />
            <div class="step-actions step-actions-next">
              <NsButton
                label="Continuer"
                icon="pi pi-arrow-right"
                iconPos="right"
                @click="activateCallback('2')"
              />
            </div>
          </StepPanel>
        </StepItem>
        <StepItem value="2">
          <Step value="2">Votre objectif</Step>
          <StepPanel v-slot="{ activateCallback }" value="2">
            <PhysicalActivityGoalFormComponent :invalidFields="invalidFields" />
            <div class="step-actions">
              <NsButton
                label="Retour"
                severity="secondary"
                outlined
                icon="pi pi-arrow-left"
                @click="activateCallback('1')"
              />
              <NsButton
                label="Continuer"
                icon="pi pi-arrow-right"
                iconPos="right"
                @click="activateCallback('3')"
              />
            </div>
          </StepPanel>
        </StepItem>
        <StepItem value="3">
          <Step value="3">Le récapitulatif</Step>
          <StepPanel v-slot="{ activateCallback }" value="3">
            <RecapComponent />
            <div class="step-actions">
              <NsButton
                label="Retour"
                severity="secondary"
                outlined
                icon="pi pi-arrow-left"
                @click="activateCallback('2')"
              />
              <NsButton
                label="Calculer mes besoins"
                icon="pi pi-calculator"
                @click="calculateCalories"
              />
            </div>
          </StepPanel>
        </StepItem>
      </Stepper>
    </NsCard>
    <p class="calorie-footnote">
      <i class="pi pi-bookmark" aria-hidden="true" /> Vos calculs de calories
      sont enregistrés dans votre historique.
    </p>
  </div>
</template>

<style scoped>
.calories-page {
  max-width: 940px;
  margin-inline: auto;
}
.calculator-card {
  padding: clamp(1.25rem, 4vw, 2.5rem);
}
.calorie-step-list {
  padding: 0 0 1.75rem;
  margin-bottom: 1.75rem;
  border-bottom: 1px solid #e8ece5;
}
.calorie-stepper :deep(.p-steppanels) {
  padding: 0;
}
.calorie-stepper :deep(.p-steppanel) {
  background: transparent;
}
.calorie-stepper :deep(.p-step-title) {
  font-size: 0.85rem;
  font-weight: 600;
}
.calorie-stepper :deep(.p-step-number) {
  font-size: 0.8rem;
  min-width: 2rem;
  height: 2rem;
  border-width: 1px;
}
.calorie-stepper :deep(.p-step-header) {
  gap: 0.6rem;
}
.step-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-top: 1.5rem;
  margin-top: 1.75rem;
  border-top: 1px solid #e8ece5;
}
.step-actions-next {
  justify-content: flex-end;
}
.calorie-footnote {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 0.6rem;
  color: #69766f;
  font-size: 0.75rem;
  line-height: 1.6;
  margin: 1.25rem 0 0;
}
.calorie-footnote i {
  font-size: 0.75rem;
}
.calorie-stepper-mobile :deep(.p-stepitem) {
  margin-bottom: 0.5rem;
}
.calorie-stepper-mobile :deep(.p-step) {
  padding: 0.7rem 0;
}
.calorie-stepper-mobile :deep(.p-steppanel) {
  padding: 1rem 0 1.5rem;
}
.calorie-stepper-mobile :deep(.p-steppanel-content) {
  padding: 0;
  margin: 0;
  width: 100%;
}
.calorie-stepper-mobile :deep(.p-stepper-separator) {
  display: none;
}
@media (max-width: 480px) {
  .step-actions > :last-child {
    flex-grow: 1;
  }
  .calorie-footnote {
    text-align: left;
    justify-content: flex-start;
  }
}
</style>
