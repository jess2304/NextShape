<script setup lang="ts">
import { isCancel } from "axios"
import NsButton from "@/components/ui/NsButton.vue"
import NsInput from "@/components/ui/NsInput.vue"
import NsNumberInput from "@/components/ui/NsNumberInput.vue"
import NsTextarea from "@/components/ui/NsTextarea.vue"
import NsMultiSelect from "@/components/ui/NsMultiSelect.vue"
import NsFormField from "@/components/ui/NsFormField.vue"
import NsCard from "@/components/ui/NsCard.vue"
import NsBadge from "@/components/ui/NsBadge.vue"
import NsEmptyState from "@/components/ui/NsEmptyState.vue"
import NsSkeleton from "@/components/ui/NsSkeleton.vue"
import PageHeader from "@/components/layout/PageHeader.vue"
import Tab from "primevue/tab"
import TabList from "primevue/tablist"
import TabPanel from "primevue/tabpanel"
import TabPanels from "primevue/tabpanels"
import Tabs from "primevue/tabs"
import { useToast } from "primevue/usetoast"
import { useCoachStore } from "@/stores/coachStore"
import { SUPPLEMENT_OPTIONS } from "@/assets/js/constants"
import { computed, onMounted, ref } from "vue"
import { resolveApiErrorMessage, resolveApiMessage } from "@/assets/js/utils"

const coachStore = useCoachStore()
const toast = useToast()
const isPreferencesLoading = ref(false)
const isSavingPreferences = ref(false)
const isGenerating = ref(false)
const preferencesError = ref("")
const planError = ref("")

const loadPreferences = async () => {
  isPreferencesLoading.value = true
  preferencesError.value = ""
  try {
    return await coachStore.loadNutritionPreferences()
  } catch (err: any) {
    if (isCancel(err)) return
    preferencesError.value = resolveApiErrorMessage(
      err,
      "Impossible de charger les préférences nutritionnelles."
    )
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: preferencesError.value,
      life: 4000,
    })
  } finally {
    isPreferencesLoading.value = false
  }
}

const savePreferences = async () => {
  isSavingPreferences.value = true
  try {
    const response = await coachStore.saveNutritionPreferences()
    toast.add({
      severity: "success",
      summary: "Sauvegarde",
      detail: resolveApiMessage(response, "Préférences mises à jour."),
      life: 3000,
    })
  } catch (err: any) {
    if (isCancel(err)) return
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: resolveApiErrorMessage(
        err,
        "Impossible de sauvegarder les préférences."
      ),
      life: 4000,
    })
  } finally {
    isSavingPreferences.value = false
  }
}

const loadWeekPlan = async () => {
  planError.value = ""
  try {
    return await coachStore.loadWeekPlan()
  } catch (err: any) {
    if (isCancel(err)) return
    planError.value = resolveApiErrorMessage(
      err,
      "Impossible de charger votre programme enregistré."
    )
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: planError.value,
      life: 4000,
    })
  }
}

const buildWeekPlan = async () => {
  isGenerating.value = true
  planError.value = ""
  try {
    const response = await coachStore.buildWeekPlan()
    toast.add({
      severity: "success",
      summary: "Plan généré",
      detail: resolveApiMessage(response, "Programme nutritionnel généré."),
      life: 3000,
    })
  } catch (err: any) {
    if (isCancel(err)) return
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: resolveApiErrorMessage(
        err,
        "Impossible de générer le plan hebdo."
      ),
      life: 4000,
    })
  } finally {
    isGenerating.value = false
  }
}

const formattedWeekPlanUpdatedAt = computed(() => {
  if (!coachStore.weekPlanUpdatedAt) {
    return null
  }
  const parsed = new Date(coachStore.weekPlanUpdatedAt)
  if (Number.isNaN(parsed.getTime())) {
    return coachStore.weekPlanUpdatedAt
  }
  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "long",
    timeStyle: "short",
  }).format(parsed)
})

onMounted(async () => {
  await Promise.all([loadPreferences(), loadWeekPlan()])
})
</script>

