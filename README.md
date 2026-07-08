# Smart Voice Analyzer

Pick a file, a folder, or record a call → it gets transcribed (any language)
and classified as **Spam / Important / Normal** → you get a popup with the
suggested action (Delete / Archive / Keep).

```
Web Browser  <---->  API (FastAPI)  <---->  Ollama (local LLM)
                         |
                    faster-whisper
                (speech-to-text, multilingual)
```

---

## 1. Run it on localhost (do this first)

### Step 1 — Install Ollama and pull a model
Download Ollama from https://ollama.com and install it, then in a terminal:

```bash
ollama pull llama3.1
ollama serve
```
(On Mac/Windows, `ollama serve` usually starts automatically after install —
just make sure the Ollama app is running.)

### Step 2 — Set up the backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

The first time you analyze a file, it will download the Whisper model
(`small` by default — good accuracy/speed balance, ~500MB). You can change
the size in `app.py` (`WHISPER_MODEL_SIZE`): `tiny` (fastest), `base`,
`small`, `medium`, `large-v3` (most accurate, slower).

Check it's alive: open http://localhost:8000/health — you should see
`{"status": "ok", "ollama_reachable": true}`.

### Step 3 — Open the frontend
Just open `frontend/index.html` directly in your browser (double-click it,
or `open frontend/index.html` / `start frontend/index.html`).

No build step needed — it's a single static HTML file that talks to
`http://localhost:8000`.

### Step 4 — Try it
- **Pick Files** — choose one or more audio files (mp3, wav, m4a, ogg, etc.)
- **Pick Folder** — choose a whole folder of recordings
- **Record Call** — records straight from your mic, right in the browser
  (handy for testing without needing real call recordings yet)
- Hit **Analyze** — each file gets transcribed and classified
- Click a result card to see the transcript and confirm the suggested action

---

## 2. Moving to a real app

Once this works on localhost, there are two realistic paths depending on
what you actually need:

### Option A — Keep the same backend, wrap it as a mobile app
The backend (`/analyze` endpoint) doesn't change. You build a thin mobile
front end (Flutter or React Native) that:
1. Reads real call recordings from the phone's storage (Android exposes a
   call-recording folder on many OEMs; iOS does **not** allow apps to access
   call recordings — this is an Apple platform restriction, not something
   code can work around).
2. Sends the audio file to the same `/analyze` API (same JSON contract as
   the web version).
3. Shows the same Spam/Important/Normal result and Delete/Archive/Keep
   popup, but calls real OS APIs to actually delete/archive the file.

This is why **Android is realistically the first mobile target** — call
recording access on iOS is restricted at the OS level for any app, not just
this one.

### Option B — Host the backend so it's not just "localhost"
Right now `OLLAMA_URL` points at `http://localhost:11434`, which only works
if Ollama runs on the same machine as the API. To let a real phone talk to
it over the internet, you'd either:
- Run the backend + Ollama on a small server/VPS you control (Ollama can run
  on CPU, but a GPU box will be much faster for whisper + LLM), or
- Swap Ollama for a hosted LLM API (e.g. Anthropic's Claude API) for the
  classification step, and keep whisper (or a hosted transcription API) for
  speech-to-text.

Either way, the only change needed is the API's `OLLAMA_URL` (or swapping
`classify_text()` for a hosted-API call) — the rest of the pipeline and the
JSON contract stay the same, so the frontend/mobile app doesn't need to
change.

---

## Files in this project

```
smart-voice-analyzer/
├── backend/
│   ├── app.py            FastAPI server: transcribe + classify
│   └── requirements.txt
├── frontend/
│   └── index.html        Single-file web UI (matches your sketch)
└── README.md              this file
```

## Notes
- All languages: faster-whisper auto-detects the spoken language, so calls
  in any language get transcribed and then classified.
- The classification prompt (in `app.py`, `CLASSIFY_PROMPT`) is the easiest
  place to tune what counts as Spam vs Important vs Normal for your case —
  edit the wording there and restart the server.
- The **Delete/Archive/Keep** buttons in the popup currently confirm the
  action in the UI only. Actually deleting/archiving a file requires
  filesystem or OS-level access, which is why this needs a real mobile app
  (Option A above) once you're past local testing.
