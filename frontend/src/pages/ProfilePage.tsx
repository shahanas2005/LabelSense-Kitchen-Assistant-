import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ProfilePanel } from '../components/ProfilePanel'
import { getHistory, saveProfile } from '../services/api'
import type { HistoryItem, Profile } from '../types'

type ProfilePageProps = {
  profile: Profile
  setProfile: (profile: Profile) => void
}

export function ProfilePage({ profile, setProfile }: ProfilePageProps) {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getHistory(profile.user_id).then(setHistory).catch(() => setHistory([]))
  }, [profile.user_id])

  const handleSave = async (nextProfile: Profile) => {
    setLoading(true)
    try {
      const saved = await saveProfile(nextProfile)
      setProfile({
        user_id: saved.user_id,
        email: saved.email ?? null,
        display_name: saved.display_name ?? null,
        age_group: saved.age_group,
        conditions: saved.conditions,
        allergies: saved.allergies,
        diet: saved.diet,
        language: saved.language,
        notes: saved.notes,
      })
      localStorage.setItem('profile', JSON.stringify({
        user_id: saved.user_id,
        email: saved.email ?? null,
        display_name: saved.display_name ?? null,
        age_group: saved.age_group,
        conditions: saved.conditions,
        allergies: saved.allergies,
        diet: saved.diet,
        language: saved.language,
        notes: saved.notes,
      }))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-100">
      <div className="mx-auto max-w-6xl px-4 py-12">
        <motion.div className="text-center mb-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-5xl font-black text-slate-900 mb-4">Health Profile</h1>
          <p className="text-2xl text-slate-600">Customize your preferences</p>
        </motion.div>

        <div className="grid gap-12 xl:grid-cols-[1.5fr_1fr]">
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
            <ProfilePanel initialProfile={profile} onSave={handleSave} loading={loading} />
          </motion.div>

          <motion.aside className="bg-white rounded-2xl shadow-xl p-8" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
            <h2 className="text-3xl font-bold text-slate-900 mb-6">Recent Scans</h2>
            <div className="space-y-6">
              {history.length ? history.map((item) => (
                <motion.div key={item.id} className="bg-gray-50 rounded-xl p-6 shadow-md" whileHover={{ scale: 1.02 }}>
                  <p className="text-2xl font-bold text-slate-900">{item.expiry_status}</p>
                  <p className="text-xl text-slate-600 mt-2">Expiry: {item.expiry_date ?? 'Not found'}</p>
                  <p className="text-lg text-slate-600 mt-2">Warnings: {item.warnings.length ? item.warnings.map(w => w.warning).join(', ') : 'None'}</p>
                </motion.div>
              )) : <p className="text-xl text-slate-600">No scan history yet.</p>}
            </div>
          </motion.aside>
        </div>
      </div>
    </div>
  )
}
