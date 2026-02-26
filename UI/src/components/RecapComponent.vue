<script setup lang="ts">
import { useProgressRecord } from "@/stores/progressRecordStore"
import { ACTIVITY_LEVELS, GENDER, GOALS } from "@/assets/js/constants"
import { computed } from "vue"
import { formatDate } from "@/assets/js/utils"
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
  <div class="fadein animation-duration-800">
    <h2 class="text-5xl text-center text-primary mb-6">
      Récapitulatif & Calcul
    </h2>

    <!-- Information section -->
    <div class="card shadow-2 p-4 mb-5 border-round">
      <h3 class="text-2xl font-semibold text-surface-700 mb-3">
        Vos informations
      </h3>
      <div class="grid">
        <div class="col-12 md:col-6">
          Sexe : <b>{{ formattedGender }}</b>
        </div>
        <div class="col-12 md:col-6">
          Âge : <b>{{ progressRecordStore.progressRecord.age }} ans</b>
        </div>
        <div class="col-12 md:col-6">
          Taille : <b>{{ progressRecordStore.progressRecord.height_cm }} cm</b>
        </div>
        <div class="col-12 md:col-6">
          Poids : <b>{{ progressRecordStore.progressRecord.weight_kg }} kg</b>
        </div>
        <div class="col-12 md:col-6">
          Activité : <b>{{ fromattedActivity }}</b>
        </div>
        <div class="col-12 md:col-6">
          Objectif : <b>{{ formattedGoal }}</b>
        </div>
      </div>
    </div>
    <div class="card shadow-1 bg-surface-100 p-4 mb-5 border-round">
      <h3 class="text-xl font-semibold text-surface-700 mb-4">
        Formules utilisées & définitions
      </h3>

      <div class="grid">
        <div class="col-12 md:col-6">
          <p class="font-mono text-sm mb-3">
            <strong>BMR :</strong><br />
            <span v-if="progressRecordStore.progressRecord.gender === 'H'">
              BMR = 10 × poids(kg) + 6.25 × taille(cm) – 5 × âge + 5
            </span>
            <span v-else>
              BMR = 10 × poids(kg) + 6.25 × taille(cm) – 5 × âge – 161
            </span>
          </p>

          <p class="font-mono text-sm mb-3">
            <strong>TDEE :</strong><br />
            TDEE = BMR × facteur d'activité
          </p>

          <p class="font-mono text-sm">
            <strong>Calories recommandées :</strong><br />
            Idéalement, créez un écart calorique
            <span class="font-semibold">entre 200 et 300 kcal</span> par rapport
            à votre TDEE.
            <br />
            Un écart trop petit (<200 kcal) → pas de résultats visibles. Un
            écart trop grand (>400–500 kcal) → résultats rapides mais rarement
            durables.
            <br /><br />

            <span v-if="progressRecordStore.progressRecord.goal === 'perte'">
              🔽 <strong>Objectif : Perte de poids</strong> →
              <span class="text-blue-600">TDEE – 300 kcal</span> (déficit
              modéré)
            </span>

            <span
              v-else-if="progressRecordStore.progressRecord.goal === 'prise'"
            >
              🔼 <strong>Objectif : Prise de masse</strong> →
              <span class="text-green-600">TDEE + 300 kcal</span> (surplus
              contrôlé)
            </span>

            <span v-else>
              ⚖️ <strong>Objectif : Maintien</strong> →
              <span class="text-orange-600">TDEE</span> (équilibre)
            </span>
          </p>
          <Accordion value="-1">
            <AccordionPanel value="0">
              <AccordionHeader
                >effets négatifs si l’écart est mal calibré</AccordionHeader
              >
              <AccordionContent>
                <div class="space-y-4 text-sm">
                  <div>
                    <strong>💡 Perte de poids (déficit trop grand)</strong>
                    <ul class="list-disc ml-6 mt-1 text-gray-700">
                      <li>
                        Ralentissement du métabolisme (mode “économie
                        d’énergie”)
                      </li>
                      <li>Perte musculaire si protéines insuffisantes</li>
                      <li>Baisse d’énergie et performance</li>
                      <li>
                        Fringales et compulsions → craquage assuré après 1–2
                        semaines
                      </li>
                      <li>
                        Effet yo-yo : reprise rapide du poids perdu, voire plus
                      </li>
                    </ul>
                  </div>
                  <div>
                    <strong>💡 Prise de masse (surplus trop grand)</strong>
                    <ul class="list-disc ml-6 mt-1 text-gray-700">
                      <li>Prise de gras excessive</li>
                      <li>Problèmes digestifs (ballonnements, inconfort)</li>
                      <li>Baisse de sensibilité à l’insuline</li>
                      <li>
                        “Marathon de bouffe” → tu tiens 1–2 semaines, puis tu
                        craques, et retour en arrière
                      </li>
                    </ul>
                  </div>
                </div>
              </AccordionContent>
            </AccordionPanel>
          </Accordion>
        </div>
        <div class="col-12 md:col-6 text-sm leading-relaxed">
          <p class="mb-3">
            <strong>BMR (Basal Metabolic Rate)</strong> : c'est le nombre de
            calories que votre corps dépense au repos complet, pour assurer ses
            fonctions vitales (respiration, circulation, température...).
          </p>
          <p class="mb-3">
            <strong>TDEE (Total Daily Energy Expenditure)</strong> : c'est le
            total des calories brûlées dans une journée complète, en tenant
            compte de votre activité physique. Il est obtenu en multipliant le
            BMR par un facteur lié à votre niveau d'activité.
          </p>
          <p>
            <strong>Calories recommandées</strong> : selon votre objectif, vous
            devez viser un
            <span class="text-primary font-medium">déficit</span> (perte de
            poids), un <span class="text-primary font-medium">maintien</span> ou
            un <span class="text-primary font-medium">excédent</span> (prise de
            masse) calorique.
          </p>
        </div>
      </div>
    </div>
    <div class="grid mb-6">
      <div class="col-12 md:col-4">
        <div
          class="shadow-2 p-4 text-center border-left-4 border-primary bg-surface-50 rounded"
        >
          <h4 class="text-xl mb-1">BMR</h4>
          <div class="text-2xl font-bold text-primary">
            {{ bmr }} <span v-if="bmr">kcal</span> <span v-else>-</span>
          </div>
        </div>
      </div>
      <div class="col-12 md:col-4">
        <div
          class="shadow-2 p-4 text-center border-left-4 border-primary bg-surface-50 rounded"
        >
          <h4 class="text-xl mb-1">TDEE</h4>
          <div class="text-2xl font-bold text-primary">
            {{ tdee }} <span v-if="tdee">kcal</span><span v-else>-</span>
          </div>
        </div>
      </div>
      <div class="col-12 md:col-4">
        <div
          class="shadow-2 p-4 text-center border-left-4 border-primary bg-surface-50 rounded"
        >
          <h4 class="text-xl mb-1">Objectif</h4>
          <div class="text-2xl font-bold text-primary">
            {{ calories }} <span v-if="calories">kcal</span
            ><span v-else>-</span>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="calories"
      class="text-center text-lg text-surface-700 mt-4 mb-6 italic"
    >
      À la date du
      <span
        v-if="progressRecordStore.progressRecord.date"
        class="font-semibold"
      >
        {{ formatDate(progressRecordStore.progressRecord.date) }}
      </span>
      , pour <b>{{ formattedGoal }}</b
      >, vous devriez consommer environ
      <span class="text-primary font-bold text-2xl">{{ calories }} kcal</span>
      par jour.
    </div>
  </div>
</template>

<style scoped>
.fadein {
  animation: fadein 0.4s ease;
}
@keyframes fadein {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
