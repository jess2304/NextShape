import {
  AxiosRequestTransformer,
  InternalAxiosRequestConfig,
  AxiosRequestHeaders,
} from "axios"
import { API_MESSAGES_FR } from "@/assets/js/messages.fr"

const isPlainObject = (v: unknown) =>
  Object.prototype.toString.call(v) === "[object Object]"

export const dateTransformer: AxiosRequestTransformer = function (
  this: InternalAxiosRequestConfig,
  data: any,
  headers: AxiosRequestHeaders
): any {
  if (data instanceof Date) {
    const year = data.getFullYear()
    const month = String(data.getMonth() + 1).padStart(2, "0")
    const day = String(data.getDate()).padStart(2, "0")
    return `${year}-${month}-${day}`
  }

  if (Array.isArray(data)) {
    return data.map((val) => dateTransformer.call(this, val, headers))
  }

  if (isPlainObject(data)) {
    return Object.fromEntries(
      Object.entries(data).map(([key, val]) => [
        key,
        dateTransformer.call(this, val, headers),
      ])
    )
  }

  return data
}

export const validateRequiredFields = (data: any, fields: string[]): string[] =>
  fields.filter((field) => !data[field])

export const showToast = (
  toast: any,
  severity: "success" | "error" | "info",
  summary: string,
  detail = ""
) => {
  toast.add({
    severity,
    summary,
    detail,
    life: 5000,
  })
}

const extractFirstError = (errors: any): string | null => {
  if (!errors) return null
  if (Array.isArray(errors) && errors.length) return String(errors[0])
  if (typeof errors === "object") {
    for (const value of Object.values(errors)) {
      if (Array.isArray(value) && value.length) return String(value[0])
      if (value) return String(value)
    }
  }
  if (typeof errors === "string") return errors
  return null
}

export const resolveApiMessage = (
  payload: any,
  fallback = "Une erreur est survenue."
): string => {
  if (!payload || typeof payload !== "object") return fallback

  const code = typeof payload.code === "string" ? payload.code : ""
  if (code && API_MESSAGES_FR[code]) {
    return API_MESSAGES_FR[code]
  }

  if (typeof payload.message === "string" && payload.message.trim()) {
    return payload.message
  }

  if (typeof payload.detail === "string" && payload.detail.trim()) {
    return payload.detail
  }

  const firstError = extractFirstError(payload.errors)
  return firstError || fallback
}

export const resolveApiErrorMessage = (
  error: any,
  fallback = "Une erreur est survenue."
): string => {
  const payload = error?.response?.data
  if (!payload) return fallback
  return resolveApiMessage(payload, fallback)
}

export const getAgeFromBirthDate = (
  birthDateStr: string | null | undefined
): number | null => {
  if (!birthDateStr) return null

  const birthDate = new Date(birthDateStr)
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()

  const hasBirthdayPassedThisYear =
    today.getMonth() > birthDate.getMonth() ||
    (today.getMonth() === birthDate.getMonth() &&
      today.getDate() >= birthDate.getDate())

  if (!hasBirthdayPassedThisYear) {
    age--
  }
  return age
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString("fr-FR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}
