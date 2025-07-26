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
        const data = await getProgressRecords()
        this.progressRecords = data
      } catch (error) {
        throw error
      }
    },
    async updateRecord(id: number, payload: Record<string, any>) {
      try {
        const index = this.progressRecords.findIndex((r) => r.id === id)
        if (index !== -1) {
          const updatedRecord = await updateRecord(id, payload)
          this.progressRecords[index] = updatedRecord
        }
      } catch (error) {
        throw error
      }
    },
    async deleteRecord(id: number) {
      try {
        const index = this.progressRecords.findIndex((r) => r.id === id)
        if (index !== -1) {
          await deleteRecord(id)
          this.progressRecords.splice(index, 1)
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
