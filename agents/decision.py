from utils.gemini import analyze_crop_conditions

def decision(input_data):
    """
    Upgraded Multi-Task Autonomous Operator Decision Agent.
    Now utilizes a global unbounded dynamic LLM Knowledge Base.
    Input: { crop, location, task, rain_prob, humidity, temperature, soil }
    """
    crop = input_data.get("crop", "wheat").lower()
    location = input_data.get("location", "Unknown Location")
    task = input_data.get("task", "fertilization").lower()
    rain_prob = input_data.get("rain_prob", 0)
    humidity = input_data.get("humidity", 0)
    temp = input_data.get("temperature", 25)
    soil = input_data.get("soil", "medium")

    # --- DYNAMIC GLOBAL CROP KNOWLEDGE ---
    # Call the free Gemini API to analyze any crop for seasonality, soil, and weather
    llm_analysis = analyze_crop_conditions(input_data)
    
    if llm_analysis and "decision" in llm_analysis:
        # Save the guardrail analysis to avoid calling the LLM twice
        if "guardrail" in llm_analysis:
            input_data["_dynamic_guardrail"] = llm_analysis["guardrail"]
            
        return {
            "task": task,
            "aggressive_action": f"Proceed with {task}",
            "risk_aware_action": llm_analysis["decision"].get("risk_aware_action", f"Proceed with {task}"),
            "reasoning": llm_analysis["decision"].get("reasoning", ""),
            "confidence": llm_analysis["decision"].get("confidence", "Medium")
        }

    # FALLBACK (Deterministic Logic if LLM fails or is disconnected)
    aggressive_action = f"Proceed with {task}"
    risk_aware_action = f"Proceed with {task}"

    # TASK LOGIC
    if task == "planting":
        if 30 <= rain_prob <= 70:
            risk_aware_action = "Proceed with planting"
        elif rain_prob > 80:
            risk_aware_action = "Delay planting due to heavy rain"
            
    elif task == "irrigation":
        if rain_prob > 60:
            risk_aware_action = "Do NOT irrigate, sufficient rainfall"
        elif rain_prob < 30:
            risk_aware_action = "Irrigation required"
            
    elif task == "fertilization":
        if crop == "wheat" and rain_prob > 60:
            risk_aware_action = "Delay fertilization"
        elif crop == "rice" and rain_prob > 60:
            risk_aware_action = "Proceed with fertilization"
            
    elif task == "harvesting":
        if rain_prob > 60:
            risk_aware_action = "Delay harvesting (crop damage risk)"
        elif rain_prob < 40:
            risk_aware_action = "Proceed with harvesting"

    # CONFIDENCE DETERMINATION
    if not soil:
        confidence = "Low"
    elif rain_prob > 70:
        confidence = "Low"
    elif 40 <= rain_prob <= 70:
        confidence = "Medium"
    else:
        confidence = "High"

    # REASONING CONSTRUCTION
    reasoning = (
        f"For {task} {crop} in {location}, rain probability is {rain_prob}% with humidity {humidity}%. "
        f"Hence {risk_aware_action.lower()} is recommended."
    )

    return {
        "task": task,
        "aggressive_action": aggressive_action,
        "risk_aware_action": risk_aware_action,
        "reasoning": reasoning,
        "confidence": confidence
    }
