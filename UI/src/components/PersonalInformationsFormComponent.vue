<script setup lang="ts">
import NsNumberInput from "@/components/ui/NsNumberInput.vue"
import NsSelectButton from "@/components/ui/NsSelectButton.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import { GENDER } from "@/assets/js/constants"
import { useProgressRecord } from "@/stores/progressRecordStore"

const progressRecordStore = useProgressRecord()
const props = defineProps<{ invalidFields: Record<string, boolean> }>()
</script>

<template>
  <section class="personal-form" aria-labelledby="personal-title">
    <div class="step-heading">
      <span>ÉTAPE 01</span>
      <h2 id="personal-title">Commençons par vous.</h2>
      <p>Ces informations permettent d'estimer vos besoins énergétiques.</p>
    </div>
    <div class="personal-fields">
      <div class="gender-field">
        <span id="calorie-gender-label" class="field-label"
          >Genre <span aria-hidden="true">*</span></span
        >
        <NsSelectButton
          v-model="progressRecordStore.progressRecord.gender"
          :invalid="props.invalidFields.gender"
          :options="GENDER"
          optionLabel="label"
          optionValue="value"
          defaultValue="H"
          aria-labelledby="calorie-gender-label"
          :aria-describedby="
            props.invalidFields.gender ? 'calorie-gender-error' : undefined
          "
          class="gender-options"
        />
        <small
          v-if="props.invalidFields.gender"
          id="calorie-gender-error"
          class="field-error"
          >Sélectionnez votre genre.</small
        >
      </div>
      <NsFormField
        v-slot="{ describedby }"
        id="age"
        label="Âge"
        required
        :error="
          props.invalidFields.age
            ? 'Renseignez un âge supérieur à zéro.'
            : undefined
        "
      >
        <NsNumberInput
          v-model="progressRecordStore.progressRecord.age"
          :invalid="props.invalidFields.age"
          inputId="age"
          :pt="{ pcInputText: { root: { 'aria-describedby': describedby } } }"
          suffix=" ans"
          fluid
          :minFractionDigits="0"
          :maxFractionDigits="0"
          :min="0"
          placeholder="Ex. 30"
        />
      </NsFormField>
      <NsFormField
        v-slot="{ describedby }"
        id="height"
        label="Taille"
        required
        :error="
          props.invalidFields.height_cm
            ? 'Renseignez une taille supérieure à zéro.'
            : undefined
        "
      >
        <NsNumberInput
          v-model="progressRecordStore.progressRecord.height_cm"
          :invalid="props.invalidFields.height_cm"
          inputId="height"
          :pt="{ pcInputText: { root: { 'aria-describedby': describedby } } }"
          suffix=" cm"
          fluid
          :minFractionDigits="1"
          :maxFractionDigits="1"
          :min="0"
          placeholder="Ex. 175"
        />
      </NsFormField>
      <NsFormField
        v-slot="{ describedby }"
        id="weight"
        label="Poids"
        required
        :error="
          props.invalidFields.weight_kg
            ? 'Renseignez un poids supérieur à zéro.'
            : undefined
        "
      >
        <NsNumberInput
          v-model="progressRecordStore.progressRecord.weight_kg"
          :invalid="props.invalidFields.weight_kg"
          inputId="weight"
          :pt="{ pcInputText: { root: { 'aria-describedby': describedby } } }"
          suffix=" kg"
          fluid
          :minFractionDigits="1"
          :maxFractionDigits="1"
          :min="0"
          placeholder="Ex. 70"
        />
      </NsFormField>
    </div>
    <p class="required-note">
      Les champs marqués d'un astérisque sont obligatoires.
    </p>
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
.personal-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.gender-field {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.field-label {
  color: #344b3e;
  font-size: 0.85rem;
  font-weight: 600;
}
.field-label > span {
  color: #8e6a4e;
}
.gender-options {
  display: flex;
  width: 100%;
}
.gender-options :deep(.p-togglebutton) {
  flex: 1;
  min-height: 2.75rem;
}
.field-error {
  color: #b13f3c;
  font-size: 0.78rem;
}
.required-note {
  color: #7b857f;
  font-size: 0.73rem;
  margin: 1.5rem 0 0;
}
@media (max-width: 600px) {
  .personal-fields {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
  .step-heading {
    margin-bottom: 1.5rem;
  }
}
</style>
