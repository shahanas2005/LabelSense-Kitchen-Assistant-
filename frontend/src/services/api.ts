import axios from 'axios'
import type { AnalysisResult, HistoryItem, Profile } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
})

export async function analyzeImage(file: File, userId?: number | null): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append('image', file)
  if (userId) {
    formData.append('user_id', String(userId))
  }
  const { data } = await api.post<AnalysisResult>('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function saveProfile(profile: Profile): Promise<Profile & { id: number; created_at: string; updated_at: string }> {
  const { data } = await api.post('/profile', profile)
  return data
}

export async function getHistory(userId?: number | null): Promise<HistoryItem[]> {
  const { data } = await api.get<{ items: HistoryItem[] }>('/history', {
    params: userId ? { user_id: userId } : {},
  })
  return data.items
}
