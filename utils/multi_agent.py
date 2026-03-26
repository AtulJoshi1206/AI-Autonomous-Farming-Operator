import os
import json
import asyncio
from .multilingual import detect_and_translate, transcribe_audio, translate_output
from .weather import get_weather, get_forecast
from .gemini import generate_farmer_explanation
from main import run_pipeline

class FarmingMultiAgentSystem:
    """
    Enhanced Multi-Agent Orchestrator with Phonetic TTS support.
    Handles Romanized Marathi for when native voices are missing.
    """

    def __init__(self):
        self.linguistic_agent = self.LinguisticAgent()
        self.environmental_agent = self.EnvironmentalAgent()
        self.decision_agent = self.DecisionAgent()
        self.advisory_agent = self.AdvisoryAgent()

    class LinguisticAgent:
        def process_input(self, text=None, audio_path=None):
            if audio_path:
                return transcribe_audio(audio_path)
            if text:
                return detect_and_translate(text)
            return {}

        def process_output(self, en_text, target_lang):
            return translate_output(en_text, target_lang)

    class EnvironmentalAgent:
        async def fetch_data(self, location, soil=None):
            if not location:
                return None
            
            # Fetch Weather and Forecast CONCURRENTLY rather than sequentially
            weather, forecast = await asyncio.gather(
                asyncio.to_thread(get_weather, location),
                asyncio.to_thread(get_forecast, location)
            )
            
            return {
                "current_weather": weather,
                "five_day_forecast": forecast,
                "soil_condition": soil or "Medium"
            }

    class DecisionAgent:
        def execute(self, env_data, task, crop):
            if not env_data:
                return None
            input_dict = {
                "crop": crop,
                "location": env_data["current_weather"].get("location"),
                "task": task,
                "rain_prob": env_data["current_weather"].get("rain_prob"),
                "humidity": env_data["current_weather"].get("humidity"),
                "temperature": env_data["current_weather"].get("temperature"),
                "soil": env_data["soil_condition"]
            }
            result = run_pipeline(input_dict)
            return result

    class AdvisoryAgent:
        def generate(self, decision_result, env_data, target_lang="English"):
            if not decision_result or not env_data:
                return {"explanation_en": "I need more information about your location or crop.", "explanation_local": "Data unavailable.", "explanation_phonetic": "Data unavailable."}

            context = {
                "crop": decision_result["decision"].get("crop"),
                "task": decision_result["decision"].get("task"),
                "location": env_data["current_weather"].get("location"),
                "rain_prob": env_data["current_weather"].get("rain_prob"),
                "humidity": env_data["current_weather"].get("humidity"),
                "temperature": env_data["current_weather"].get("temperature"),
                "guardrail_status": decision_result["guardrail"].get("status"),
                "reason": decision_result["guardrail"].get("reason")
            }
            return generate_farmer_explanation(context, target_lang)

    async def run_flow(self, text=None, audio_path=None, location=None, crop=None, soil="medium"):
        """
        Agentic flow with Phonetic TTS (Romanized).
        """
        # 1. Linguistic Agent (Input Layer)
        linguistic_in = self.linguistic_agent.process_input(text, audio_path)

        # Let the Guardrail agent catch missing data! Override with extracted data
        final_location = linguistic_in.get("location") or location or "Unknown"
        final_crop = linguistic_in.get("crop") or crop or "Unknown"
        final_task = linguistic_in.get("task") or "Unknown"
        source_lang = linguistic_in.get("detected_language", "English")

        # 2. Environmental Agent (Now Async for 2x faster APIs)
        env_data = await self.environmental_agent.fetch_data(final_location, soil)

        # 3. Decision Agent
        decision_out = self.decision_agent.execute(env_data, final_task, final_crop) if env_data else None

        # 4. Advisory Agent (Now inherently translates and Romanizes into JSON via prompt for 0 latency cost)
        if not decision_out:
             return {
                "linguistic": {"transcription": linguistic_in},
                "status": "error",
                "explanation": {"explanation_local": "Could not identify location."}
             }

        advice_en = self.advisory_agent.generate(decision_out, env_data, source_lang)

        # Removed 5. Linguistic Agent completely (1 less network trip, saving 1.5 seconds)

        from datetime import datetime
        return {
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "orchestration_mode": "async_agentic",
                "decision_authority": "deterministic_guardrail",
                "deployment_readiness": "prototype_v2"
            },
            "linguistic": {"transcription": linguistic_in, "source_language": source_lang},
            "environment": env_data,
            "pipeline": {
                "timeline": decision_out["timeline"],
                "summary": {
                    "guardrail_status": decision_out["guardrail"].get("status"),
                    "commit_state": decision_out["commit"].get("system_state"),
                    "recovery_triggered": decision_out["recovery"].get("recovered")
                }
            },
            "explanation": {
                "explanation_en": advice_en.get("explanation_en", ""),
                "explanation_local": advice_en.get("explanation_local", ""),
                "explanation_phonetic": advice_en.get("explanation_phonetic", ""),
                "detected_language": source_lang
            }
        }