<template>
  <div class="nutrition-page">
    <PageHeader
      eyebrow="Votre alimentation"
      title="Un programme qui vous ressemble"
      description="Renseignez vos préférences et retrouvez votre programme nutritionnel de la semaine."
    />
    <Tabs value="0" class="nutrition-tabs">
      <TabList
        ><Tab value="0">Programme nutritionnel</Tab
        ><Tab value="1">Suivi</Tab></TabList
      >
      <TabPanels>
        <TabPanel value="0">
          <div class="nutrition-workspace">
            <aside
              class="nutrition-preferences"
              aria-label="Préférences nutritionnelles"
            >
              <NsCard>
                <div class="preferences-heading">
                  <span class="preferences-icon"
                    ><i class="pi pi-sliders-h" aria-hidden="true"
                  /></span>
                  <div>
                    <h2>Vos préférences</h2>
                    <p>Les détails qui font la différence.</p>
                  </div>
                </div>
                <p
                  v-if="preferencesError"
                  class="preferences-error"
                  role="alert"
                >
                  {{ preferencesError }}
                </p>
                <form
                  class="preferences-form"
                  @submit.prevent="savePreferences"
                >
                  <fieldset
                    :disabled="isPreferencesLoading || isSavingPreferences"
                    class="preferences-fields"
                    :aria-busy="isPreferencesLoading"
                  >
                    <NsFormField id="nutrition-allergies" label="Allergies">
                      <NsTextarea
                        id="nutrition-allergies"
                        v-model="coachStore.nutritionPreferences.allergies"
                        :rows="2"
                        autoResize
                        placeholder="Indiquez vos allergies alimentaires"
                        fluid
                      />
                    </NsFormField>
                    <NsFormField id="nutrition-diet" label="Régime alimentaire">
                      <NsInput
                        id="nutrition-diet"
                        v-model="coachStore.nutritionPreferences.diet_type"
                        placeholder="Ex. : végétarien, halal…"
                        fluid
                      />
                    </NsFormField>
                    <NsFormField
                      id="nutrition-dislikes"
                      label="Aliments non souhaités"
                    >
                      <NsTextarea
                        id="nutrition-dislikes"
                        v-model="coachStore.nutritionPreferences.disliked_foods"
                        :rows="2"
                        autoResize
                        placeholder="Les aliments que vous préférez éviter"
                        fluid
                      />
                    </NsFormField>
                    <NsFormField
                      id="nutrition-supplements"
                      label="Compléments autorisés"
                      hint="Uniquement ceux que vous souhaitez inclure."
                      v-slot="{ describedby }"
                    >
                      <NsMultiSelect
                        inputId="nutrition-supplements"
                        :aria-describedby="describedby"
                        v-model="coachStore.nutritionPreferences.supplements"
                        :options="SUPPLEMENT_OPTIONS"
                        optionLabel="label"
                        optionValue="value"
                        display="chip"
                        filter
                        placeholder="Sélectionner des compléments"
                        fluid
                        :maxSelectedLabels="2"
                        selectedItemsLabel="{0} compléments sélectionnés"
                      />
                    </NsFormField>
                    <NsFormField id="nutrition-meals" label="Repas par jour">
                      <NsNumberInput
                        inputId="nutrition-meals"
                        v-model="coachStore.nutritionPreferences.meals_per_day"
                        :min="1"
                        :max="5"
                        :minFractionDigits="0"
                        :maxFractionDigits="0"
                        showButtons
                        fluid
                      />
                    </NsFormField>
                  </fieldset>
                  <div class="preferences-actions">
                    <NsButton
                      type="submit"
                      label="Enregistrer"
                      icon="pi pi-check"
                      :loading="isSavingPreferences"
                      :disabled="isPreferencesLoading || isSavingPreferences"
                    />
                    <NsButton
                      label="Actualiser"
                      icon="pi pi-refresh"
                      severity="secondary"
                      outlined
                      :loading="isPreferencesLoading"
                      :disabled="isPreferencesLoading || isSavingPreferences"
                      @click="loadPreferences"
                    />
                  </div>
                </form>
                <div class="preferences-generate">
                  <p>
                    Enregistrez vos préférences avant de générer votre
                    programme.
                  </p>
                  <NsButton
                    label="Générer mon programme"
                    icon="pi pi-sparkles"
                    :loading="coachStore.isPlanLoading"
                    :disabled="coachStore.isPlanLoading"
                    @click="buildWeekPlan"
                  />
                </div>
              </NsCard>
            </aside>

            <section
              class="nutrition-plan"
              aria-label="Programme hebdomadaire"
              :aria-busy="coachStore.isPlanLoading"
            >
              <div class="plan-heading">
                <div>
                  <h2>Votre semaine, à table.</h2>
                  <p v-if="formattedWeekPlanUpdatedAt">
                    Mis à jour le {{ formattedWeekPlanUpdatedAt }}
                  </p>
                  <p v-else>Vos repas et vos repères nutritionnels.</p>
                </div>
                <NsBadge v-if="coachStore.weekPlan" tone="success"
                  >{{ coachStore.weekPlan.days.length }} jour{{
                    coachStore.weekPlan.days.length > 1 ? "s" : ""
                  }}</NsBadge
                >
              </div>

              <NsCard v-if="coachStore.isPlanLoading" class="plan-loading">
                <div class="plan-loading-label" role="status">
                  <i class="pi pi-spin pi-spinner" aria-hidden="true" /><span>{{
                    isGenerating
                      ? "Création de votre programme en cours…"
                      : "Chargement de votre programme…"
                  }}</span>
                </div>
                <p v-if="isGenerating">
                  Cela peut prendre un moment. Votre programme s’affichera ici
                  dès qu’il sera prêt.
                </p>
                <div class="plan-loading-lines">
                  <NsSkeleton height="5rem" /><NsSkeleton
                    height="2rem"
                    width="65%"
                  /><NsSkeleton height="7rem" />
                </div>
              </NsCard>
              <NsCard v-else-if="planError">
                <NsEmptyState
                  icon="pi pi-exclamation-circle"
                  title="Programme indisponible"
                  :description="planError"
                  ><NsButton
                    label="Réessayer"
                    icon="pi pi-refresh"
                    outlined
                    @click="loadWeekPlan"
                /></NsEmptyState>
              </NsCard>
              <NsCard v-else-if="!coachStore.weekPlan" class="plan-empty">
                <NsEmptyState
                  icon="pi pi-calendar"
                  title="Votre prochaine semaine commence ici"
                  description="Renseignez et enregistrez vos préférences, puis générez votre programme pour retrouver tous vos repas dans cet espace."
                />
              </NsCard>
              <template v-else>
                <NsCard class="plan-targets">
                  <div class="targets-heading">
                    <span>Objectifs quotidiens</span
                    ><span
                      >{{ coachStore.weekPlan.meals_per_day }} repas /
                      jour</span
                    >
                  </div>
                  <dl class="targets-grid">
                    <div>
                      <dt>Calories</dt>
                      <dd>
                        {{ coachStore.weekPlan.calories_target }}
                        <small>kcal</small>
                      </dd>
                    </div>
                    <div>
                      <dt>Protéines</dt>
                      <dd>
                        {{ coachStore.weekPlan.protein_g_target }}
                        <small>g</small>
                      </dd>
                    </div>
                    <div>
                      <dt>Glucides</dt>
                      <dd>
                        {{ coachStore.weekPlan.carbs_g_target }}
                        <small>g</small>
                      </dd>
                    </div>
                    <div>
                      <dt>Lipides</dt>
                      <dd>
                        {{ coachStore.weekPlan.fat_g_target }} <small>g</small>
                      </dd>
                    </div>
                  </dl>
                </NsCard>
                <NsCard
                  v-for="day in coachStore.weekPlan.days"
                  :key="day.day_index"
                  class="plan-day"
                >
                  <div class="day-heading">
                    <h3>
                      <span class="day-number">{{
                        String(day.day_index).padStart(2, "0")
                      }}</span
                      >Jour {{ day.day_index }}
                    </h3>
                    <span>{{ day.meals.length }} repas</span>
                  </div>
                  <div class="day-meals">
                    <article
                      v-for="(meal, mealIndex) in day.meals"
                      :key="`${day.day_index}-${mealIndex}`"
                      class="plan-meal"
                    >
                      <h4>{{ meal.title }}</h4>
                      <ul class="meal-items">
                        <li
                          v-for="(item, itemIndex) in meal.items"
                          :key="`${day.day_index}-${mealIndex}-${itemIndex}`"
                        >
                          <span
                            >{{ item.name }}
                            <span class="item-portion"
                              >· {{ item.portion }}</span
                            ></span
                          ><small v-if="item.note">{{ item.note }}</small>
                        </li>
                      </ul>
                      <dl class="meal-macros">
                        <div>
                          <dt>Calories</dt>
                          <dd>{{ meal.approx_calories }} kcal</dd>
                        </div>
                        <div>
                          <dt>Protéines</dt>
                          <dd>{{ meal.approx_protein_g }} g</dd>
                        </div>
                        <div>
                          <dt>Glucides</dt>
                          <dd>{{ meal.approx_carbs_g }} g</dd>
                        </div>
                        <div>
                          <dt>Lipides</dt>
                          <dd>{{ meal.approx_fat_g }} g</dd>
                        </div>
                      </dl>
                    </article>
                  </div>
                </NsCard>
                <NsCard
                  v-if="coachStore.weekPlan.notes?.length"
                  class="plan-notes"
                  ><h3>
                    <i class="pi pi-file-edit" aria-hidden="true" />Notes du
                    coach
                  </h3>
                  <ul>
                    <li
                      v-for="(note, index) in coachStore.weekPlan.notes"
                      :key="`note-${index}`"
                    >
                      {{ note }}
                    </li>
                  </ul></NsCard
                >
              </template>
            </section>
          </div>
        </TabPanel>
        <TabPanel value="1">
          <NsCard class="tracking-empty"
            ><NsEmptyState
              icon="pi pi-chart-line"
              title="Votre suivi se construit"
              description="Le suivi détaillé n’est pas encore disponible. Vos calculs enregistrés restent consultables dans l’historique."
              ><RouterLink to="/historique" class="tracking-history-link"
                >Consulter mon historique
                <i
                  class="pi pi-arrow-right"
                  aria-hidden="true" /></RouterLink></NsEmptyState
          ></NsCard>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<style scoped>
