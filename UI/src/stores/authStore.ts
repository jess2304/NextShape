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
} from "@/services/apiService"
import router from "@/router"
import { useProgressRecord } from "@/stores/progressRecordStore"
import { User, VerifyCodeResponse } from "@/assets/js/interfaces"
import { resolveApiErrorMessage } from "@/assets/js/utils"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
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
      }
      try {
        const response = await registerUser(payload)
        return response.data
      } catch (error: any) {
        throw resolveApiErrorMessage(error, "Erreur lors de l'inscription.")
      }
    },

    async login(credentials: { email: string; password: string }) {
      try {
        const response = await loginUser(credentials)
        this.setUser(response.data)
        const progressStore = useProgressRecord()
        progressStore.$reset()
        return response
      } catch (error: any) {
        throw resolveApiErrorMessage(error, "Erreur lors de la connexion.")
      }
    },

    setUser(userData: User) {
      this.user = userData
    },

    async logout() {
      try {
        await logoutUser()
      } catch {
      } finally {
        this.user = null
        const progressStore = useProgressRecord()
        progressStore.$reset()
        router.push("/connexion")
      }
    },

    async checkAuthentication() {
      const isAuthenticated = await checkAuthentication()
      if (!isAuthenticated) {
        await this.logout()
      }
      return isAuthenticated
    },

    async updateProfileField(field: string, value: any) {
      const payload: Record<string, any> = { [field]: value }
      try {
        const response = await updateProfileRequest(payload)
        this.user = response.data
        return response
      } catch (error: any) {
        throw resolveApiErrorMessage(
          error,
          "Erreur lors de la mise à jour de votre profil."
        )
      }
    },

    async deleteAccount() {
      try {
        const response = await deleteAccountRequest()
        await this.logout()
        router.push("/")
        return response
      } catch (error) {
        throw resolveApiErrorMessage(
          error,
          "Échec de la suppression du compte."
        )
      }
    },

    async sendVerificationCode(
      email: string,
      context: "registration" | "reset-password"
    ) {
      try {
        return await sendVerificationCodeRequest(email, context)
      } catch (error) {
        throw resolveApiErrorMessage(error, "Échec de l'envoi du code.")
      }
    },

    async verifyCode(email: string, code: string): Promise<VerifyCodeResponse> {
      try {
        return await verifyCodeRequest(email, code)
      } catch (error) {
        throw resolveApiErrorMessage(error, "Erreur lors de la vérification.")
      }
    },

    async resetPassword(email: string, newPassword: string, code: string) {
      try {
        return await resetPasswordRequest(email, newPassword, code)
      } catch (error) {
        throw resolveApiErrorMessage(
          error,
          "Erreur lors de la mise à jour du mot de passe."
        )
      }
    },
  },

  persist: true,
})
