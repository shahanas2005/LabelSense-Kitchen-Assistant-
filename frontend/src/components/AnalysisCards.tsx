import { AlertTriangle, BadgeCheck, Clock3, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import type { AnalysisResult } from '../types'

const iconMap: Record<string, JSX.Element> = {
  'Expired': <AlertTriangle className="h-6 w-6" />,
  'Near Expiry': <Clock3 className="h-6 w-6" />,
  'Safe': <BadgeCheck className="h-6 w-6" />,
  'Unknown': <Sparkles className="h-6 w-6" />,
}

type AnalysisCardsProps = {
  result: AnalysisResult | null
}

export function AnalysisCards({ result }: AnalysisCardsProps) {
  if (!result) {
    return null
  }

  const statusTone =
    result.expiry_status === 'Expired'
      ? 'border-rose-200 bg-rose-50 text-rose-700'
      : result.expiry_status === 'Near Expiry'
      ? 'border-amber-200 bg-amber-50 text-amber-700'
      : result.expiry_status === 'Safe'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
      : 'border-slate-200 bg-slate-50 text-slate-700'

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <motion.section className={`glass-card p-6 ${statusTone}`} initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-white/80 p-3">{iconMap[result.expiry_status] ?? iconMap.Unknown}</div>
          <div>
            <p className="label-text">Expiry status</p>
            <h3 className="text-2xl font-bold">{result.expiry_status}</h3>
          </div>
        </div>
        <div className="mt-5 space-y-2 text-lg font-medium text-slate-800">
          <p>Expiry date: {result.expiry_date ?? 'Not detected'}</p>
          <p>Confidence: {(result.confidence * 100).toFixed(0)}%</p>
        </div>
      </motion.section>
      <motion.section className="glass-card p-6" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
        <p className="label-text">Ingredients</p>
        <h3 className="mt-2 text-2xl font-bold text-slate-900">Detected list</h3>
        <div className="mt-4 flex flex-wrap gap-3">
          {result.ingredients.length ? result.ingredients.map((item) => (
            <span key={item} className="rounded-full bg-mist-100 px-4 py-2 text-base font-semibold text-mist-800">
              {item}
            </span>
          )) : <p className="text-lg text-slate-600">No clear ingredient block found.</p>}
        </div>
      </motion.section>
      <motion.section className="glass-card p-6" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <p className="label-text">Warnings</p>
        <h3 className="mt-2 text-2xl font-bold text-slate-900">Health alerts</h3>
        <div className="mt-4 space-y-3">
          {result.warnings.length ? result.warnings.map((warning, index) => {
            const severityColor = warning.severity === 'high' ? 'border-rose-200 bg-rose-50 text-rose-800' :
                                  warning.severity === 'medium' ? 'border-amber-200 bg-amber-50 text-amber-800' :
                                  'border-slate-200 bg-slate-50 text-slate-700'
            return (
              <div key={index} className={`rounded-2xl border px-4 py-3 text-lg font-semibold ${severityColor}`}>
                <p className="font-bold">{warning.warning}</p>
                <p className="text-sm mt-1">{warning.reason}</p>
                {warning.ingredient && <p className="text-sm mt-1">Ingredient: {warning.ingredient}</p>}
              </div>
            )
          }) : <p className="text-lg text-slate-600">No high-risk warning matched the current profile.</p>}
        </div>
      </motion.section>
      <motion.section className="glass-card p-6 lg:col-span-3" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
        <p className="label-text">Label details</p>
        <h3 className="mt-2 text-2xl font-bold text-slate-900">Manufacturing and weight fields</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {[
            { label: 'Expiry date', value: result.expiry_date ?? 'Not detected' },
            { label: 'Manufacturing date', value: result.manufacturing_date ?? 'Not detected' },
            { label: 'Net weight', value: result.net_weight ?? 'Not detected' },
          ].map((item) => (
            <div key={item.label} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">{item.label}</p>
              <p className="mt-2 text-xl font-bold text-slate-900">{item.value}</p>
            </div>
          ))}
        </div>
        {result.label_details?.length ? (
          <div className="mt-5 flex flex-wrap gap-3">
            {result.label_details.map((detail) => (
              <span key={`${detail.field}-${detail.value ?? 'unknown'}`} className="rounded-full bg-mist-100 px-4 py-2 text-base font-semibold text-mist-800">
                {detail.field.replace(/_/g, ' ')}: {detail.value ?? 'Not detected'}
              </span>
            ))}
          </div>
        ) : null}
      </motion.section>
    </div>
  )
}
