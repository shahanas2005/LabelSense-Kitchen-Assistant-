import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnalysisCards } from '../components/AnalysisCards'
import { VoicePlayer } from '../components/VoicePlayer'
import type { AnalysisResult } from '../types'

export function ResultPage() {
  const navigate = useNavigate()
  const [result, setResult] = useState<AnalysisResult | null>(null)

  useEffect(() => {
    const stored = sessionStorage.getItem('last-analysis')
    if (stored) {
      setResult(JSON.parse(stored) as AnalysisResult)
    }
  }, [])

  if (!result) {
    return (
      <div className="glass-card space-y-4 p-8 text-center">
        <h2 className="text-3xl font-bold text-slate-900">No analysis found</h2>
        <p className="text-lg text-slate-600">Upload an image from the home page to generate a result first.</p>
        <button className="big-button bg-slate-900 text-white hover:bg-slate-800" onClick={() => navigate('/')}>Go home</button>
      </div>
    )
  }

  return (
    <motion.div className="space-y-8" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <section className="glass-card p-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="label-text">Analysis result</p>
            <h1 className="mt-2 text-4xl font-black text-slate-950">Your package scan summary</h1>
          </div>
          <VoicePlayer speechText={result.speech_text} audioUrl={result.audio_url} />
        </div>
      </section>
      <AnalysisCards result={result} />
      <section className="glass-card p-8">
        <p className="label-text">Raw OCR text</p>
        <pre className="mt-4 whitespace-pre-wrap rounded-3xl bg-slate-950 p-6 text-lg leading-8 text-slate-100">{result.raw_text || 'No OCR text returned.'}</pre>
      </section>
    </motion.div>
  )
}
