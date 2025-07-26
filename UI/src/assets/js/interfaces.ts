// Response to calories computation
export interface CaloriesResponse {
  success: boolean
  message: string
  data: {
    bmr: number
    tdee: number
    calories_recommandees: number
  }
}

// Response to login
export interface LoginResponse {
  data: {
    first_name: string
    last_name: string
    email: string
    gender: string
    birth_date: string
    phone_number: string
  }
  access: string
}

// Response to verify code
export interface VerifyCodeResponse {
  success: boolean
  message: string
}

// User structure
export interface User {
  first_name: string
  last_name: string
  email: string
  gender: string
  birth_date: string
  phone_number: string
  [key: string]: string
}

// ProgressRecord structure
export interface ProgressRecord {
  user: User | null
  date: string | null
  weight_kg: number | null
  height_cm: number | null
  imc: number | null
  gender: string | null
  age: number | null
  activity_level: string | null
  goal: string | null
  bmr: number | null
  tdee: number | null
  calories_recommandees: number | null
  created_at: Date | null
  modified_at: Date | null
  [key: string]: string | User | number | Date | null
}

// Credentials
export interface Credentials {
  email: string | null
  password: string | null
}

// Registration Form
export interface RegistrationForm {
  first_name: string | null
  last_name: string | null
  gender: string
  birth_date: Date | null
  email: string | null
  confirmEmail: string | null
  phone_number: string | null
  password: string | null
  confirmPassword: string | null
}
