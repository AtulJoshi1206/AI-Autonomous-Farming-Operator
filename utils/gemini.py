import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DEFAULT_MODEL = "gemini-2.5-flash-lite"

def generate_farmer_explanation(context, target_lang="English"):
    if not GEMINI_API_KEY:
        return {"explanation_en": "Conditions are safe to proceed.", "explanation_local": "", "explanation_phonetic": ""}
        
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(DEFAULT_MODEL)
    
    prompt = f"""
    Context:
    Crop: {context.get('crop')}
    Task: {context.get('task')}
    Location: {context.get('location')}
    Conditions: {context.get('rain_prob')}% Rain probability, {context.get('humidity')}% Humidity, {context.get('temperature')}°C
    System Status: {context.get('guardrail_status')}
    System Reason: {context.get('reason')}

    Role: Expert Agricultural Advisor.
    Explain the system's decision simply to a farmer.
    Keep it under 3 sentences. Focus on 'Why'.
    Tell them if they should proceed or wait.
    IMPORTANT: If the System Status is 'blocked', your explanation MUST begin exactly with: "Guardrails have stopped me from doing this task." and then explain why in the remaining sentences.
    
    You must output ONLY a JSON object containing the explanation in English, and translated to {target_lang}.
    {{
        "explanation_en": "The english explanation",
        "explanation_local": "The explanation translated into the native script of {target_lang}",
        "explanation_phonetic": "The same translated {target_lang} explanation written in Roman/English characters suitable for TTS (or english if english)"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text_content = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text_content)
    except Exception as e:
        print(f"Farmer Explanation Error: {e}")
        if context.get('guardrail_status') in ['blocked', 'need_more_data']:
            reason = context.get('reason', 'Safety policy enforced.')
            msg = f"Guardrails have stopped me from doing this task. {reason}"
            return {"explanation_en": msg, "explanation_local": msg, "explanation_phonetic": msg}
            
        return {"explanation_en": "It is currently safe to proceed.", "explanation_local": "It is safe.", "explanation_phonetic": "It is safe"}

def generate_what_if(context):
    if not GEMINI_API_KEY:
        return {
            "risk_en": "High risk predicted.",
            "impact_en": "Minor impact on yield."
        }
        
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(DEFAULT_MODEL)
    
    prompt = f"""
    Scenario: {context.get('reason')}
    Action: {context.get('action')}
    Crop: {context.get('crop')}
    Rain: {context.get('rain_prob')}%
    
    Predict 'risk' and 'yield impact' of this scenario.
    Return JSON only:
    {{
      "risk_en": "Description risk",
      "impact_en": "Description yield impact"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text.replace("```json", "").replace("```", "")
        return json.loads(content.strip())
    except:
        return {
            "risk_en": "Weather conditions might interfere with optimal resource uptake.",
            "impact_en": "Minor impact on yield predicted."
        }

def analyze_crop_conditions(input_data):
    """
    Dynamic Knowledge Base Agent using Gemini to evaluate ANY crop globally, 
    accounting for current season, temperature, soil, and rain rules.
    """
    if not GEMINI_API_KEY:
        return None
        
    genai.configure(api_key=GEMINI_API_KEY)
    
    # We use a system instruction to strictly shape JSON response
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an expert Agronomist AI assessing a farming task. You have infinite knowledge about all crops.
    
    Input:
    - Crop: {input_data.get('crop')}
    - Task: {input_data.get('task')}
    - Location: {input_data.get('location', 'Unknown')}
    - Weather: {input_data.get('temperature', 25)}°C, Humidity: {input_data.get('humidity', 50)}%, Rain Prob: {input_data.get('rain_prob', 0)}%
    
    CRITICAL RULE:
    If the 'Crop', 'Task', or 'Location' is undefined, missing, vague, or unrecognized (e.g., meaningless words or 'unknown'):
    - You MUST NOT evaluate temperature or season.
    - Set guardrail "status" strictly to "blocked".
    - Set guardrail "reason" to EXACTLY state what core data is missing and that the pipeline is halted.

    EVALUATE (Only if Crop, Task, and Location are clear and recognized):
    1. Is the current temperature and assumed season suitable for this crop in this location?
    2. Does it tolerate the provided rain probability for this specific task?
    3. Is the soil type appropriate?
    
    Construct your response strictly as JSON:
    {{
      "decision": {{
        "risk_aware_action": "Clear directive, e.g., 'Delay planting due to high temp' or 'Proceed with fertilization'",
        "reasoning": "Detailed explanation mentioning season suitablity, temp, and rain.",
        "confidence": "High" (or Medium/Low)
      }},
      "guardrail": {{
        "status": "approved" (ONLY if it is currently safe, the correct season, and right time to proceed. Output "blocked" if the task should be delayed, stopped, or if conditions are unsuitable.),
        "reason": "Clear safety reason if blocked, or approval confirmation."
      }}
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text_content = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text_content)
    except Exception as e:
        print(f"Dynamic Crop Analysis Error: {e}")
        return None
