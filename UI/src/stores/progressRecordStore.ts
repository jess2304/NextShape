import { defineStore } from "pinia"
import { calculateIMC } from "@/services/apiService"
import { User } from "@/stores/authStore"

export interface ProgressRecord {
  user: User
  date: Date
  weight_kg: number
  height_cm: number
  imc: number
  created_at: Date
  modified_at: Date
  [key: string]: string | User | number | Date
}

export const useProgressRecord = defineStore("progressRecord", {
  state: () => ({
    progressRecord: null as ProgressRecord | null,
  }),
  actions: {
    async calculateIMC(weight_kg: number, height_cm: number) {
      try {
        const response = await calculateIMC({ weight_kg, height_cm })
        this.progressRecord = response.data
      } catch (error: any) {
        throw error
      }
    },
  },
  persist: true,
})
