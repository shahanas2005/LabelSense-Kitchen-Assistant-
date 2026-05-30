import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import type { Profile } from '../types'

const DEFAULT_PROFILE: Profile = {
  user_id: null,
  email: '',
  display_name: '',
  age_group: null,
  conditions: [],
  allergies: [],
  diet: [],
  language: 'en',
  notes: '',
}

type ProfilePanelProps = {
  initialProfile?: Profile
  onSave: (profile: Profile) => Promise<void>
  loading?: boolean
}

export function ProfilePanel({ initialProfile, onSave, loading }: ProfilePanelProps) {
  const [profile, setProfile] = useState<Profile>(initialProfile ?? DEFAULT_PROFILE)
  const [allergyInput, setAllergyInput] = useState((initialProfile?.allergies ?? []).join(', '))
  const [conditionInput, setConditionInput] = useState((initialProfile?.conditions ?? []).join(', '))
  const [dietInput, setDietInput] = useState((initialProfile?.diet ?? []).join(', '))

  useEffect(() => {
    if (initialProfile) {
      setProfile(initialProfile)
      setAllergyInput(initialProfile.allergies.join(', '))
      setConditionInput(initialProfile.conditions.join(', '))
      setDietInput(initialProfile.diet.join(', '))
    }
  }, [initialProfile])

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await onSave({
      ...profile,
      email: profile.email?.trim() ? profile.email.trim() : null,
      display_name: profile.display_name?.trim() ? profile.display_name.trim() : null,
      conditions: conditionInput.split(',').map((item) => item.trim()).filter(Boolean),
      allergies: allergyInput.split(',').map((item) => item.trim()).filter(Boolean),
      diet: dietInput.split(',').map((item) => item.trim()).filter(Boolean),
    })
  }

  return (
    <motion.form className="bg-white rounded-2xl shadow-xl p-10 space-y-8" onSubmit={submit} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div>
        <h2 className="text-4xl font-black text-slate-900 mb-2">Health Preferences</h2>
        <p className="text-xl text-slate-600">Set your profile for personalized warnings</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <label className="space-y-3">
          <span className="text-2xl font-semibold text-slate-800">Display Name</span>
          <input className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={profile.display_name ?? ''} onChange={(event) => setProfile({ ...profile, display_name: event.target.value })} />
        </label>
        <label className="space-y-3">
          <span className="text-2xl font-semibold text-slate-800">Email</span>
          <input className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" type="email" value={profile.email ?? ''} onChange={(event) => setProfile({ ...profile, email: event.target.value })} />
        </label>
        <label className="space-y-3">
          <span className="text-2xl font-semibold text-slate-800">Age Group</span>
          <select className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={profile.age_group ?? ''} onChange={(event) => setProfile({ ...profile, age_group: event.target.value as 'elderly' | 'adult' | null })}>
            <option value="">Select age group</option>
            <option value="adult">Adult</option>
            <option value="elderly">Elderly</option>
          </select>
        </label>
        <label className="space-y-3">
          <span className="text-2xl font-semibold text-slate-800">Language</span>
          <select className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={profile.language} onChange={(event) => setProfile({ ...profile, language: event.target.value as 'en' | 'ur' })}>
            <option value="en">English</option>
            <option value="ur">Urdu</option>
          </select>
        </label>
      </div>

      <label className="space-y-3 block">
        <span className="text-2xl font-semibold text-slate-800">Conditions</span>
        <input className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={conditionInput} onChange={(event) => setConditionInput(event.target.value)} placeholder="diabetes, hypertension" />
      </label>

      <label className="space-y-3 block">
        <span className="text-2xl font-semibold text-slate-800">Allergies</span>
        <input className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={allergyInput} onChange={(event) => setAllergyInput(event.target.value)} placeholder="nuts, lactose, gluten" />
      </label>

      <label className="space-y-3 block">
        <span className="text-2xl font-semibold text-slate-800">Diet Preferences</span>
        <input className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" value={dietInput} onChange={(event) => setDietInput(event.target.value)} placeholder="low_sugar, vegan" />
      </label>

      <label className="space-y-3 block">
        <span className="text-2xl font-semibold text-slate-800">Notes</span>
        <textarea className="w-full text-xl p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-32 resize-y" value={profile.notes ?? ''} onChange={(event) => setProfile({ ...profile, notes: event.target.value })} placeholder="Optional user notes" />
      </label>

      <button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white text-2xl font-bold py-6 rounded-xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300" disabled={loading}>
        {loading ? 'Saving...' : 'Save Profile'}
      </button>
    </motion.form>
  )
}
