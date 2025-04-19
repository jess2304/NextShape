import axios, { AxiosError, AxiosRequestTransformer } from "axios"
import { dateTransformer } from "@/assets/js/utils"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import router from "@/router"

const API_URL = "http://127.0.0.1:8000/api/"

const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
  timeoutErrorMessage: "Le serveur na pas répondu à temps (20 secondes)",
  transformRequest: [
    dateTransformer,
    ...((axios.defaults.transformRequest as AxiosRequestTransformer[]) || []),
  ],
})

// Intercepteur de réponse
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response && error.response.status === 401) {
      // Afficher un toast indiquant que la session a expiré
      const toast = useToast()
      toast.add({
        severity: "error",
        summary: "Session expirée",
        detail: "Votre session a expiré. Veuillez vous reconnecter.",
        life: 5000,
      })
      // Si on reçoit un 401, c'est probablement que le token a expiré ou est invalide.
      // On récupère le store auth et on déconnecte l'utilisateur
      const authStore = useAuthStore()
      authStore.logout()
      // Rediriger vers la page de connexion
      router.push("/connexion")
    }
    return Promise.reject(error)
  }
)

export const registerUser = async (userData) =>
  await api.post(`${API_URL}register/`, userData)

export const loginUser = async (credentials) =>
  await api.post(`${API_URL}login/`, credentials)

export const updateProfile = async (userData, token) => {
  const response = await api.patch(`${API_URL}profile/`, userData, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  return response
}

export const deleteAccount = async (token) => {
  await api.delete(`${API_URL}delete-account/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}
