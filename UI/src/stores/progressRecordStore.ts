import { defineStore } from "pinia"
import { calculateCalories } from "@/services/apiService"
import { useAuthStore } from "@/stores/authStore"
import { getAgeFromBirthDate } from "@/assets/js/utils"
import { ProgressRecord } from "@/assets/js/interfaces"

export const useProgressRecord = defineStore("progressRecord", {
  state: () => ({
    progressRecord: {
      user: useAuthStore().user,
      gender: useAuthStore().user?.gender ?? null,
      age: getAgeFromBirthDate(useAuthStore().user?.birth_date),
      date: new Date().toString(),
      weight_kg: null,
      height_cm: null,
      imc: null,
      activity_level: null,
      goal: null,
      bmr: null,
      tdee: null,
      calories_recommandees: null,
      created_at: null,
      modified_at: null,
    } as ProgressRecord,
  }),
  actions: {
    calculateIMC(weight_kg: number, height_cm: number) {
      if (weight_kg <= 0) {
        throw new Error("Le poids doit être supérieur à 0.")
      }
      if (height_cm <= 0) {
        throw new Error("La taille doit être supérieure à 0.")
      }

      const height_m = height_cm / 100
      const imc = weight_kg / (height_m * height_m)
      return Math.round(imc * 100) / 100
    },
    async calculateCalories() {
      try {
        const payload = {
          gender: this.progressRecord.gender,
          age: this.progressRecord.age,
          date: this.progressRecord.date,
          weight_kg: this.progressRecord.weight_kg,
          height_cm: this.progressRecord.height_cm,
          activity_level: this.progressRecord.activity_level,
          goal: this.progressRecord.goal,
        }
        const result = await calculateCalories(payload)

        this.progressRecord.bmr = result.data.bmr
        this.progressRecord.tdee = result.data.tdee
        this.progressRecord.calories_recommandees =
          result.data.calories_recommandees
        return { success: result.success, message: result.message }
      } catch (error) {
        throw error
      }
    },
  },
  persist: true,
})
