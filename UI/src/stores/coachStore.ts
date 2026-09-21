import { CanceledError } from "axios"
import { NutritionPreferences, NutritionWeekPlan } from "@/assets/js/interfaces"
import { defineStore } from "pinia"
import {
  generateWeekNutritionPlan,
  getWeekNutritionPlan,
  getNutritionPreferences,
  updateNutritionPreferences,
  runSessionRequest,
} from "@/services/apiService"

export const useCoachStore = defineStore("coach", {
  state: () => ({
    nutritionPreferences: {
      allergies: "",
      diet_type: "",
      disliked_foods: "",
      supplements: [] as string[],
      meals_per_day: 3,
    } as NutritionPreferences,
    weekPlan: null as NutritionWeekPlan | null,
    weekPlanUpdatedAt: null as string | null,
    isPlanLoading: false,
  }),

  actions: {
    loadNutritionPreferences() {
      return runSessionRequest(
        () => getNutritionPreferences(),
        (response) => {
          this.nutritionPreferences = {
            allergies: response.data.allergies || "",
            diet_type: response.data.diet_type || "",
            disliked_foods: response.data.disliked_foods || "",
            supplements: Array.isArray(response.data.supplements)
              ? response.data.supplements
              : [],
            meals_per_day: response.data.meals_per_day || 3,
          }
        }
      )
    },

    saveNutritionPreferences() {
      return runSessionRequest(
        () => updateNutritionPreferences(this.nutritionPreferences),
        (response) => {
          this.nutritionPreferences = {
            allergies: response.data.allergies || "",
            diet_type: response.data.diet_type || "",
            disliked_foods: response.data.disliked_foods || "",
            supplements: Array.isArray(response.data.supplements)
              ? response.data.supplements
              : [],
            meals_per_day: response.data.meals_per_day || 3,
          }
        }
      )
    },

    buildWeekPlan() {
      if (this.isPlanLoading) {
        return Promise.reject(new CanceledError("Chargement en cours"))
      }
      this.isPlanLoading = true
      return runSessionRequest(
        () => generateWeekNutritionPlan(),
        (response) => {
          this.weekPlan = response.data.plan
          this.weekPlanUpdatedAt = response.data.updated_at
        },
        () => {
          this.isPlanLoading = false
        }
      )
    },

    loadWeekPlan() {
      if (this.isPlanLoading) {
        return Promise.reject(new CanceledError("Chargement en cours"))
      }
      this.isPlanLoading = true
      return runSessionRequest(
        () => getWeekNutritionPlan(),
        (response) => {
          this.weekPlan = response.data.plan
          this.weekPlanUpdatedAt = response.data.updated_at
        },
        () => {
          this.isPlanLoading = false
        }
      )
    },
  },
})
