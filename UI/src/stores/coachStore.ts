import { NutritionPreferences, NutritionWeekPlan } from "@/assets/js/interfaces"
import { defineStore } from "pinia"
import {
  generateWeekNutritionPlan,
  getNutritionPreferences,
  updateNutritionPreferences,
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
    isPlanLoading: false,
  }),

  actions: {
    async loadNutritionPreferences() {
      const response = await getNutritionPreferences()
      this.nutritionPreferences = {
        allergies: response.data.allergies || "",
        diet_type: response.data.diet_type || "",
        disliked_foods: response.data.disliked_foods || "",
        supplements: Array.isArray(response.data.supplements)
          ? response.data.supplements
          : [],
        meals_per_day: response.data.meals_per_day || 3,
      }
      return response
    },

    async saveNutritionPreferences() {
      const response = await updateNutritionPreferences(
        this.nutritionPreferences
      )
      this.nutritionPreferences = {
        allergies: response.data.allergies || "",
        diet_type: response.data.diet_type || "",
        disliked_foods: response.data.disliked_foods || "",
        supplements: Array.isArray(response.data.supplements)
          ? response.data.supplements
          : [],
        meals_per_day: response.data.meals_per_day || 3,
      }
      return response
    },

    async buildWeekPlan() {
      this.isPlanLoading = true
      try {
        const response = await generateWeekNutritionPlan()
        this.weekPlan = response.data
        return response
      } finally {
        this.isPlanLoading = false
      }
    },
  },
  persist: true,
})
