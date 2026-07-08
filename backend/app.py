"""
Smart Voice Analyzer - Backend
--------------------------------
Pipeline:
  Audio file  -->  faster-whisper (speech-to-text, auto language detect)
              -->  Ollama local LLM (classifies text as Spam / Important / Normal)
              -->  JSON result returned to the frontend

Run with:
    uvicorn app:app --reload --port 8000

Requires Ollama running locally (https://ollama.com) with a model pulled, e.g.:
    ollama pull llama3.1
"""

import json
import os
import shutil
import tempfile
import traceback

import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "small")  # tiny/base/small/medium/large-v3
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")            # cpu or cuda
WHISPER_COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")

app = FastAPI(title="Smart Voice Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy-load whisper model (so the server starts fast, model loads on first use)
# ---------------------------------------------------------------------------
_whisper_model = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print(f"Loading faster-whisper model '{WHISPER_MODEL_SIZE}' ...")
        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        print("Whisper model loaded.")
    return _whisper_model


def transcribe_audio(file_path: str):
    """Transcribe an audio file. Auto-detects language (multilingual)."""
    model = get_whisper_model()
    segments, info = model.transcribe(file_path, beam_size=1, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip(), info.language


CLASSIFY_PROMPT = """You are a call/message triage assistant. You will be given the transcript
of a phone call or voice recording (it may be in any language). Classify it into exactly one
of these three categories:

- "Spam": scam calls, robocalls, telemarketing, fraud attempts, irrelevant junk.
- "Important": anything requiring action or attention (banking, work, family emergencies,
  appointments, deliveries, OTPs, official notices).
- "Normal": everyday, low-urgency conversation that isn't spam and doesn't need urgent action.

Respond with ONLY valid JSON, no extra text, no markdown, in this exact shape:
{{"category": "Spam" | "Important" | "Normal", "reason": "one short sentence explaining why", "summary": "one short sentence summarizing the call"}}

Transcript:
\"\"\"{transcript}\"\"\"
"""


def classify_text(transcript: str):
    """Call local Ollama model to classify the transcript."""
    prompt = CLASSIFY_PROMPT.format(transcript=transcript[:4000])
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("response", "").strip()

    # Be defensive: strip code fences if the model added them anyway
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {
            "category": "Normal",
            "reason": "Could not parse model output; defaulted to Normal.",
            "summary": raw[:200],
        }

    category = str(parsed.get("category", "Normal")).strip().capitalize()
    if category not in ("Spam", "Important", "Normal"):
        category = "Normal"

    action_map = {
        "Spam": "delete",
        "Important": "archive",
        "Normal": "keep",
    }

    return {
        "category": category,
        "reason": parsed.get("reason", ""),
        "summary": parsed.get("summary", ""),
        "suggested_action": action_map[category],
    }


@app.get("/health")
def health():
    """Quick check that the API, and optionally Ollama, are reachable."""
    ollama_ok = False
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
    except Exception:
        ollama_ok = False
    return {"status": "ok", "ollama_reachable": ollama_ok}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Accepts an audio file (call recording or any voice file), transcribes it
    (any language), classifies it, and returns the result as JSON.
    """
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        transcript, language = transcribe_audio(tmp_path)

        if not transcript:
            return JSONResponse(
                {
                    "filename": file.filename,
                    "language": language,
                    "transcript": "",
                    "category": "Normal",
                    "reason": "No speech detected in file.",
                    "summary": "",
                    "suggested_action": "keep",
                }
            )

        result = classify_text(transcript)

        return JSONResponse(
            {
                "filename": file.filename,
                "language": language,
                "transcript": transcript,
                **result,
            }
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            {"error": str(e)},
            status_code=500,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

# Serve the frontend (index.html + any assets) at the root URL.
# This must come after all API routes so /health and /analyze still work.
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
