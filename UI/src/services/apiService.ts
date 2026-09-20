import axios, {
  AxiosError,
  AxiosRequestTransformer,
  InternalAxiosRequestConfig,
} from "axios"
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
const REFRESH_URL = API_URL + "refresh-access/"
const COACH_PLAN_TIMEOUT_MS = Number(
  import.meta.env.VITE_COACH_PLAN_TIMEOUT_MS || 300000
)

type RequestSignal = NonNullable<InternalAxiosRequestConfig["signal"]>
type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean }

let sessionController = new AbortController()
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  signal: sessionController.signal,
  timeout: 60000,
  timeoutErrorMessage: "Le serveur n'a pas répondu à temps (60 secondes)",
  transformRequest: [
    dateTransformer,
    ...((axios.defaults.transformRequest as AxiosRequestTransformer[]) || []),
  ],
})

let csrfRequest: Promise<string> | null = null
let refreshRequest: { signal: RequestSignal; promise: Promise<void> } | null =
  null

const assertActiveSession = (signal?: RequestSignal): void => {
  if (signal?.aborted) throw new axios.CanceledError("Connexion terminée")
}

export const resetApiSession = (): void => {
  const previousController = sessionController
  sessionController = new AbortController()
  api.defaults.signal = sessionController.signal
  csrfRequest = null
  refreshRequest = null
  previousController.abort()
}

// apply et finish doivent être synchrones : aucune fonction async ici.
export async function runSessionRequest<T>(
  request: () => Promise<T>,
  apply: (response: T) => void,
  finish?: () => void
): Promise<T> {
  const signal = sessionController.signal
  try {
    const response = await request()
    assertActiveSession(signal)
    apply(response)
    return response
  } catch (error) {
    assertActiveSession(signal)
    throw error
  } finally {
    if (!signal.aborted) finish?.()
  }
}

export const getCsrfToken = (): Promise<string> => {
  if (csrfRequest === null) {
    const request: Promise<string> = api
      .get<ApiResponse<{ csrfToken: string }>>("csrf/")
      .then((response) => response.data.data.csrfToken)
      .finally(() => {
        if (csrfRequest === request) csrfRequest = null
      })
    csrfRequest = request
  }
  return csrfRequest
}

const refreshAccess = (signal: RequestSignal): Promise<void> => {
  assertActiveSession(signal)
  if (refreshRequest?.signal === signal) return refreshRequest.promise

  const request: Promise<void> = (async () => {
    const csrfToken = await getCsrfToken()
    assertActiveSession(signal)
    await axios.post(REFRESH_URL, null, {
      signal,
      withCredentials: true,
      timeout: 60000,
      headers: { "X-CSRFToken": csrfToken },
    })
    assertActiveSession(signal)
  })().finally(() => {
    if (refreshRequest?.promise === request) refreshRequest = null
  })

  refreshRequest = { signal, promise: request }
  return request
}

api.interceptors.request.use(async (config) => {
  assertActiveSession(config.signal)
  const method = (config.method ?? "GET").toUpperCase()
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = await getCsrfToken()
    assertActiveSession(config.signal)
    config.headers.set("X-CSRFToken", csrfToken)
  }
  return config
})

const noRefresh = new Set(["csrf/", "login/", "logout/", "refresh-access/"])

const expireLocalSession = (): void => {
  useAuthStore().clearLocalSession(true)
  void router.replace("/connexion")
}

api.interceptors.response.use(
  (response) => {
    assertActiveSession(response.config.signal)
    return response
  },
  async (error: AxiosError) => {
    if (axios.isCancel(error)) throw error
    const config = error.config as RetryConfig | undefined
    assertActiveSession(config?.signal)

    if (
      error.response?.status !== 401 ||
      !config?.signal ||
      noRefresh.has(config.url ?? "") ||
      (useAuthStore().isChangingSession && config.url !== "delete-account/")
    ) {
      throw error
    }

    if (config._retry) {
      expireLocalSession()
      throw new axios.CanceledError("Session expirée")
    }

    config._retry = true
    try {
      await refreshAccess(config.signal)
      assertActiveSession(config.signal)
    } catch (refreshError) {
      assertActiveSession(config.signal)
      if (axios.isCancel(refreshError)) throw refreshError
      if (
        axios.isAxiosError(refreshError) &&
        refreshError.response?.status === 401 &&
        refreshError.config?.url === REFRESH_URL
      ) {
        expireLocalSession()
        throw new axios.CanceledError("Session expirée")
      }
      throw refreshError
    }

    return api(config)
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

export const checkAuthentication = async (): Promise<{
  authenticated: boolean
  user: User | null
}> => {
  const response = await api.get<
    ApiResponse<{ authenticated: boolean; user: User | null }>
  >("check-authentication/")
  return response.data.data
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
