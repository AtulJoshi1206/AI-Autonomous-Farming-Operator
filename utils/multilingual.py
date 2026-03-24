import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def configure_gemini():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in .env")
    genai.configure(api_key=GEMINI_API_KEY)

# Use gemini-2.5-flash-lite for higher quota/availability
DEFAULT_MODEL = "gemini-2.5-flash-lite"

def detect_and_translate(text: str) -> dict:
    configure_gemini()
    model = genai.GenerativeModel(DEFAULT_MODEL)
    
    prompt = f"""Analyze text: "{text}"
    Detect language (one of: Hindi, Marathi, Gujarati, Punjabi, English).
    Extract 'task', 'crop', 'location'.
    
    Return JSON only:
    {{
      "original_text": "{text}",
      "detected_language": "Detected language",
      "task": "...",
      "crop": "...",
      "location": "...",
      "is_missing_data": boolean,
      "missing_message_local": "Request in original script",
      "missing_message_phonetic": "The same request in ROMANIZED script (English characters) for TTS"
    }}"""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(content.strip())
    except Exception as e:
        print(f"Extraction Error: {e}")
        return {"detected_language": "English", "is_missing_data": False}

def transcribe_audio(audio_path: str) -> dict:
    configure_gemini()
    model = genai.GenerativeModel(DEFAULT_MODEL)
    try:
        audio_file = genai.upload_file(path=audio_path)
        prompt = """Transcribe, detect language, extract 'task', 'crop', 'location'.
        Return JSON only:
        {
          "original_text": "...",
          "detected_language": "Detected language",
          "task": "...",
          "crop": "...",
          "location": "...",
          "is_missing_data": boolean,
          "missing_message_local": "Request in original script",
          "missing_message_phonetic": "The same request in ROMANIZED script (English characters) for TTS"
        }"""
        response = model.generate_content([prompt, audio_file])
        content = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(content.strip())
    except:
        return {"detected_language": "English", "is_missing_data": False}

def translate_output(text: str, target_lang: str) -> dict:
    if not target_lang or target_lang.lower() == "english":
        return {"local": text, "phonetic": text}
        
    configure_gemini()
    model = genai.GenerativeModel(DEFAULT_MODEL)
    prompt = f"""Translate farming advice to {target_lang}.
    'local': native script
    'phonetic': ROMANIZED script (English characters)
    Text: "{text}"
    Return JSON only:
    {{ "local": "...", "phonetic": "..." }}"""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.replace("```json", "").replace("```", "")
        return json.loads(content.strip())
    except:
        return {"local": text, "phonetic": text}
