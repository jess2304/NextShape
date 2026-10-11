<script setup lang="ts">
import { computed, ref } from "vue"
import { useToast } from "primevue/usetoast"
import { useProgressRecord } from "@/stores/progressRecordStore"
import PageHeader from "@/components/layout/PageHeader.vue"
import NsBadge from "@/components/ui/NsBadge.vue"
import NsButton from "@/components/ui/NsButton.vue"
import NsCard from "@/components/ui/NsCard.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import NsNumberInput from "@/components/ui/NsNumberInput.vue"

const progressStore = useProgressRecord()
const toast = useToast()

const weight_kg = ref<number>()
const height_cm = ref<number>()
const imc = ref<number>()

const imcResult = computed(() => {
  if (!imc.value) return null
  if (imc.value < 18.5) return { label: "Maigreur", severity: "warn" }
  if (imc.value < 25)
    return { label: "Corpulence normale", severity: "success" }
  if (imc.value < 30) return { label: "Surpoids", severity: "warn" }
  return { label: "Obésité", severity: "danger" }
})

const calculateIMC = () => {
  try {
    imc.value = progressStore.calculateIMC(
      weight_kg.value || -1,
      height_cm.value || -1
    )
    toast.add({
      severity: "success",
      summary: "IMC calculé",
      detail: `Votre IMC est prêt`,
      life: 5000,
    })
  } catch (error: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail:
        error?.response?.data?.errors?.non_field_errors?.[0] ||
        error?.response?.data?.message ||
        "Échec de l'enregistrement de l'IMC",
      life: 5000,
    })
  }
}
</script>

