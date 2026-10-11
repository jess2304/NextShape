<script setup lang="ts">
import { useProgressRecord } from "@/stores/progressRecordStore"
import { ACTIVITY_LEVELS, GENDER, GOALS } from "@/assets/js/constants"
import { computed } from "vue"
import { formatDate } from "@/assets/js/utils"
import NsBadge from "@/components/ui/NsBadge.vue"
import Accordion from "primevue/accordion"
import AccordionHeader from "primevue/accordionheader"
import AccordionPanel from "primevue/accordionpanel"
import AccordionContent from "primevue/accordioncontent"

// Store
const progressRecordStore = useProgressRecord()

const formattedGender = computed(() => {
  const rawDate = progressRecordStore.progressRecord.gender
  if (!rawDate) return "N/A"
  return rawDate == GENDER[0].value ? GENDER[0].label : GENDER[1].label
})

const fromattedActivity = computed(() => {
  return (
    ACTIVITY_LEVELS.find(
      (a) => a.value === progressRecordStore.progressRecord.activity_level
    )?.label || ""
  )
})

const formattedGoal = computed(() => {
  return (
    GOALS.find((g) => g.value === progressRecordStore.progressRecord.goal)
      ?.label || ""
  )
})

const bmr = computed(() => progressRecordStore.progressRecord.bmr || null)
const tdee = computed(() => progressRecordStore.progressRecord.tdee || null)
const calories = computed(
  () => progressRecordStore.progressRecord.calories_recommandees || null
)
</script>
<template>
  <section class="recap" aria-labelledby="recap-title">
    <div class="step-heading">
      <span>ÉTAPE 03</span>
      <h2 id="recap-title">Tout est prêt pour le calcul.</h2>
      <p>Vérifiez vos informations, puis calculez vos besoins caloriques.</p>
    </div>

    <div class="recap-information">
      <div class="information-heading">
        <h3>Vos informations</h3>
        <NsBadge>Récapitulatif</NsBadge>
      </div>
      <dl class="information-grid">
        <div>
          <dt>Genre</dt>
          <dd>{{ formattedGender }}</dd>
        </div>
        <div>
          <dt>Âge</dt>
          <dd>{{ progressRecordStore.progressRecord.age }} ans</dd>
        </div>
        <div>
          <dt>Taille</dt>
          <dd>{{ progressRecordStore.progressRecord.height_cm }} cm</dd>
        </div>
        <div>
          <dt>Poids</dt>
          <dd>{{ progressRecordStore.progressRecord.weight_kg }} kg</dd>
        </div>
        <div>
          <dt>Activité physique</dt>
          <dd>{{ fromattedActivity || "Non renseignée" }}</dd>
        </div>
        <div>
          <dt>Objectif</dt>
          <dd>{{ formattedGoal || "Non renseigné" }}</dd>
        </div>
      </dl>
    </div>

    <div class="results" aria-live="polite" aria-atomic="true">
      <div class="metric">
        <span class="metric-label">Au repos</span>
        <strong>{{ bmr ?? "—" }} <small v-if="bmr">kcal</small></strong>
        <span class="metric-caption">Métabolisme de base · BMR</span>
      </div>
      <div class="metric">
        <span class="metric-label">Avec votre activité</span>
        <strong>{{ tdee ?? "—" }} <small v-if="tdee">kcal</small></strong>
        <span class="metric-caption">Dépense quotidienne · TDEE</span>
      </div>
      <div class="metric metric-target">
        <span class="metric-label">Votre objectif</span>
        <strong
          >{{ calories ?? "—" }} <small v-if="calories">kcal</small></strong
        >
        <span class="metric-caption">Calories recommandées / jour</span>
      </div>
    </div>
    <p v-if="!calories" class="result-note">
      Vos résultats s'afficheront après le calcul.
    </p>
    <p v-else class="result-note">
      <template v-if="progressRecordStore.progressRecord.date"
        >Calcul du {{ formatDate(progressRecordStore.progressRecord.date) }} ·
      </template>
      Objectif : {{ formattedGoal }}.
    </p>

    <Accordion value="-1" class="formula-accordion">
      <AccordionPanel value="0">
        <AccordionHeader
          >Comment ces résultats sont-ils calculés ?</AccordionHeader
        >
        <AccordionContent>
          <div class="formula-details">
            <div>
              <h4>1. Votre métabolisme de base</h4>
              <p>
                Le BMR estime l'énergie dépensée au repos pour assurer les
                fonctions vitales du corps.
              </p>
              <p
                class="equation"
                v-if="progressRecordStore.progressRecord.gender === 'H'"
              >
                10 × poids (kg) + 6,25 × taille (cm) − 5 × âge + 5
              </p>
              <p class="equation" v-else>
                10 × poids (kg) + 6,25 × taille (cm) − 5 × âge − 161
              </p>
            </div>
            <div>
              <h4>2. Votre dépense quotidienne</h4>
              <p>Le TDEE tient compte de votre niveau d'activité physique.</p>
              <p class="equation">TDEE = BMR × facteur d'activité</p>
            </div>
            <div>
              <h4>3. L'ajustement selon votre objectif</h4>
              <p v-if="progressRecordStore.progressRecord.goal === 'perte'">
                Perte de poids : le calcul applique un déficit de 300 kcal.
              </p>
              <p
                v-else-if="progressRecordStore.progressRecord.goal === 'prise'"
              >
                Prise de masse : le calcul applique un surplus de 300 kcal.
              </p>
              <p v-else>Maintien : le calcul conserve la valeur du TDEE.</p>
              <p
                class="equation"
                v-if="progressRecordStore.progressRecord.goal === 'perte'"
              >
                Objectif = TDEE − 300 kcal
              </p>
              <p
                class="equation"
                v-else-if="progressRecordStore.progressRecord.goal === 'prise'"
              >
                Objectif = TDEE + 300 kcal
              </p>
              <p class="equation" v-else>Objectif = TDEE</p>
            </div>
          </div>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
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
.recap-information {
  border: 1px solid #e5e9e1;
  border-radius: 0.875rem;
  padding: 1.25rem;
}
.information-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}
.information-heading h3 {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
}
.information-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
  margin: 1.5rem 0 0;
}
.information-grid dt {
  font-size: 0.75rem;
  color: #69766f;
  margin-bottom: 0.4rem;
}
.information-grid dd {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
  overflow-wrap: anywhere;
}
.results {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 1.5rem;
}
.metric {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  background: #f5f6f1;
  border: 1px solid #e5e9e1;
  border-radius: 0.875rem;
  padding: 1.15rem;
}
.metric-label {
  color: #52685a;
  font-size: 0.75rem;
  font-weight: 600;
}
.metric > strong {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.05em;
  color: #1d4d40;
  margin: 0.8rem 0 0.5rem;
}
.metric small {
  font-size: 0.7rem;
  font-weight: 400;
  letter-spacing: 0;
}
.metric-caption {
  color: #69766f;
  font-size: 0.67rem;
  line-height: 1.5;
}
.metric-target {
  background: #1d4d40;
  border-color: #1d4d40;
}
.metric-target .metric-label,
.metric-target .metric-caption {
  color: #c7d8ce;
}
.metric-target > strong {
  color: #fff;
}
.result-note {
  color: #69766f;
  font-size: 0.75rem;
  line-height: 1.6;
  margin: 0.75rem 0 1.5rem;
}
.formula-accordion {
  font-size: 0.85rem;
}
.formula-details {
  display: grid;
  gap: 1.25rem;
  padding-top: 0.5rem;
}
.formula-details h4 {
  font-size: 0.875rem;
  margin: 0 0 0.5rem;
}
.formula-details p {
  font-size: 0.82rem;
  line-height: 1.7;
  color: #69766f;
  margin: 0;
}
.formula-details .equation {
  margin-top: 0.6rem;
  color: #1d4d40;
  background: #f3f6ef;
  padding: 0.7rem 0.875rem;
  border-radius: 0.5rem;
  font-variant-numeric: tabular-nums;
}
@media (max-width: 600px) {
  .information-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .results {
    grid-template-columns: 1fr;
  }
  .metric {
    display: grid;
    grid-template-columns: 1fr auto;
    column-gap: 0.5rem;
    align-items: center;
  }
  .metric > strong {
    grid-column: 2;
    grid-row: 1 / 3;
    margin: 0;
    font-size: 1.65rem;
  }
  .metric-caption {
    grid-column: 1;
    margin-top: 0.35rem;
  }
  .step-heading {
    margin-bottom: 1.5rem;
  }
}
</style>
