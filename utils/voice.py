import edge_tts
import base64
import os
import uuid

VOICE_MAP = {
    "hindi": "hi-IN-SwaraNeural",
    "marathi": "mr-IN-AarohiNeural",
    "gujarati": "gu-IN-DhwaniNeural",
    "punjabi": "pa-IN-KashviNeural",
    "english": "en-IN-NeerjaNeural"
}

async def generate_speech_base64(text: str, language: str) -> str:
    """
    Generates high-quality TTS audio using Edge TTS (Azure Neural voices) without needing an API key.
    Returns the Audio as a Base64 string.
    """
    if not text:
        return None

    lang_key = language.lower() if language else "hindi"
    voice = VOICE_MAP.get(lang_key, "hi-IN-SwaraNeural")
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        
        temp_file = f"temp_{uuid.uuid4()}.mp3"
        await communicate.save(temp_file)
        
        with open(temp_file, "rb") as f:
            audio_data = f.read()
        
        os.remove(temp_file)
        
        return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
