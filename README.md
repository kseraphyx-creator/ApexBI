# APEX Intelligence v5.0 — Backend Setup Guide
**Founders: Khushi Choudhary & Kartik Baliyan**

> Complete step-by-step instructions. Follow in order. Do not skip any step.

---

## WHAT YOU WILL SET UP

Your Phone / Browser → index.html (Frontend) → app.py (Backend) → Firebase (Database) → Anthropic (AI)

---

## YOUR FILE STRUCTURE

ApexBI/
├── backend/
│   ├── app.py
│   ├── firebase-credentials.json
│   ├── .env
│   └── Procfile
├── frontend/
│   ├── index.html
│   └── firebase.js
├── requirements.txt
├── runtime.txt
├── .gitignore
└── README.md

---

## STEP 1 — Install Python
1. Go to https://python.org/downloads
2. Download Python 3.11
3. CHECK the box "Add Python to PATH" during install
4. Test: open CMD and type: python --version

---

## STEP 2 — Set Up Firebase
1. Go to https://console.firebase.google.com
2. Open your project apexbi-8bf8c
3. Click Firestore Database → Create database → Test mode → asia-south1
4. Gear icon → Project Settings → Service Accounts → Generate new private key
5. Rename downloaded file to: firebase-credentials.json
6. Move it into your backend/ folder

---

## STEP 3 — Get Anthropic API Key
1. Go to https://console.anthropic.com
2. API Keys → Create Key → name it "APEX Backend"
3. Copy the key starting with sk-ant-...

---

## STEP 4 — Create .env File
Create a file named .env inside backend/ folder. Paste this:

ANTHROPIC_API_KEY=sk-ant-PASTE_YOUR_KEY_HERE
JWT_SECRET_KEY=apexbi2025kiranaindiasecretkey123456
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_PROJECT_ID=apexbi-8bf8c
FLASK_ENV=development

---

## STEP 5 — Install Python Packages
Open CMD in your project folder:

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r ../requirements.txt

---

## STEP 6 — Run the Backend
python app.py

Test at: http://localhost:5000/api/health
You should see: APEX backend is running

---

## STEP 7 — Test the Frontend
Open frontend/index.html in Chrome
Try signing up → if it works, Firebase is connected
Try AI chat → if it works, Anthropic is connected

---

## STEP 8 — Push to GitHub
git init
git add .
git commit -m "APEX Intelligence v5.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/apex-intelligence.git
git push -u origin main

---

## STEP 9 — Deploy on Render.com (Free)
1. Go to https://render.com
2. New + → Web Service → connect GitHub repo
3. Build Command: pip install -r requirements.txt
4. Start Command: gunicorn app:app
5. Add environment variables from your .env file
6. Deploy → get your live URL like https://apex-backend.onrender.com
7. Update API_URL in index.html to your live URL

---

## STEP 10 — Host Frontend on GitHub Pages
GitHub repo → Settings → Pages → Branch: main → Save
Live at: https://YOUR_USERNAME.github.io/apex-intelligence/

---

## TROUBLESHOOTING

ModuleNotFoundError → pip install -r requirements.txt
Firebase connection failed → check firebase-credentials.json is in backend/
Invalid API key → check .env file
CORS error → make sure backend is running on port 5000
venv activate fails → try venv\Scripts\activate.bat

---

## API ROUTES

GET  /api/health       → check server (no auth)
POST /api/auth/signup  → create account (no auth)
POST /api/auth/login   → login (no auth)
GET  /api/data         → load shop data (JWT needed)
POST /api/data         → save shop data (JWT needed)
POST /api/ai/chat      → ask AI (JWT needed)

---

Built with love by Khushi Choudhary & Kartik Baliyan
APEX Intelligence v5.0 — India's AI for Kirana & Retail Shops