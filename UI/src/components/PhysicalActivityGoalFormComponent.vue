<script setup lang="ts">
import { computed } from "vue"
import NsSelectButton from "@/components/ui/NsSelectButton.vue"
import { useProgressRecord } from "@/stores/progressRecordStore"
import {
  ACTIVITY_LEVELS,
  ACTIVITY_DESCRIPTIONS,
  GOALS,
} from "@/assets/js/constants"

const progressRecordStore = useProgressRecord()
const props = defineProps<{ invalidFields: Record<string, boolean> }>()
const activityDescription = computed(() => {
  return (
    ACTIVITY_DESCRIPTIONS[
      progressRecordStore.progressRecord.activity_level || ""
    ] || ""
  )
})
</script>

<template>
  <section class="activity-form" aria-labelledby="activity-title">
    <div class="step-heading">
      <span>ÉTAPE 02</span>
      <h2 id="activity-title">Votre rythme, votre objectif.</h2>
      <p>Choisissez ce qui correspond à votre quotidien actuel.</p>
    </div>
    <div class="activity-field">
      <span id="activity-level-label" class="field-label"
        >Niveau d'activité physique <span aria-hidden="true">*</span></span
      >
      <NsSelectButton
        v-model="progressRecordStore.progressRecord.activity_level"
        :options="ACTIVITY_LEVELS"
        optionLabel="label"
        optionValue="value"
        :invalid="props.invalidFields.activity_level"
        aria-labelledby="activity-level-label"
        :aria-describedby="
          props.invalidFields.activity_level
            ? 'activity-description activity-error'
            : 'activity-description'
        "
        class="activity-options"
      />
      <small
        v-if="props.invalidFields.activity_level"
        id="activity-error"
        class="field-error"
        role="alert"
        >Sélectionnez un niveau d'activité.</small
      >
      <div
        id="activity-description"
        class="activity-description"
        aria-live="polite"
      >
        <i class="pi pi-info-circle" aria-hidden="true" />
        <p>
          {{
            activityDescription ||
            "Sélectionnez un niveau pour découvrir à quoi il correspond."
          }}
        </p>
      </div>
    </div>
    <div class="goal-field">
      <span id="calorie-goal-label" class="field-label"
        >Votre objectif <span aria-hidden="true">*</span></span
      >
      <NsSelectButton
        v-model="progressRecordStore.progressRecord.goal"
        :options="GOALS"
        optionLabel="label"
        optionValue="value"
        :invalid="props.invalidFields.goal"
        aria-labelledby="calorie-goal-label"
        :aria-describedby="
          props.invalidFields.goal ? 'calorie-goal-error' : undefined
        "
        class="goal-options"
      />
      <small
        v-if="props.invalidFields.goal"
        id="calorie-goal-error"
        class="field-error"
        role="alert"
        >Sélectionnez un objectif.</small
      >
    </div>
  </section>
</template>

<style scoped>
.step-heading {
  margin-bottom: 2rem;
}
.step-heading > span {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #718074;
  margin-bottom: 0.75rem;
}
.step-heading h2 {
  font-size: clamp(1.25rem, 3vw, 1.65rem);
  font-weight: 600;
  letter-spacing: -0.04em;
  margin: 0 0 0.65rem;
}
.step-heading p {
  font-size: 0.875rem;
  color: #69766f;
  line-height: 1.65;
  margin: 0;
}
.activity-field,
.goal-field {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.goal-field {
  margin-top: 2rem;
}
.field-label {
  color: #344b3e;
  font-size: 0.85rem;
  font-weight: 600;
}
.field-label > span {
  color: #8e6a4e;
}
.activity-options,
.goal-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.activity-options :deep(.p-togglebutton),
.goal-options :deep(.p-togglebutton) {
  flex: 1 1 auto;
  border-radius: 0.625rem;
  border: 1px solid var(--p-togglebutton-border-color);
  min-height: 2.8rem;
}
.activity-options :deep(.p-togglebutton-checked),
.goal-options :deep(.p-togglebutton-checked) {
  border-color: #769781;
}
.activity-description {
  display: flex;
  gap: 0.7rem;
  padding: 1rem;
  background: #f0f4ed;
  border-radius: 0.75rem;
  color: #4e6655;
  align-items: baseline;
  min-height: 4.5rem;
}
.activity-description p {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.65;
}
.activity-description i {
  flex-shrink: 0;
  font-size: 0.85rem;
}
.field-error {
  color: #b13f3c;
  font-size: 0.78rem;
}
@media (max-width: 600px) {
  .goal-options {
    flex-direction: column;
  }
  .step-heading {
    margin-bottom: 1.5rem;
  }
}
</style>
