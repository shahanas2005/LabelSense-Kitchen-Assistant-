import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { AlertCircle, ArrowRight, Sparkles } from 'lucide-react'
import { analyzeImage } from '../services/api'
import type { AnalysisResult, Profile } from '../types'
import { UploadZone } from '../components/UploadZone'
import { AnalysisCards } from '../components/AnalysisCards'
import { VoicePlayer } from '../components/VoicePlayer'

type HomePageProps = {
  profile: Profile
  onProfileJump: () => void
}

export function HomePage({ profile, onProfileJump }: HomePageProps) {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)

  const startAnalysis = async () => {
    if (!file) {
      setError('Please choose an image first.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const response = await analyzeImage(file, profile.user_id)
      setResult(response)
      sessionStorage.setItem('last-analysis', JSON.stringify(response))
      navigate('/result')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Analysis failed. Check the backend connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <motion.section className="glass-card overflow-hidden p-8 lg:p-10" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
        <div className="grid gap-10 lg:grid-cols-[1.4fr_0.9fr] lg:items-center">
          <div className="space-y-6">
            <span className="inline-flex items-center gap-2 rounded-full bg-mist-100 px-4 py-2 text-sm font-bold uppercase tracking-[0.24em] text-mist-800">
              <Sparkles className="h-4 w-4" />
              LabelSense
            </span>
            <h1 className="max-w-3xl text-5xl font-black tracking-tight text-slate-950 sm:text-6xl">
              Read expiry dates, ingredients, and health warnings in one scan.
            </h1>
            <p className="max-w-2xl text-xl leading-9 text-slate-600">
              Built for clarity and speed, with large readable typography, high contrast cards, and voice playback for elderly users.
            </p>
            <div className="flex flex-wrap gap-4">
              <button className="big-button bg-mist-700 text-white hover:bg-mist-600" onClick={startAnalysis} disabled={loading}>
                {loading ? 'Analyzing...' : 'Analyze Image'}
                <ArrowRight className="h-5 w-5" />
              </button>
              <button className="big-button border border-slate-200 bg-white text-slate-900 hover:bg-slate-50" onClick={onProfileJump}>
                <AlertCircle className="h-5 w-5" />
                Update profile
              </button>
            </div>
            {error ? <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-lg font-medium text-rose-700">{error}</p> : null}
          </div>
          <div className="rounded-[2rem] bg-soft-radial p-1 shadow-halo">
            <div className="rounded-[1.8rem] bg-slate-950/92 p-6 text-white">
              <p className="text-sm uppercase tracking-[0.24em] text-mist-200">Live profile</p>
              <div className="mt-4 space-y-3 text-lg">
                <p><span className="font-semibold text-mist-200">User:</span> {profile.display_name || 'Guest'}</p>
                <p><span className="font-semibold text-mist-200">Age group:</span> {profile.age_group || 'Not set'}</p>
                <p><span className="font-semibold text-mist-200">Conditions:</span> {profile.conditions.length ? profile.conditions.join(', ') : 'None'}</p>
                <p><span className="font-semibold text-mist-200">Allergies:</span> {profile.allergies.length ? profile.allergies.join(', ') : 'None'}</p>
                <p><span className="font-semibold text-mist-200">Diet:</span> {profile.diet.length ? profile.diet.join(', ') : 'None'}</p>
                <p><span className="font-semibold text-mist-200">Language:</span> {profile.language === 'ur' ? 'Urdu' : 'English'}</p>
              </div>
              <div className="mt-8 rounded-3xl bg-white/10 p-5">
                <p className="text-sm uppercase tracking-[0.24em] text-mist-200">Workflow</p>
                <p className="mt-3 text-lg leading-8 text-white/90">
                  Upload a package image, let OCR extract text, classify expiry, identify ingredients, and hear the result out loud.
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      <UploadZone file={file} onFileSelected={setFile} onClear={() => setFile(null)} />

      {result ? (
        <div className="space-y-6">
          <AnalysisCards result={result} />
          <div className="flex flex-wrap items-center gap-4">
            <VoicePlayer speechText={result.speech_text} audioUrl={result.audio_url} />
            <button className="big-button border border-slate-200 bg-white text-slate-900 hover:bg-slate-50" onClick={() => navigate('/result')}>
              View result page
            </button>
          </div>
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-3">
          <div className="glass-card p-6">
            <p className="text-lg font-semibold text-slate-900">1. Upload</p>
            <p className="mt-2 text-lg leading-8 text-slate-600">Drop a food label image or capture from the camera.</p>
          </div>
          <div className="glass-card p-6">
            <p className="text-lg font-semibold text-slate-900">2. Analyze</p>
            <p className="mt-2 text-lg leading-8 text-slate-600">Backend OCR finds expiry and ingredient clues from noisy text.</p>
          </div>
          <div className="glass-card p-6">
            <p className="text-lg font-semibold text-slate-900">3. Speak</p>
            <p className="mt-2 text-lg leading-8 text-slate-600">A readable voice summary helps elderly users hear the result.</p>
          </div>
        </div>
      )}
    </div>
  )
}
