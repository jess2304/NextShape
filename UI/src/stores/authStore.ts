import { defineStore } from "pinia"
import {
  sendVerificationCode,
  verifyCode,
  updateProfile,
  deleteAccount,
  resetPassword,
  registerUser,
  loginUser,
  logoutUser,
  checkAuthentication,
} from "@/services/apiService"
import router from "@/router"
import { useProgressRecord } from "@/stores/progressRecordStore"
import { User, VerifyCodeResponse } from "@/assets/js/interfaces"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
  }),

  actions: {
    async register(userData: any) {
      // Call service to register a new user
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
        throw error.response?.data?.message || "Erreur lors de l'inscription."
      }
    },
    async login(credentials: { email: string; password: string }) {
      // Call service to log in
      try {
        const response = await loginUser(credentials)
        const user = response.data
        this.setUser(user)
        const progressStore = useProgressRecord()
        progressStore.$reset()
        return response.data
      } catch (error: any) {
        throw error.response?.data?.message || "Erreur lors de la connexion."
      }
    },
    setUser(
      // Setter to update user data.
      userData: User
    ) {
      this.user = userData
    },

    async logout() {
      // Logout the user.
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
      // Call service to update one user field.
      try {
        const response = await updateProfile(payload)
        this.user = response.data
        return response.data
      } catch (error: any) {
        throw (
          error.response?.data?.message ||
          "Erreur lors de la mise à jour de votre profil."
        )
      }
    },

    async deleteAccount() {
      // Call service to delete the user account.
      try {
        await deleteAccount()
        await this.logout()
        // Redirect to the home page
        router.push("/")
      } catch (error) {
        throw error
      }
    },

    async sendVerificationCode(
      email: string,
      context: "registration" | "reset-password"
    ) {
      try {
        await sendVerificationCode(email, context)
      } catch (error) {
        throw error
      }
    },

    async verifyCode(email: string, code: string): Promise<VerifyCodeResponse> {
      const response = await verifyCode(email, code)
      return response
    },

    async resetPassword(email: string, newPassword: string) {
      try {
        const response = await resetPassword(email, newPassword)
        return response
      } catch (error) {
        throw error
      }
    },
  },

  persist: true,
})
