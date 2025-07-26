import {
  AxiosRequestTransformer,
  InternalAxiosRequestConfig,
  AxiosRequestHeaders,
} from "axios"

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
