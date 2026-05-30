# LabelSense

LabelSense is a web application for analyzing product labels from uploaded images. It uses OCR and rule-based detection to identify expiry information, manufacturing dates, ingredients, warnings, and net weight, then presents the results in a simple interface with optional voice playback.

## Overview

The project is designed to make label reading faster and more accessible, especially for users who want a clearer summary of a package without reading small print manually.

## Features

- Image upload and camera capture for label scanning
- OCR-based text extraction from product images
- Expiry and manufacturing date detection with common label aliases
- Net weight detection from a range of label formats
- Ingredient extraction and health-warning analysis
- Personalized warnings based on stored user profile details
- Voice playback for spoken summaries
- Accessible UI with large text and high-contrast cards

## How It Works

1. A user uploads or captures a product label image.
2. The backend preprocesses the image and runs OCR.
3. The extracted text is analyzed for expiry, manufacturing, and weight fields.
4. Ingredient rules and profile-based rules generate warnings.
5. The frontend displays the result and can read the summary aloud.

## Project Structure

```
backend/
  app/
    api/
    core/
    db/
    services/
  data/
frontend/
  src/
    components/
    pages/
    services/
    styles/
run.bat
```

## Requirements

- Python 3.11+
- Node.js 18+
- npm

## Local Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### One-step launch

You can also start both apps with:

```bash
run.bat
```

Then open:

```text
http://localhost:5173
```

## Configuration

The backend reads its settings from `backend/.env`. Common values include:

- `DATABASE_URL`
- `APP_NAME`
- CORS origins for the frontend

## API Endpoints

- `POST /api/analyze` - Analyze a label image
- `POST /api/profile` - Create or update a user profile
- `GET /api/history` - Fetch past analyses
- `GET /api/audio/{filename}` - Retrieve generated voice output

## Technology Stack

- Backend: FastAPI, SQLAlchemy, SQLite or PostgreSQL
- OCR: RapidOCR with pytesseract fallback
- Image preprocessing: OpenCV and Pillow
- Frontend: React, TypeScript, Vite, Tailwind CSS

## Notes

- The app is optimized for label photos, but accuracy still depends on lighting, focus, and print quality.
- Voice output is generated as a summary to keep playback concise.
- The backend stores uploaded images, audio, and analysis history locally by default.

## Vercel Deployment

This repository is set up to deploy the frontend on Vercel.

Use these settings when creating the Vercel project from GitHub:

- Framework preset: `Vite`
- Build command: `cd frontend && npm run build`
- Output directory: `frontend/dist`
- Install command: `cd frontend && npm install`

Set this environment variable in Vercel:

- `VITE_API_BASE_URL` = the public URL of your backend API, for example `https://your-backend-domain.com/api`

Important:

- The FastAPI backend is not meant to run on Vercel as-is because it depends on OCR and TTS packages that fit better on a normal Python host.
- Deploy the backend separately on a Python-friendly host such as Render, Railway, or any server that supports the required native libraries.
- The frontend will call that backend through `VITE_API_BASE_URL`.

## License and Ownership

© 2026 LabelSense. Created by Shah Anas Khan.

- GitHub: https://github.com/shahanas2005
- LinkedIn: https://www.linkedin.com/in/shah-anas-khan/
