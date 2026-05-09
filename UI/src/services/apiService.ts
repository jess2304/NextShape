import axios, { AxiosError, AxiosRequestTransformer } from "axios"
import { dateTransformer } from "@/assets/js/utils"
import { useAuthStore } from "@/stores/authStore"
import router from "@/router"
import {
  ApiResponse,
  CaloriesData,
  NutritionPreferences,
  NutritionWeekPlan,
  ProgressRecord,
  User,
  VerifyCodeResponse,
} from "@/assets/js/interfaces"

const API_URL = import.meta.env.VITE_API_URL
const COACH_PLAN_TIMEOUT_MS = Number(
  import.meta.env.VITE_COACH_PLAN_TIMEOUT_MS || 300000
)

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  timeout: 60000,
  timeoutErrorMessage: "Le serveur n'a pas répondu à temps (60 secondes)",
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
  await api.post<ApiResponse<null>>(`register/`, userData)

// Login
export const loginUser = async (credentials: {
  email: string
  password: string
}) => {
  const response = await api.post<ApiResponse<User>>(`login/`, credentials)
  return response.data
}

// Logout
export const logoutUser = async () => {
  const response = await api.post<ApiResponse<null>>(`logout/`)
  return response.data
}

export const checkAuthentication = async () => {
  try {
    const response = await api.get<ApiResponse<{ authenticated: boolean }>>(
      "check-authentication/"
    )
    return response.data.data.authenticated
  } catch {
    return false
  }
}

// Profile update
export const updateProfile = async (userData: any) => {
  const response = await api.patch<ApiResponse<User>>("profile/", userData)
  return response.data
}

// Account deletion
export const deleteAccount = async () => {
  const response = await api.delete<ApiResponse<null>>("delete-account/")
  return response.data
}

// Send verification code based on context
export const sendVerificationCode = async (
  email: string,
  context: "registration" | "reset-password"
) => {
  const response = await api.post<ApiResponse<null>>(`send-code-${context}/`, {
    email,
  })
  return response.data
}

// Verify code
export const verifyCode = async (
  email: string,
  code: string
): Promise<VerifyCodeResponse> => {
  const response = await api.post<VerifyCodeResponse>("verify-code/", {
    email,
    code,
  })
  return response.data
}

// Reset password
export const resetPassword = async (
  email: string,
  password: string,
  code: string
) => {
  const response = await api.post<ApiResponse<null>>("reset-password/", {
    email,
    code,
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
}): Promise<ApiResponse<CaloriesData>> => {
  try {
    const response = await api.post<ApiResponse<CaloriesData>>(
      "calculate-calories/",
      payload
    )
    return response.data
  } catch (error) {
    throw error
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ProgressRecords services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export const getProgressRecords = async (): Promise<
  ApiResponse<ProgressRecord[]>
> => {
  try {
    const response = await api.get<ApiResponse<ProgressRecord[]>>(
      "progress-records/"
    )
    return response.data
  } catch (error) {
    throw error
  }
}

export const updateRecord = async (
  id: number,
  payload: Record<string, any>
): Promise<ApiResponse<ProgressRecord>> => {
  try {
    const response = await api.patch<ApiResponse<ProgressRecord>>(
      `progress-records/${id}/`,
      payload
    )
    return response.data
  } catch (error) {
    throw error
  }
}

export const deleteRecord = async (id: number) => {
  try {
    const response = await api.delete<ApiResponse<null>>(
      `progress-records/${id}/`
    )
    return response.data
  } catch (error) {
    throw error
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Contact services
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export const sendMail = async (payload: Record<string, any>) => {
  try {
    const response = await api.post<ApiResponse<null>>("contact/", payload)
    return response.data
  } catch (error) {
    throw error
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// AI coach service
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
export const getNutritionPreferences = async () => {
  const response = await api.get<ApiResponse<NutritionPreferences>>(
    "nutrition-preferences/"
  )
  return response.data
}

export const updateNutritionPreferences = async (
  payload: Partial<NutritionPreferences>
) => {
  const response = await api.patch<ApiResponse<NutritionPreferences>>(
    "nutrition-preferences/",
    payload
  )
  return response.data
}

export const generateWeekNutritionPlan = async () => {
  const response = await api.post<
    ApiResponse<{ plan: NutritionWeekPlan; updated_at: string | null }>
  >(
    "coach/week-plan/",
    {},
    {
      timeout: COACH_PLAN_TIMEOUT_MS,
      timeoutErrorMessage:
        "La génération du plan prend plus de temps que prévu. Réessayez dans un instant.",
    }
  )
  return response.data
}

export const getWeekNutritionPlan = async () => {
  const response = await api.get<
    ApiResponse<{ plan: NutritionWeekPlan | null; updated_at: string | null }>
  >("coach/week-plan/")
  return response.data
}
