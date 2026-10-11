<script setup lang="ts">
import { ref } from "vue"
import PageHeader from "@/components/layout/PageHeader.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsInput from "@/components/ui/NsInput.vue"
import NsNumberInput from "@/components/ui/NsNumberInput.vue"
import NsPasswordInput from "@/components/ui/NsPasswordInput.vue"
import NsDatePicker from "@/components/ui/NsDatePicker.vue"
import NsSelect from "@/components/ui/NsSelect.vue"
import NsTextarea from "@/components/ui/NsTextarea.vue"
import NsInputOtp from "@/components/ui/NsInputOtp.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import NsCard from "@/components/ui/NsCard.vue"
import NsBadge from "@/components/ui/NsBadge.vue"
import NsDialog from "@/components/ui/NsDialog.vue"
import NsEmptyState from "@/components/ui/NsEmptyState.vue"
import NsSkeleton from "@/components/ui/NsSkeleton.vue"

const name = ref("")
const weight = ref<number | null>(null)
const password = ref("")
const date = ref<Date | null>(null)
const goal = ref<string | null>(null)
const message = ref("")
const code = ref("")
const dialogOpen = ref(false)
const options = [
  { label: "Maintien", value: "maintien" },
  { label: "Prise de poids", value: "prise" },
]
</script>

<template>
  <PageHeader
    eyebrow="Développement uniquement"
    title="Les composants NextShape"
    description="La même base visuelle pour tous les écrans. Cette page n'est pas incluse dans l'application de production."
  />
  <div class="kit">
    <NsCard>
      <h2>Actions & états</h2>
      <div class="kit__row">
        <NsButton label="Action principale" /><NsButton
          label="Secondaire"
          outlined
        /><NsButton label="Discret" text /><NsButton
          label="Supprimer"
          severity="danger"
          outlined
        />
      </div>
      <div class="kit__row">
        <NsButton label="Chargement" loading /><NsButton
          label="Indisponible"
          disabled
        /><NsButton
          label="Ouvrir une fenêtre"
          icon="pi pi-external-link"
          @click="dialogOpen = true"
        />
      </div>
      <div class="kit__row">
        <NsBadge>Neutre</NsBadge><NsBadge tone="success">Enregistré</NsBadge
        ><NsBadge tone="warning">À vérifier</NsBadge
        ><NsBadge tone="danger">Erreur</NsBadge>
      </div>
    </NsCard>
    <NsCard>
      <h2>Champs de formulaire</h2>
      <div class="kit__fields">
        <NsFormField
          id="kit-name"
          label="Prénom"
          hint="Une aide concise sous le champ."
          v-slot="{ describedby }"
          ><NsInput
            id="kit-name"
            v-model="name"
            placeholder="Votre prénom"
            :aria-describedby="describedby"
        /></NsFormField>
        <NsFormField id="kit-weight" label="Poids"
          ><NsNumberInput
            inputId="kit-weight"
            v-model="weight"
            suffix=" kg"
            :min="0"
            :maxFractionDigits="1"
        /></NsFormField>
        <NsFormField id="kit-password" label="Mot de passe"
          ><NsPasswordInput
            inputId="kit-password"
            v-model="password"
            toggleMask
            :feedback="false"
        /></NsFormField>
        <NsFormField id="kit-date" label="Date"
          ><NsDatePicker
            inputId="kit-date"
            v-model="date"
            dateFormat="dd/mm/yy"
            showIcon
        /></NsFormField>
        <NsFormField id="kit-goal" label="Objectif"
          ><NsSelect
            inputId="kit-goal"
            v-model="goal"
            :options="options"
            optionLabel="label"
            optionValue="value"
            placeholder="Sélectionnez un objectif"
        /></NsFormField>
        <NsFormField
          id="kit-error"
          label="Champ invalide"
          error="Vérifiez cette information."
          v-slot="{ describedby }"
          ><NsInput
            id="kit-error"
            invalid
            aria-invalid="true"
            :aria-describedby="describedby"
        /></NsFormField>
        <NsFormField id="kit-message" label="Message"
          ><NsTextarea id="kit-message" v-model="message" rows="3"
        /></NsFormField>
        <div>
          <p class="kit__label" id="kit-otp-label">Code de vérification</p>
          <NsInputOtp
            v-model="code"
            :length="6"
            integerOnly
            aria-labelledby="kit-otp-label"
          />
        </div>
      </div>
    </NsCard>
    <NsCard
      ><NsEmptyState
        title="Aucun résultat pour le moment"
        description="Une explication courte et une action pour poursuivre."
        ><NsButton label="Commencer" outlined /></NsEmptyState
    ></NsCard>
    <NsCard aria-busy="true" aria-label="Exemple de chargement"
      ><NsSkeleton width="45%" height="1rem" /><NsSkeleton
        height="5rem"
        class="kit__skeleton"
    /></NsCard>
  </div>
  <NsDialog v-model:visible="dialogOpen" header="Une fenêtre NextShape"
    ><p>La fenêtre gère le focus, le clavier et le défilement sur mobile.</p>
    <template #footer
      ><NsButton label="Fermer" outlined @click="dialogOpen = false" /><NsButton
        label="Confirmer"
        @click="dialogOpen = false" /></template
  ></NsDialog>
</template>

<style scoped>
.kit {
  display: grid;
  gap: 1.5rem;
}
.kit h2 {
  margin: 0 0 1.5rem;
}
.kit__row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}
.kit__fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.5rem;
}
.kit__label {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}
.kit__skeleton {
  margin-top: 1rem;
}
@media (max-width: 640px) {
  .kit__fields {
    grid-template-columns: 1fr;
  }
}
</style>
