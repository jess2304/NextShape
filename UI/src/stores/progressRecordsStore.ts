import { ProgressRecord } from "@/assets/js/interfaces"
import {
  getProgressRecords,
  updateRecord,
  deleteRecord,
  runSessionRequest,
} from "@/services/apiService"
import { defineStore } from "pinia"

export const useProgressRecords = defineStore("progressRecords", {
  state: () => ({
    progressRecords: [] as ProgressRecord[],
  }),
  actions: {
    getProgressRecords() {
      return runSessionRequest(
        () => getProgressRecords(),
        (response) => {
          this.progressRecords = response.data
        }
      )
    },
    updateRecord(id: number, payload: Record<string, any>) {
      return runSessionRequest(
        () => updateRecord(id, payload),
        (response) => {
          const index = this.progressRecords.findIndex((r) => r.id === id)
          if (index !== -1) this.progressRecords[index] = response.data
        }
      )
    },
    deleteRecord(id: number) {
      return runSessionRequest(
        () => deleteRecord(id),
        () => {
          this.progressRecords = this.progressRecords.filter((r) => r.id !== id)
        }
      )
    },
    reset() {
      this.progressRecords = []
    },
  },
})
