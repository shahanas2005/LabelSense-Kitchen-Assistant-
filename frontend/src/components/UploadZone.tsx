import { useState } from 'react'
import { Camera, Upload, ScanText } from 'lucide-react'
import { motion } from 'framer-motion'

type UploadZoneProps = {
  file: File | null
  onFileSelected: (file: File) => void
  onClear: () => void
}

export function UploadZone({ file, onFileSelected, onClear }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0]
    if (selected) {
      onFileSelected(selected)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    const droppedFile = event.dataTransfer.files?.[0]
    if (droppedFile) {
      onFileSelected(droppedFile)
    }
  }

  return (
    <motion.div
      className={`glass-card border-dashed p-6 transition ${isDragging ? 'border-mist-500 bg-mist-50 ring-4 ring-mist-200' : 'border-mist-200'}`}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      onDragOver={(event) => {
        event.preventDefault()
        setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className="rounded-2xl bg-mist-100 p-3 text-mist-700">
              <ScanText className="h-6 w-6" />
            </span>
            <div>
              <p className="label-text">Upload or capture</p>
              <h2 className="text-2xl font-bold text-slate-900">Scan a food package image</h2>
            </div>
          </div>
          <p className="max-w-2xl text-lg leading-8 text-slate-600">
            Drag an image here, browse from your device, or use the camera on mobile to capture a label.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <label className="big-button cursor-pointer bg-slate-900 text-white hover:bg-slate-800">
            <Upload className="h-5 w-5" />
            Browse Files
            <input className="hidden" type="file" accept="image/*" onChange={handleChange} />
          </label>
          <label className="big-button cursor-pointer border border-slate-200 bg-white text-slate-900 hover:bg-slate-50">
            <Camera className="h-5 w-5" />
            Camera Capture
            <input className="hidden" type="file" accept="image/*" capture="environment" onChange={handleChange} />
          </label>
        </div>
      </div>
      <div className="mt-6 rounded-3xl border-2 border-dashed border-mist-200 bg-mist-50/70 p-6 text-center">
        {file ? (
          <div className="space-y-4">
            <p className="text-xl font-semibold text-slate-900">Selected file: {file.name}</p>
            <p className="text-base text-slate-600">{Math.round(file.size / 1024)} KB</p>
            <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-900 shadow-sm ring-1 ring-slate-200" onClick={onClear}>
              Remove file
            </button>
          </div>
        ) : (
          <div className="space-y-3 py-8">
            <p className="text-2xl font-bold text-slate-900">Drop image here</p>
            <p className="text-lg text-slate-600">Simple controls and clear text make scanning easy.</p>
            <p className="text-base text-slate-500">Drag and drop on desktop. Capture images on mobile.</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}
