import { defineStore } from "pinia"
import { registerUser, loginUser } from "@/services/apiService"
import { updateProfile, deleteAccount } from "@/services/apiService"
import router from "@/router"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as {
      first_name: string
      last_name: string
      email: string
      birth_date: Date
      phone_number: string
    } | null,
    token: null as string | null,
  }),

  actions: {
    async register(userData: any) {
      // Appelle le service pour enregistrer un nouvel utilisateur
      const dateObj = new Date(userData.birth_date)
      userData.birth_date = dateObj.toISOString().split("T")[0]
      const payload = {
        username: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        birth_date: userData.birth_date,
        email: userData.email,
        phone_number: userData.phone_number,
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
      // Appelle le service pour se connecter
      try {
        const response = await loginUser(credentials)
        const { user, access } = response.data
        this.setUser(user, access)
        return response.data
      } catch (error: any) {
        throw (
          error.response?.data?.message ||
          "Une erreur est survenue lors de la connexion. Veuillez vérifier vos identifiants."
        )
      }
    },
    setUser(
      // Setter pour mettre à jour les données de l'utilisateur.
      userData: {
        first_name: string
        last_name: string
        email: string
        birth_date: Date
        phone_number: string
      },
      token: string
    ) {
      this.user = userData
      this.token = token
    },

    logout() {
      // Déconnexion de l'utilisateur.
      this.user = null
      this.token = null
    },

    async updateProfileField(field: string, value: any) {
      // Appelle le service pour modifier une valeur dans l'utilisateur.
      try {
        const payload: Record<string, any> = {}
        payload[field] = value

        const response = await updateProfile(payload, this.token)

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
      // Appelle le service pour supprimer tout un compte utilisateur.
      try {
        await deleteAccount(this.token)
        this.logout()
        // Rediriger vers la page de connexion
        router.push("/")
      } catch (error) {
        throw error
      }
    },
  },
  persist: {
    paths: ["user", "token"],
    storage: localStorage,
  },
})
