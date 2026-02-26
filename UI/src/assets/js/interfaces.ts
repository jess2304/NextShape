// Generic API response envelope
export interface ApiResponse<T = unknown, E = Record<string, any>> {
  success: boolean
  code: string
  message: string
  data: T
  errors?: E
}

// Response to calories computation
export interface CaloriesData {
  bmr: number
  tdee: number
  calories_recommandees: number
}

// Response to verify code
export type VerifyCodeResponse = ApiResponse<{ valid: boolean }>

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
  id: number
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

// Nutrition preferences
export interface NutritionPreferences {
  allergies: string
  diet_type: string
  disliked_foods: string
  supplements: string[]
  meals_per_day: number
}

// Nutrition plan meal item
export interface NutritionPlanMealItem {
  name: string
  portion: string
  note?: string | null
}

// Nutrition plan meal
export interface NutritionPlanMeal {
  title: string
  items: NutritionPlanMealItem[]
  approx_calories: number
  approx_protein_g: number
  approx_fat_g: number
  approx_carbs_g: number
}

// Nutrition plan for a day
export interface NutritionPlanDay {
  day_index: number
  meals: NutritionPlanMeal[]
}

// Nutrition plan for a whole week
export interface NutritionWeekPlan {
  calories_target: number
  protein_g_target: number
  fat_g_target: number
  carbs_g_target: number
  meals_per_day: number
  days: NutritionPlanDay[]
  notes: string[]
}
