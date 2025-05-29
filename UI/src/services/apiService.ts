import axios, { AxiosError, AxiosRequestTransformer } from "axios"
import { dateTransformer } from "@/assets/js/utils"
import { useAuthStore } from "@/stores/authStore"
import { useToast } from "primevue/usetoast"
import router from "@/router"

const API_URL = import.meta.env.VITE_API_URL

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

export interface LoginResponse {
  user: {
    first_name: string
    last_name: string
    email: string
    birth_date: string
    phone_number: string
  }
  access: string
}
export interface VerifyCodeResponse {
  valid: boolean
}

const authHeader = (token: string | null) => ({
  headers: {
    Authorization: `Bearer ${token}`,
  },
})

// Inscription
export const registerUser = async (userData: any) =>
  await api.post(`${API_URL}register/`, userData)

// Connexion
export const loginUser = async (credentials: {
  email: string
  password: string
}) => {
  const response = await api.post<LoginResponse>(
    `${API_URL}login/`,
    credentials
  )
  return response.data
}

// Update du profil
export const updateProfile = async (userData: any, token: string | null) => {
  const response = await api.patch(
    `${API_URL}profile/`,
    userData,
    authHeader(token)
  )
  return response.data
}

// Suppression du compte
export const deleteAccount = async (token: string | null) =>
  await api.delete(`${API_URL}delete-account/`, authHeader(token))

// Envoi de code de vérification selon un contexte
export const sendVerificationCode = async (
  email: string,
  context: "registration" | "reset-password"
) => await api.post(`${API_URL}send-code-${context}/`, { email })

// Verifier le code
export const verifyCode = async (
  email: string,
  code: string
): Promise<VerifyCodeResponse> => {
  const response = await api.post(`${API_URL}verify-code/`, {
    email,
    code,
  })
  return response.data
}

// Réinitialiser le mot de passe
export const resetPassword = async (email: string, password: string) => {
  const response = await api.post(`${API_URL}reset-password/`, {
    email,
    password,
  })
  return response.data
}
