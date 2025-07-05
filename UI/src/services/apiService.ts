import axios, { AxiosError, AxiosRequestTransformer } from "axios"
import { dateTransformer } from "@/assets/js/utils"
import { useAuthStore } from "@/stores/authStore"
import router from "@/router"

const API_URL = import.meta.env.VITE_API_URL

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
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
  async (error: AxiosError) => {
    if (error.response && error.response.status === 401) {
      try {
        // Tenter le refresh-access
        await axios.post(`${API_URL}refresh-access/`, null, {
          withCredentials: true,
        })

        // Rejouer la requête originale après refresh
        const config = error.config
        return api(config!)
      } catch (refreshError) {
        // Échec du refresh donc déconnexion
        const authStore = useAuthStore()
        authStore.logout()
        router.push("/connexion")
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Auth Services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export interface LoginResponse {
  data: {
    first_name: string
    last_name: string
    email: string
    birth_date: string
    phone_number: string
  }
  access: string
}
export interface VerifyCodeResponse {
  success: boolean
  message: string
}

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

export const checkAuthentication = async () => {
  try {
    const response = await api.get(`${API_URL}check-authentication/`, {
      withCredentials: true,
    })
    return response.data.authenticated
  } catch {
    return false
  }
}

// Update du profil
export const updateProfile = async (userData: any) => {
  const response = await api.patch(`${API_URL}profile/`, userData, {
    withCredentials: true,
  })
  return response.data
}

// Suppression du compte
export const deleteAccount = async () =>
  await api.delete(`${API_URL}delete-account/`, { withCredentials: true })

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

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ProgressRecord services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

export const calculateIMC = async (payload: {
  weight_kg: number
  height_cm: number
}) => {
  try {
    const response = await api.post(`${API_URL}calculate-imc/`, payload, {
      withCredentials: true,
    })
    return response.data
  } catch (error) {
    throw error
  }
}
