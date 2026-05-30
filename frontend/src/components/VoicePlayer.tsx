import { Volume2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { useState } from 'react'

type VoicePlayerProps = {
  speechText: string
  audioUrl?: string | null
}

export function VoicePlayer({ speechText, audioUrl }: VoicePlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/api\/?$/, '') ?? 'http://localhost:8000'

  const speak = () => {
    setIsPlaying(true)
    if (audioUrl) {
      const resolvedUrl = audioUrl.startsWith('http') ? audioUrl : `${apiBaseUrl}${audioUrl}`
      const audio = new Audio(resolvedUrl)
      audio.playbackRate = 1.12
      audio.onended = () => setIsPlaying(false)
      void audio.play()
      return
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(speechText)
      utterance.rate = 1.08
      utterance.pitch = 1.05
      utterance.onend = () => setIsPlaying(false)
      window.speechSynthesis.speak(utterance)
    }
  }

  return (
    <motion.button
      onClick={speak}
      className="bg-gradient-to-r from-purple-600 to-blue-600 text-white text-2xl font-bold py-6 px-12 rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center gap-4"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      animate={isPlaying ? { scale: [1, 1.1, 1] } : {}}
      transition={isPlaying ? { repeat: Infinity, duration: 1 } : {}}
      type="button"
    >
      <motion.div animate={isPlaying ? { rotate: [0, 10, -10, 0] } : {}} transition={{ repeat: Infinity, duration: 0.5 }}>
        <Volume2 className="h-8 w-8" />
      </motion.div>
      {isPlaying ? 'Playing summary...' : 'Play summary'}
    </motion.button>
  )
}
