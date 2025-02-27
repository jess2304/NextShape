import { defineStore } from "pinia"
import { registerUser, loginUser } from "@/services/apiService"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as { firstName: string; lastName: string; email: string } | null,
    token: null as string | null,
  }),

  actions: {
    async register(userData: any) {
      // Fromatage de la date
      const dateObj = new Date(userData.birthDate)
      const formattedDate = dateObj.toISOString().split("T")[0] // "YYYY-MM-DD"
      userData.birthDate = formattedDate
      // Préparation du payload
      const payload = {
        username: userData.email,
        first_name: userData.firstName,
        last_name: userData.lastName,
        birth_date: userData.birthDate,
        email: userData.email,
        phone_number: userData.phone,
        password: userData.password,
      }
      try {
        const response = await registerUser(payload)
        return response.data
      } catch (error: any) {
        throw (
          error.response?.data?.message ||
          "Une erreur est survenue lors de l'inscription. Veuillez vérifier vos données."
        )
      }
    },
    async login(credentials: any) {
      try {
        const response = await loginUser(credentials)
        const { user, token } = response.data
        this.setUser(user, token)
        return response.data
      } catch (error: any) {
        throw (
          error.response?.data?.message ||
          "Une erreur est survenue lors de la connexion. Veuillez vérifier vos identifiants."
        )
      }
    },
    setUser(
      userData: { firstName: string; lastName: string; email: string },
      token: string
    ) {
      this.user = userData
      this.token = token
      localStorage.setItem("user", JSON.stringify(userData))
      localStorage.setItem("token", token)
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem("user")
      localStorage.removeItem("token")
    },

    loadStoredUser() {
      const storedUser = localStorage.getItem("user")
      const storedToken = localStorage.getItem("token")

      if (storedUser && storedToken) {
        this.user = JSON.parse(storedUser)
        this.token = storedToken
      }
    },
  },
})
