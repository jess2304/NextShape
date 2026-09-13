<script setup lang="ts">
import Splitter from "primevue/splitter"
import SplitterPanel from "primevue/splitterpanel"
import Button from "primevue/button"
import InputText from "primevue/inputtext"
import InputNumber from "primevue/inputnumber"
import Textarea from "primevue/textarea"
import Divider from "primevue/divider"
import MultiSelect from "primevue/multiselect"
import Tab from "primevue/tab"
import TabList from "primevue/tablist"
import TabPanel from "primevue/tabpanel"
import TabPanels from "primevue/tabpanels"
import Tabs from "primevue/tabs"
import { useToast } from "primevue/usetoast"
import { useCoachStore } from "@/stores/coachStore"
import { SUPPLEMENT_OPTIONS } from "@/assets/js/constants"
import { computed, onMounted } from "vue"
import { resolveApiErrorMessage, resolveApiMessage } from "@/assets/js/utils"

const coachStore = useCoachStore()
const toast = useToast()

const loadPreferences = async () => {
  try {
    return await coachStore.loadNutritionPreferences()
  } catch (err: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: resolveApiErrorMessage(
        err,
        "Impossible de charger les préférences nutritionnelles."
      ),
      life: 4000,
    })
  }
}

const savePreferences = async () => {
  try {
    const response = await coachStore.saveNutritionPreferences()
    toast.add({
      severity: "success",
      summary: "Sauvegarde",
      detail: resolveApiMessage(response, "Préférences mises à jour."),
      life: 3000,
    })
  } catch (err: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: resolveApiErrorMessage(
        err,
        "Impossible de sauvegarder les préférences."
      ),
      life: 4000,
    })
  }
}

const loadWeekPlan = async () => {
  try {
    return await coachStore.loadWeekPlan()
  } catch (err: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: resolveApiErrorMessage(
        err,
        "Impossible de charger le plan hebdo sauvegarde."
      ),
      life: 4000,
    })
  }
}

