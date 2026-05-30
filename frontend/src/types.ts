export type Profile = {
  user_id?: number | null
  email?: string | null
  display_name?: string | null
  age_group?: 'elderly' | 'adult' | null
  conditions: string[]
  allergies: string[]
  diet: string[]
  language: 'en' | 'ur'
  notes: string
}

export type Warning = {
  warning: string
  severity: 'high' | 'medium' | 'low'
  reason: string
  ingredient?: string
  rule: string
}

export type AnalysisResult = {
  analysis_id: number
  expiry_status: string
  expiry_date: string | null
  ingredients: string[]
  warnings: Warning[]
  confidence: number
  manufacturing_date?: string | null
  manufacturing_source?: string | null
  net_weight?: string | null
  net_weight_source?: string | null
  label_details?: Array<{ field: string; value: string | null; source?: string | null; matched_text?: string | null; confidence?: number }>
  speech_text: string
  raw_text: string
  audio_url?: string | null
}

export type HistoryItem = {
  id: number
  user_id: number | null
  image_path: string
  expiry_status: string
  expiry_date: string | null
  ingredients: string[]
  warnings: Warning[]
  confidence: number
  speech_text: string
  created_at: string
}