<template>
  <div class="imc-page">
    <PageHeader
      eyebrow="LES CALCULATRICES"
      title="Un premier repère pour vous."
      description="Renseignez votre taille et votre poids pour calculer votre indice de masse corporelle."
    />

    <div class="imc-layout">
      <NsCard class="measurement-card">
        <div class="section-heading">
          <span class="section-icon" aria-hidden="true"
            ><i class="pi pi-calculator"
          /></span>
          <div>
            <h2>Calculer mon IMC</h2>
            <p>Deux mesures, un résultat immédiat.</p>
          </div>
        </div>
        <form class="measurements" @submit.prevent="calculateIMC">
          <NsFormField
            v-slot="{ describedby }"
            id="taille"
            label="Taille"
            hint="En centimètres"
          >
            <NsNumberInput
              v-model="height_cm"
              inputId="taille"
              :pt="{
                pcInputText: { root: { 'aria-describedby': describedby } },
              }"
              suffix=" cm"
              placeholder="Ex. 175"
              fluid
              :minFractionDigits="1"
              :maxFractionDigits="1"
            />
          </NsFormField>
          <NsFormField
            v-slot="{ describedby }"
            id="poids"
            label="Poids"
            hint="En kilogrammes"
          >
            <NsNumberInput
              v-model="weight_kg"
              inputId="poids"
              :pt="{
                pcInputText: { root: { 'aria-describedby': describedby } },
              }"
              suffix=" kg"
              placeholder="Ex. 70"
              fluid
              :minFractionDigits="1"
              :maxFractionDigits="1"
            />
          </NsFormField>
          <NsButton
            type="submit"
            label="Calculer mon IMC"
            icon="pi pi-arrow-right"
            iconPos="right"
            class="calculate-button"
          />
        </form>

        <div class="imc-result" aria-live="polite" aria-atomic="true">
          <template v-if="imcResult">
            <span class="result-label">VOTRE INDICE DE MASSE CORPORELLE</span>
            <div class="result-value">{{ imc }}</div>
            <NsBadge
              :tone="
                imcResult.severity === 'warn'
                  ? 'warning'
                  : imcResult.severity === 'danger'
                  ? 'danger'
                  : 'success'
              "
              >{{ imcResult.label }}</NsBadge
            >
            <p>Un indicateur à interpréter dans son contexte.</p>
          </template>
          <template v-else>
            <i class="pi pi-chart-bar empty-icon" aria-hidden="true" />
            <h3>Votre résultat apparaîtra ici</h3>
            <p>Complétez vos mesures puis lancez le calcul.</p>
          </template>
        </div>
      </NsCard>

      <div class="imc-explanation">
        <NsCard>
          <span class="section-eyebrow">COMPRENDRE LE RÉSULTAT</span>
          <h2>Un indice, pas toute l'histoire.</h2>
          <p>
            L'indice de masse corporelle met en relation votre poids et votre
            taille. Il donne un repère sur la corpulence.
          </p>
          <div class="formula">
            <span>La formule</span><strong>Poids (kg) ÷ taille² (m)</strong>
          </div>
          <p class="context-note">
            L'IMC ne tient pas compte de la masse musculaire, de la répartition
            des graisses ou de l'âge.
          </p>
        </NsCard>
        <NsCard>
          <h3>Les repères de l'IMC</h3>
          <dl class="imc-ranges">
            <div>
              <dt>Moins de 18,5</dt>
              <dd><NsBadge tone="warning">Maigreur</NsBadge></dd>
            </div>
            <div>
              <dt>De 18,5 à 24,9</dt>
              <dd><NsBadge tone="success">Corpulence normale</NsBadge></dd>
            </div>
            <div>
              <dt>De 25 à 29,9</dt>
              <dd><NsBadge tone="warning">Surpoids</NsBadge></dd>
            </div>
            <div>
              <dt>30 et plus</dt>
              <dd><NsBadge tone="danger">Obésité</NsBadge></dd>
            </div>
          </dl>
        </NsCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.imc-page {
  max-width: 1120px;
  margin-inline: auto;
}
.imc-layout {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 1.5rem;
  align-items: start;
}
.section-heading {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}
.section-icon {
  width: 3rem;
  height: 3rem;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 0.875rem;
  color: #1d4d40;
  background: #e7eee7;
  font-size: 1.2rem;
}
h2 {
  font-size: 1.25rem;
  letter-spacing: -0.03em;
  margin: 0 0 0.5rem;
}
h3 {
  font-size: 1rem;
  margin: 0 0 0.75rem;
}
p {
  color: #69766f;
  line-height: 1.7;
  margin: 0.5rem 0 0;
}
.section-heading p {
  font-size: 0.875rem;
  margin: 0;
}
.measurements {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
.calculate-button {
  grid-column: 1 / -1;
  margin-top: 0.25rem;
  width: 100%;
}
.imc-result {
  background: #edf2eb;
  border: 1px solid #dee7dc;
  border-radius: 1rem;
  padding: 2rem 1rem;
  margin-top: 1.75rem;
  text-align: center;
  min-height: 194px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.result-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #52665a;
}
.result-value {
  color: #1d4d40;
  font-size: 3.5rem;
  font-weight: 600;
  letter-spacing: -0.06em;
  line-height: 1.35;
  font-variant-numeric: tabular-nums;
}
.imc-result p {
  font-size: 0.8rem;
}
.imc-result h3 {
  margin: 0.75rem 0 0;
  font-size: 0.95rem;
}
.empty-icon {
  color: #738b77;
  font-size: 1.5rem;
}
.imc-explanation {
  display: grid;
  gap: 1.5rem;
}
.section-eyebrow {
  display: block;
  margin-bottom: 0.75rem;
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  color: #69766f;
  font-weight: 700;
}
.formula {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  border-left: 3px solid #a9bdab;
  padding: 0.75rem 1rem;
  margin: 1.5rem 0;
  background: #f6f7f3;
  border-radius: 0 0.5rem 0.5rem 0;
}
.formula span {
  color: #69766f;
  font-size: 0.75rem;
}
.formula strong {
  font-size: 1rem;
  color: #1d4d40;
}
.context-note {
  font-size: 0.8rem;
}
.imc-ranges {
  margin: 1rem 0 0;
}
.imc-ranges > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.875rem 0;
  border-bottom: 1px solid #edf0eb;
}
.imc-ranges > div:last-child {
  border: 0;
  padding-bottom: 0;
}
.imc-ranges dt {
  font-size: 0.85rem;
  color: #526058;
}
.imc-ranges dd {
  margin: 0;
  text-align: right;
}
@media (max-width: 800px) {
  .imc-layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 400px) {
  .measurements {
    grid-template-columns: 1fr;
  }
  .section-heading {
    align-items: flex-start;
    gap: 0.75rem;
  }
  .imc-ranges dt {
    font-size: 0.78rem;
  }
}
</style>
