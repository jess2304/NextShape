import axios, { AxiosError, AxiosRequestTransformer } from "axios"
import { dateTransformer } from "@/assets/js/utils"
import { useAuthStore } from "@/stores/authStore"
import router from "@/router"
import {
  CaloriesResponse,
  LoginResponse,
  ProgressRecord,
  VerifyCodeResponse,
} from "@/assets/js/interfaces"

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

// Inscription
export const registerUser = async (userData: any) =>
  await api.post(`register/`, userData)

// Connexion
export const loginUser = async (credentials: {
  email: string
  password: string
}) => {
  const response = await api.post<LoginResponse>(`login/`, credentials)
  return response.data
}

// Déconnexion
export const logoutUser = async () => {
  await api.post(`logout/`)
}

export const checkAuthentication = async () => {
  try {
    const response = await api.get("check-authentication/")
    return response.data.authenticated
  } catch {
    return false
  }
}

// Update du profil
export const updateProfile = async (userData: any) => {
  const response = await api.patch("profile/", userData)
  return response.data
}

// Suppression du compte
export const deleteAccount = async () => await api.delete("delete-account/")

// Envoi de code de vérification selon un contexte
export const sendVerificationCode = async (
  email: string,
  context: "registration" | "reset-password"
) => await api.post(`send-code-${context}/`, { email })

// Verifier le code
export const verifyCode = async (
  email: string,
  code: string
): Promise<VerifyCodeResponse> => {
  const response = await api.post("verify-code/", {
    email,
    code,
  })
  return response.data
}

// Réinitialiser le mot de passe
export const resetPassword = async (email: string, password: string) => {
  const response = await api.post("reset-password/", {
    email,
    password,
  })
  return response.data
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ProgressRecord services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export const calculateCalories = async (payload: {
  gender: string | null
  age: number | null
  weight_kg: number | null
  height_cm: number | null
  activity_level: string | null
  goal: string | null
}): Promise<CaloriesResponse> => {
  try {
    const response = await api.post("calculate-calories/", payload)
    return response.data
  } catch (error) {
    throw error
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ProgressRecords (plural) services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export const getProgressRecords = async (): Promise<ProgressRecord[]> => {
  try {
    const response = await api.get("progress-records/")
    return response.data
  } catch (error) {
    throw error
  }
}

export const updateRecord = async (
  id: number,
  payload: Record<string, any>
): Promise<ProgressRecord> => {
  try {
    const response = await api.patch(`progress-records/${id}/`, payload)
    return response.data
  } catch (error) {
    throw error
  }
}

export const deleteRecord = async (id: number) => {
  try {
    await api.delete(`progress-records/${id}/`)
  } catch (error) {
    throw error
  }
}
