import { ProgressRecord } from "@/assets/js/interfaces"
import {
  getProgressRecords,
  updateRecord,
  deleteRecord,
} from "@/services/apiService"
import { defineStore } from "pinia"

export const useProgressRecords = defineStore("progressRecords", {
  state: () => ({
    progressRecords: [] as ProgressRecord[],
  }),
  actions: {
    async getProgressRecords() {
      try {
        const response = await getProgressRecords()
        this.progressRecords = response.data
        return response
      } catch (error) {
        throw error
      }
    },
    async updateRecord(id: number, payload: Record<string, any>) {
      try {
        const index = this.progressRecords.findIndex((r) => r.id === id)
        if (index !== -1) {
          const response = await updateRecord(id, payload)
          this.progressRecords[index] = response.data
          return response
        }
      } catch (error) {
        throw error
      }
    },
    async deleteRecord(id: number) {
      try {
        const index = this.progressRecords.findIndex((r) => r.id === id)
        if (index !== -1) {
          const response = await deleteRecord(id)
          this.progressRecords.splice(index, 1)
          return response
        }
      } catch (error) {
        throw error
      }
    },
    reset() {
      this.progressRecords = []
    },
  },
  persist: true,
})