.nutrition-page {
  display: grid;
  gap: 1.75rem;
  min-width: 0;
}
.nutrition-tabs {
  min-width: 0;
}
.nutrition-tabs :deep(.p-tabpanels) {
  padding: 1.5rem 0 0;
  background: transparent;
}
.nutrition-tabs :deep(.p-tablist-tab-list) {
  background: transparent;
}
.nutrition-workspace {
  display: grid;
  grid-template-columns: minmax(17rem, 21rem) minmax(0, 1fr);
  align-items: start;
  gap: 1.5rem;
}
.nutrition-preferences,
.nutrition-plan {
  min-width: 0;
}
.preferences-heading {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  margin-bottom: 1.5rem;
}
.preferences-heading h2,
.plan-heading h2 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--ns-ink);
  letter-spacing: -0.025em;
}
.preferences-heading p,
.plan-heading p {
  margin: 0.35rem 0 0;
  color: var(--ns-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}
.preferences-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.7rem;
  display: grid;
  place-items: center;
  background: var(--ns-sage);
  color: var(--ns-primary);
  flex: 0 0 auto;
}
.preferences-fields {
  margin: 0;
  padding: 0;
  border: 0;
  display: grid;
  gap: 1.1rem;
  min-width: 0;
}
.preferences-fields:disabled {
  opacity: 0.65;
}
.preferences-actions {
  display: flex;
  gap: 0.65rem;
  margin-top: 1.25rem;
  flex-wrap: wrap;
}
.preferences-actions > * {
  flex: 1;
}
.preferences-generate {
  margin-top: 1.4rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--ns-border);
}
.preferences-generate p {
  font-size: 0.75rem;
  line-height: 1.6;
  color: var(--ns-muted);
  margin: 0 0 0.85rem;
}
.preferences-generate :deep(button) {
  width: 100%;
}
.preferences-error {
  font-size: 0.8rem;
  color: #a54332;
  background: #fff0eb;
  padding: 0.75rem;
  border-radius: 0.5rem;
  line-height: 1.5;
}
.nutrition-plan {
  display: grid;
  gap: 1.25rem;
}
.plan-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 3rem;
}
.plan-empty {
  min-height: 20rem;
  display: grid;
  align-items: center;
}
.plan-loading-label {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ns-primary);
}
.plan-loading p {
  font-size: 0.8rem;
  line-height: 1.6;
  color: var(--ns-muted);
}
.plan-loading-lines {
  display: grid;
  gap: 1rem;
  margin-top: 1.5rem;
}
.plan-targets {
  background: var(--ns-sage);
  border-color: #d4e0d6;
}
.targets-heading {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  color: var(--ns-primary);
  font-size: 0.8rem;
}
.targets-heading > span:first-child {
  font-weight: 600;
}
.targets-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  margin: 1.3rem 0 0;
}
.targets-grid dt {
  color: #53695c;
  font-size: 0.75rem;
}
.targets-grid dd {
  margin: 0.3rem 0 0;
  font-weight: 600;
  font-size: 1.35rem;
  color: var(--ns-primary);
  font-variant-numeric: tabular-nums;
}
.targets-grid small {
  font-size: 0.7rem;
  font-weight: 400;
}
.day-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1.1rem;
  border-bottom: 1px solid var(--ns-border);
}
.day-heading h3 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1rem;
}
.day-heading > span {
  font-size: 0.75rem;
  color: var(--ns-muted);
}
.day-number {
  display: grid;
  place-items: center;
  height: 2rem;
  width: 2rem;
  background: var(--ns-bg);
  border-radius: 0.5rem;
  font-size: 0.75rem;
  color: var(--ns-primary);
  font-variant-numeric: tabular-nums;
}
.day-meals {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.5rem;
  padding-top: 1.25rem;
}
.plan-meal {
  min-width: 0;
}
.plan-meal h4 {
  font-size: 0.9rem;
  margin: 0 0 0.8rem;
  color: var(--ns-ink);
}
.meal-items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.65rem;
  font-size: 0.8rem;
  line-height: 1.5;
}
.meal-items li {
  display: grid;
  gap: 0.15rem;
  overflow-wrap: anywhere;
}
.item-portion,
.meal-items small {
  color: var(--ns-muted);
}
.meal-items small {
  font-size: 0.73rem;
}
.meal-macros {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  background: var(--ns-bg);
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin: 1rem 0 0;
}
.meal-macros dt {
  font-size: 0.65rem;
  color: var(--ns-muted);
}
.meal-macros dd {
  margin: 0.1rem 0 0;
  font-size: 0.75rem;
  font-variant-numeric: tabular-nums;
}
.plan-notes h3 {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.9rem;
  margin: 0;
  color: var(--ns-primary);
}
.plan-notes ul {
  margin: 0.9rem 0 0;
  padding-left: 1rem;
  font-size: 0.8rem;
  line-height: 1.7;
  color: #53695c;
}
.plan-notes li + li {
  margin-top: 0.5rem;
}
.tracking-empty {
  min-height: 20rem;
  display: grid;
  align-items: center;
}
.tracking-history-link {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  color: var(--ns-primary);
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
}
.tracking-history-link:hover {
  text-decoration: underline;
}
.tracking-history-link:focus-visible {
  outline: 3px solid #91b5a5;
  outline-offset: 4px;
}
@media (max-width: 1200px) {
  .nutrition-workspace {
    grid-template-columns: minmax(16rem, 19rem) minmax(0, 1fr);
    gap: 1rem;
  }
  .day-meals {
    grid-template-columns: minmax(0, 1fr);
  }
  .targets-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 900px) {
  .nutrition-workspace {
    grid-template-columns: minmax(0, 1fr);
  }
  .preferences-fields {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.25rem;
  }
  .preferences-heading {
    margin-bottom: 1.25rem;
  }
  .preferences-actions {
    justify-content: flex-end;
  }
  .preferences-actions > * {
    flex: 0 1 auto;
  }
  .preferences-generate :deep(button) {
    width: auto;
  }
  .day-meals {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .targets-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
@media (max-width: 600px) {
  .preferences-fields,
  .day-meals {
    grid-template-columns: minmax(0, 1fr);
  }
  .preferences-actions > * {
    flex: 1;
  }
  .preferences-generate :deep(button) {
    width: 100%;
  }
  .targets-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .nutrition-tabs :deep(.p-tab) {
    padding-inline: 0.75rem;
    font-size: 0.8rem;
  }
  .plan-heading {
    align-items: flex-start;
  }
}
</style>
