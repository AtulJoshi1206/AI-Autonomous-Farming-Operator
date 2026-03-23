def guardrail(decision_output, input_data):
    """
    Upgraded Task-Aware Guardrail Agent.
    Now utilizes a global unbounded dynamic LLM Knowledge Base.
    Rules evaluated top-down. First match -> return.
    """
    # --- DYNAMIC GLOBAL CROP KNOWLEDGE ---
    dynamic_guard = input_data.get("_dynamic_guardrail")
    if dynamic_guard:
        return {
            "status": dynamic_guard.get("status", "need_more_data"),
            "final_action": decision_output.get("risk_aware_action"),
            "reason": dynamic_guard.get("reason", "Dynamic safety check.")
        }

    # FALLBACK (Deterministic Logic if LLM fails or is disconnected)
    task = input_data.get("task", "fertilization").lower()
    crop = input_data.get("crop", "wheat").lower()
    rain_prob = input_data.get("rain_prob", 0)
    soil = input_data.get("soil")
    confidence = decision_output.get("confidence", "High")

    # --- 1. Missing Soil ---
    if soil is None:
        return {
            "status": "need_more_data",
            "final_action": None,
            "reason": "Soil data is missing for task execution"
        }

    # --- 2. Unsafe Conditions ---
    if task == "fertilization" and crop == "wheat" and rain_prob > 60:
        return {
            "status": "blocked",
            "final_action": None,
            "reason": f"High rain probability ({rain_prob}%), wheat fertilization unsafe due to washout"
        }

    if task == "fertilization" and crop == "rice":
        # Rice has higher rain tolerance for fertilization
        if rain_prob > 80:
            return {
                "status": "blocked",
                "final_action": None,
                "reason": f"Severe rain probability ({rain_prob}%) exceeding rice tolerance thresholds."
            }
        elif soil == "poor" or soil == "dry":
            return {
                "status": "blocked",
                "final_action": None,
                "reason": "Rice requires moisture and nutrient-retaining soil; poor/dry soil blocked."
            }
        else:
            return {
                "status": "approved",
                "final_action": decision_output["risk_aware_action"],
                "reason": "Rice thrives in high moisture; current conditions within aquatic tolerance."
            }

    if task == "irrigation" and rain_prob > 60:
        return {
            "status": "blocked",
            "final_action": None,
            "reason": f"High rain probability ({rain_prob}%), irrigation blocked to prevent waterlogging"
        }

    if task == "planting" and rain_prob > 80:
        return {
            "status": "blocked",
            "final_action": None,
            "reason": f"Severe rain probability ({rain_prob}%), planting blocked due to flooding risk"
        }

    if task == "harvesting" and rain_prob > 60:
        return {
            "status": "blocked",
            "final_action": None,
            "reason": f"High rain probability ({rain_prob}%), harvesting blocked due to crop damage risk"
        }

    # --- 3. Low Confidence ---
    if confidence == "Low":
        return {
            "status": "blocked",
            "final_action": None,
            "reason": "Unreliable environment readings: Low confidence"
        }

    # --- 4. Otherwise ---
    return {
        "status": "approved",
        "final_action": decision_output["risk_aware_action"],
        "reason": f"Domain safety checks passed for {task} of {crop.capitalize()}"
    }
