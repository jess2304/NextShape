import axios from "axios"
import { defineStore } from "pinia"
import {
  sendVerificationCode as sendVerificationCodeRequest,
  verifyCode as verifyCodeRequest,
  updateProfile as updateProfileRequest,
  deleteAccount as deleteAccountRequest,
  resetPassword as resetPasswordRequest,
  registerUser,
  loginUser,
  logoutUser,
  checkAuthentication,
  resetApiSession,
  runSessionRequest,
} from "@/services/apiService"
import router from "@/router"
import { useProgressRecord } from "@/stores/progressRecordStore"
import { User, VerifyCodeResponse } from "@/assets/js/interfaces"
import { resolveApiErrorMessage } from "@/assets/js/utils"
import { useProgressRecords } from "./progressRecordsStore"
import { useCoachStore } from "./coachStore"

let sessionChannel: BroadcastChannel | null = null

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    isChangingSession: false,
  }),

  actions: {
    async register(userData: any) {
      const payload = {
        username: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        gender: userData.gender,
        birth_date: userData.birth_date,
        email: userData.email,
        phone_number: userData.phone_number,
        password: userData.password,
        code: userData.code,
      }
      try {
        const response = await registerUser(payload)
        return response.data
      } catch (error: any) {
        if (axios.isCancel(error)) throw error
        throw resolveApiErrorMessage(error, "Erreur lors de l'inscription.")
      }
    },

    setSessionUser(userData: User | null, notifyOtherTabs = false): void {
      resetApiSession()
      this.user = userData
      useProgressRecord().$reset()
      useProgressRecords().$reset()
      useCoachStore().$reset()
      if (notifyOtherTabs) sessionChannel?.postMessage("changed")
    },

    clearLocalSession(notifyOtherTabs = false): void {
      this.setSessionUser(null, notifyOtherTabs)
    },

    async login(credentials: { email: string; password: string }) {
      if (this.isChangingSession)
        throw new axios.CanceledError("Connexion en cours")
      this.isChangingSession = true
      this.setSessionUser(this.user)
      try {
        return await runSessionRequest(
          () => loginUser(credentials),
          (response) => this.setSessionUser(response.data, true)
        )
      } finally {
        this.isChangingSession = false
      }
    },

    async logout() {
      if (this.isChangingSession)
        throw new axios.CanceledError("Connexion en cours")
      this.isChangingSession = true
      this.setSessionUser(this.user)
      try {
        await runSessionRequest(
          () => logoutUser(),
          () => {
            this.setSessionUser(null, true)
            void router.replace("/connexion")
          }
        )
      } finally {
        this.isChangingSession = false
      }
    },

    async checkAuthentication() {
      if (this.isChangingSession)
        throw new axios.CanceledError("Connexion en cours")
      const result = await runSessionRequest(
        () => checkAuthentication(),
        ({ authenticated, user }) => {
          const nextUser = authenticated ? user : null
          if (nextUser?.email !== this.user?.email) {
            this.setSessionUser(nextUser)
          } else {
            this.user = nextUser
          }
        }
      )
      return result.authenticated
    },

    async updateProfileField(field: string, value: any) {
      return runSessionRequest(
        () => updateProfileRequest({ [field]: value }),
        (response) => {
          this.user = response.data
        }
      )
    },

    async deleteAccount() {
      if (this.isChangingSession)
        throw new axios.CanceledError("Connexion en cours")
      this.isChangingSession = true
      this.setSessionUser(this.user)
      try {
        return await runSessionRequest(
          () => deleteAccountRequest(),
          () => {
            this.setSessionUser(null, true)
            void router.replace("/")
          }
        )
      } finally {
        this.isChangingSession = false
      }
    },

    async sendVerificationCode(
      email: string,
      context: "registration" | "reset-password"
    ) {
      try {
        return await sendVerificationCodeRequest(email, context)
      } catch (error) {
        if (axios.isCancel(error)) throw error
        throw resolveApiErrorMessage(error, "Échec de l'envoi du code.")
      }
    },

    async verifyCode(email: string, code: string): Promise<VerifyCodeResponse> {
      try {
        return await verifyCodeRequest(email, code)
      } catch (error) {
        if (axios.isCancel(error)) throw error
        throw resolveApiErrorMessage(error, "Erreur lors de la vérification.")
      }
    },

    async resetPassword(email: string, newPassword: string, code: string) {
      try {
        return await resetPasswordRequest(email, newPassword, code)
      } catch (error) {
        if (axios.isCancel(error)) throw error
        throw resolveApiErrorMessage(
          error,
          "Erreur lors de la mise à jour du mot de passe."
        )
      }
    },
  },
})

// Called after Pinia is installed; only a notification crosses tabs, never user data.
export const startSessionSync = (): (() => void) => {
  if (typeof BroadcastChannel === "undefined") return () => {}
  sessionChannel?.close()
  const channel = new BroadcastChannel("nextshape-session")
  sessionChannel = channel
  channel.addEventListener("message", (event) => {
    if (event.data !== "changed") return
    useAuthStore().clearLocalSession()
    void router.replace({ path: "/", force: true })
  })
  return () => {
    channel.close()
    if (sessionChannel === channel) sessionChannel = null
  }
}