const buildWeekPlan = async () => {
  try {
    const response = await coachStore.buildWeekPlan()
    toast.add({
      severity: "success",
      summary: "Plan généré",
      detail: resolveApiMessage(response, "Programme nutritionnel généré."),
      life: 3000,
    })
  } catch (err: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: resolveApiErrorMessage(
        err,
        "Impossible de générer le plan hebdo."
      ),
      life: 4000,
    })
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
  <Tabs value="0">
    <TabList>
      <Tab value="0">Programme de nutrition</Tab>
      <Tab value="1">Suivi</Tab>
    </TabList>
    <TabPanels>
      <!-- TAB 1: Nutrition program -->
      <TabPanel value="0">
        <Splitter
          layout="horizontal"
          class="border-none"
          :gutterSize="0"
          :pt="{
            root: {
              style: {
                height: '100vh',
              },
            },
          }"
        >
          <SplitterPanel :size="24" class="p-3 overflow-auto">
            <h3 class="text-gray-700 font-semibold mb-3">
              Préférences nutritionnelles
            </h3>

            <div class="flex flex-column gap-2">
              <div>
                <label class="block mb-2">Allergies</label>
                <Textarea
                  v-model="coachStore.nutritionPreferences.allergies"
                  rows="2"
                  autoResize
                  class="w-full"
                />
              </div>

              <div>
                <label class="block mb-2">Régime</label>
                <InputText
                  v-model="coachStore.nutritionPreferences.diet_type"
                  class="w-full"
                  placeholder="Ex: halal, végétarien, ..."
                />
              </div>

              <div>
                <label class="block mb-2">Aliments non souhaités</label>
                <Textarea
                  v-model="coachStore.nutritionPreferences.disliked_foods"
                  rows="2"
                  autoResize
                  class="w-full"
                />
              </div>

              <div>
                <label class="block mb-2">Compléments autorisés</label>
                <MultiSelect
                  v-model="coachStore.nutritionPreferences.supplements"
                  :options="SUPPLEMENT_OPTIONS"
                  optionLabel="label"
                  optionValue="value"
                  display="chip"
                  filter
                  class="w-full"
                  placeholder="Sélectionnez les compléments à inclure dans votre régime"
                />
              </div>

              <div>
                <label class="block mb-2">Repas par jour</label>
                <InputNumber
                  v-model="coachStore.nutritionPreferences.meals_per_day"
                  :min="1"
                  :max="5"
                  :minFractionDigits="0"
                  :maxFractionDigits="0"
                  showButtons
                  class="w-full"
                  fluid
                />
              </div>

              <div class="flex gap-2">
                <Button
                  label="Enregistrer"
                  icon="pi pi-save"
                  class="w-full"
                  @click="savePreferences"
                />
                <Button
                  label="Actualiser"
                  icon="pi pi-refresh"
                  severity="secondary"
                  outlined
                  class="w-full"
                  @click="loadPreferences"
                />
              </div>

              <Divider />

              <Button
                label="Générer mon plan hebdo"
                icon="pi pi-calendar"
                severity="success"
                :loading="coachStore.isPlanLoading"
                class="w-full"
                @click="buildWeekPlan"
              />
            </div>
          </SplitterPanel>

          <SplitterPanel :size="33" class="p-3 overflow-auto">
            <h3 class="text-gray-700 font-semibold mb-3">Plan hebdomadaire</h3>

            <div v-if="!coachStore.weekPlan" class="text-gray-500 italic">
              Générez un plan nutritionnel pour l'afficher ici.
            </div>

            <div v-else class="flex flex-column gap-3">
              <div
                v-if="formattedWeekPlanUpdatedAt"
                class="text-sm text-gray-600"
              >
                Dernière mise à jour; le {{ formattedWeekPlanUpdatedAt }}
              </div>

              <div
                class="text-sm border-1 border-gray-200 border-round p-2 bg-white"
              >
                <strong>Cible:</strong>
                {{ coachStore.weekPlan.calories_target }} kcal,
                {{ coachStore.weekPlan.protein_g_target }} g protéines,
                {{ coachStore.weekPlan.carbs_g_target }} g glucides,
                {{ coachStore.weekPlan.fat_g_target }} g lipides.
              </div>

              <div
                v-for="day in coachStore.weekPlan.days"
                :key="day.day_index"
                class="border-1 border-gray-200 border-round p-2 bg-white"
              >
                <div class="font-semibold mb-2">Jour {{ day.day_index }}</div>
                <div
                  v-for="(meal, mealIndex) in day.meals"
                  :key="`${day.day_index}-${mealIndex}`"
                  class="mb-3"
                >
                  <div class="font-medium">{{ meal.title }}</div>
                  <ul class="pl-3 text-sm">
                    <li
                      v-for="(item, itemIndex) in meal.items"
                      :key="`${day.day_index}-${mealIndex}-${itemIndex}`"
                    >
                      {{ item.name }} - {{ item.portion }}
                      <span v-if="item.note">({{ item.note }})</span>
                    </li>
                  </ul>
                  <div class="text-xs text-gray-600">
                    {{ meal.approx_calories }} kcal | P
                    {{ meal.approx_protein_g }}g | G {{ meal.approx_carbs_g }}g
                    | L {{ meal.approx_fat_g }}g
                  </div>
                </div>
              </div>

              <div v-if="coachStore.weekPlan.notes?.length">
                <Divider />
                <div class="font-semibold mb-2">Notes du coach</div>
                <ul class="pl-3 text-sm">
                  <li
                    v-for="(note, index) in coachStore.weekPlan.notes"
                    :key="`note-${index}`"
                  >
                    {{ note }}
                  </li>
                </ul>
              </div>
            </div>
          </SplitterPanel>
        </Splitter>
      </TabPanel>
      <TabPanel value="1"> </TabPanel>
    </TabPanels>
  </Tabs>
</template>
