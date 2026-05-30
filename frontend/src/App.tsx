import { useEffect, useState } from 'react'
import { NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import { Home, UserRound, History } from 'lucide-react'
import { HomePage } from './pages/HomePage'
import { ProfilePage } from './pages/ProfilePage'
import { ResultPage } from './pages/ResultPage'
import type { Profile } from './types'

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

export default function App() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<Profile>(DEFAULT_PROFILE)

  useEffect(() => {
    const stored = localStorage.getItem('profile')
    if (stored) {
      setProfile(JSON.parse(stored) as Profile)
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('profile', JSON.stringify(profile))
  }, [profile])

  return (
    <div className="min-h-screen bg-soft-radial">
      <header className="sticky top-0 z-20 border-b border-white/60 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <button onClick={() => navigate('/')} className="text-left">
            <p className="text-sm font-bold uppercase tracking-[0.3em] text-mist-700">LabelSense</p>
            <p className="text-lg font-semibold text-slate-900">Intelligent label analysis</p>
          </button>
          <nav className="flex items-center gap-2 rounded-full border border-slate-200 bg-white p-2 shadow-sm">
            <NavLink to="/" className={({ isActive }) => `flex items-center gap-2 rounded-full px-4 py-3 text-lg font-semibold ${isActive ? 'bg-mist-100 text-mist-800' : 'text-slate-600'}`}>
              <Home className="h-5 w-5" /> Home
            </NavLink>
            <NavLink to="/profile" className={({ isActive }) => `flex items-center gap-2 rounded-full px-4 py-3 text-lg font-semibold ${isActive ? 'bg-mist-100 text-mist-800' : 'text-slate-600'}`}>
              <UserRound className="h-5 w-5" /> Profile
            </NavLink>
            <NavLink to="/result" className={({ isActive }) => `flex items-center gap-2 rounded-full px-4 py-3 text-lg font-semibold ${isActive ? 'bg-mist-100 text-mist-800' : 'text-slate-600'}`}>
              <History className="h-5 w-5" /> Result
            </NavLink>
            <NavLink to="/about" className={({ isActive }) => `flex items-center gap-2 rounded-full px-4 py-3 text-lg font-semibold ${isActive ? 'bg-mist-100 text-mist-800' : 'text-slate-600'}`}>
              <span className="h-5 w-5 flex items-center justify-center rounded-full bg-slate-100 text-slate-600">?</span> About
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<HomePage profile={profile} onProfileJump={() => navigate('/profile')} />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/profile" element={<ProfilePage profile={profile} setProfile={setProfile} />} />
          <Route path="/about" element={
            <div className="mx-auto max-w-3xl rounded-3xl border border-slate-200 bg-white/80 p-8 shadow-sm backdrop-blur-sm">
              <h1 className="text-4xl font-bold tracking-tight text-slate-900">About LabelSense</h1>
              <p className="mt-4 text-lg leading-8 text-slate-600">
                LabelSense is designed for older adults whose eyesight makes reading small product labels difficult. The app lets a user capture a package label image, converts the text using OCR, and reads the key information aloud in a clear, easy-to-hear voice.
              </p>
              <div className="mt-6 space-y-4 text-slate-700">
                <p>
                  It is built to make label scanning simple: large controls, clear instructions, voice playback, and personalized warnings based on health preferences. This reduces the need to strain when reading tiny text on food packaging.
                </p>
                <p>
                  LabelSense is especially helpful for people with low vision, limited mobility, or those who want a faster way to understand expiry dates, ingredients, and allergens without reading a full label manually.
                </p>
              </div>
            </div>
          } />
        </Routes>
      </main>
      <footer className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 text-center text-sm text-slate-500">
        © 2026 LabelSense • Created by Shah Anas Khan • <a className="underline" href="https://github.com/shahanas2005">GitHub</a> • <a className="underline" href="https://www.linkedin.com/in/shah-anas-khan/">LinkedIn</a>
      </footer>
    </div>
  )
}
