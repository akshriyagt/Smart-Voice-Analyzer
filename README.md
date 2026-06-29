# 🎙️ Smart Voice Analyzer v3.0

AI-powered call recording classifier. Works on **all Android phones** via browser — no USB, no app store needed.

## ✨ What's New in v3.0
- 🔐 **Sign In / Sign Up** — each user sees only their own records
- ✅ **Permission before action** — app asks "Delete? Keep? Archive?" before doing anything
- 📁 **3 separate storage folders** — spam_files/, notspam_files/, normal_files/
- 📱 **PWA (Install on Android)** — open in Chrome → "Add to Home Screen"
- 🌐 **8 languages** — English, Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Bengali
- 📊 **5 tabs** — All, Spam, Not Spam, Normal, Pending (needs your decision)
- 🤖 **AI suggests action** — you still confirm every delete/keep/archive

## 🚀 Quick Start

### 1. Install requirements
```bash
pip install -r requirements.txt
```

### 2. Install Ollama (AI engine)
Download from https://ollama.ai then run:
```bash
ollama pull llama3.2:1b
```

### 3. (Optional) Install Whisper for transcription
```bash
pip install openai-whisper
```

### 4. Start the app
**Linux/Mac:**
```bash
chmod +x start.sh && ./start.sh
```
**Windows:**
```
start.bat
```

### 5. Open in browser
- **Computer:** http://localhost:8000
- **Android phone on same WiFi:** http://YOUR-COMPUTER-IP:8000

### 6. Install on Android (no USB!)
1. Open Chrome on your Android phone
2. Go to http://YOUR-COMPUTER-IP:8000
3. Tap the 3-dot menu → "Add to Home Screen"
4. The app installs like a native app!

## 📂 File Organization
- `spam_files/` — spam recordings waiting for your decision
- `notspam_files/` — important calls waiting for your decision  
- `normal_files/` — normal calls waiting for your decision
- `archive/` — calls you chose to archive
- `uploads/` — temporary processing folder

## 🌐 Languages Supported
English • Hindi • Tamil • Telugu • Kannada • Malayalam • Marathi • Bengali
