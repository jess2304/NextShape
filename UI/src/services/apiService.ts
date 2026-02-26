import axios, { AxiosError, AxiosRequestTransformer } from "axios"
import { dateTransformer } from "@/assets/js/utils"
import { useAuthStore } from "@/stores/authStore"
import router from "@/router"
import {
  CaloriesResponse,
  LoginResponse,
  NutritionPreferences,
  NutritionWeekPlan,
  ProgressRecord,
  VerifyCodeResponse,
} from "@/assets/js/interfaces"

const API_URL = import.meta.env.VITE_API_URL

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  timeout: 60000,
  timeoutErrorMessage: "Le serveur na pas répondu à temps (60 secondes)",
  transformRequest: [
    dateTransformer,
    ...((axios.defaults.transformRequest as AxiosRequestTransformer[]) || []),
  ],
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response && error.response.status === 401) {
      try {
        // Attempt access token refresh
        await axios.post(`${API_URL}refresh-access/`, null, {
          withCredentials: true,
        })

        // Replay the original request after refresh
        const config = error.config
        return api(config!)
      } catch (refreshError) {
        // Refresh failed, so force logout
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
// Auth services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Registration
export const registerUser = async (userData: any) =>
  await api.post(`register/`, userData)

// Login
export const loginUser = async (credentials: {
  email: string
  password: string
}) => {
  const response = await api.post<LoginResponse>(`login/`, credentials)
  return response.data
}

// Logout
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

// Profile update
export const updateProfile = async (userData: any) => {
  const response = await api.patch("profile/", userData)
  return response.data
}

// Account deletion
export const deleteAccount = async () => await api.delete("delete-account/")

// Send verification code based on context
export const sendVerificationCode = async (
  email: string,
  context: "registration" | "reset-password"
) => await api.post(`send-code-${context}/`, { email })

// Verify code
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

// Reset password
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
// ProgressRecords services
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

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Contact services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export const sendMail = async (payload: Record<string, any>) => {
  try {
    await api.post("contact/", payload)
  } catch (error) {
    throw error
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// AI coach service
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export const getNutritionPreferences = async () => {
  const response = await api.get<{
    success: boolean
    message: string
    data: NutritionPreferences
  }>("nutrition-preferences/")
  return response.data
}

export const updateNutritionPreferences = async (
  payload: Partial<NutritionPreferences>
) => {
  const response = await api.patch<{
    success: boolean
    message: string
    data: NutritionPreferences
  }>("nutrition-preferences/", payload)
  return response.data
}

export const generateWeekNutritionPlan = async (language: string) => {
  const response = await api.post<{
    success: boolean
    message: string
    data: NutritionWeekPlan
  }>("coach/week-plan/", { language })
  return response.data
}
