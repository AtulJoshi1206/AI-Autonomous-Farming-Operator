def verify(commit_output, input_data):
    """
    Verification Agent.
    Checks whether the committed action produced the expected outcome.

    Inputs:
        commit_output: {
            "action_committed": bool,
            "action":           str | None,
            "state_lock":       str | None,
            "system_state":     "locked" | "idle",
            "message":          str
        }
        input_data: {
            "rain_prob": int | float,
            ...
        }

    Returns (no action committed):
        {
            "verified":        False,
            "deviation":       None,
            "deviation_level": None,
            "reason":          "No action to verify"
        }

    Returns (action was committed):
        {
            "verified":        True,
            "expected_rain":   int | float,
            "actual_rain":     int | float,
            "deviation":       int | float,
            "deviation_level": "low" | "medium" | "high"
        }

    Deviation levels:
        <= 10          → "low"
        > 10 and <= 30 → "medium"
        > 30           → "high"

    Constraints:
    - Deterministic only
    - No randomness, no external APIs
    - Simulated actual_rain derived solely from expected_rain
    - No extra fields
    """

    # --- Guard: nothing was committed ---
    if commit_output["action_committed"] == False:
        return {
            "verified":        False,
            "deviation":       None,
            "deviation_level": None,
            "reason":          "No action to verify"
        }

    # --- Verification logic ---
    expected_rain = input_data["rain_prob"]

    # Simulate actual rain outcome - appears as a prediction error
    if expected_rain > 60:
        actual_rain = max(0, expected_rain - 70)
    else:
        actual_rain = expected_rain

    # Compute deviation
    deviation = abs(expected_rain - actual_rain)

    # Classify deviation level (strict order, no overlap)
    if deviation <= 10:
        deviation_level = "low"
    elif deviation <= 30:
        deviation_level = "medium"
    else:
        deviation_level = "high"

    return {
        "verified":        True,
        "expected_rain":   expected_rain,
        "actual_rain":     actual_rain,
        "deviation":       deviation,
        "deviation_level": deviation_level
    }


def recover(verification_output, commit_output):
    """
    Recovery Agent.
    Triggers recovery ONLY when the committed action produced a high deviation.

    Inputs:
        verification_output: output from verify()
        commit_output:       output from commit()

    Returns:
        {
            "recovered": bool,
            "message":   str
        }

    Recovery rules (strict order, first match exits immediately):
        1. verified == False         → no recovery needed
        2. deviation_level == "high" → recover and report failed action
        3. else                      → no recovery needed

    Constraints:
    - Recovery only triggers when commit_output["action_committed"] == True
    - Deterministic only
    - No randomness, no external APIs
    - No hidden state
    - No extra fields
    """

    # Recovery context requirement: only meaningful when an action was committed
    if commit_output["action_committed"] != True:
        return {
            "recovered": False,
            "message":   "No recovery needed"
        }

    # --- Rule 1: nothing was verified ---
    if verification_output["verified"] == False:
        return {
            "recovered": False,
            "message":   "No recovery needed"
        }

    # --- Rule 2: high deviation → trigger recovery ---
    if verification_output["deviation_level"] == "high":
        rec_msg = (
            f"[Recovery Triggered]\n\n"
            f"Previous action '{commit_output['action']}' failed due to environmental mismatch.\n"
            f"Estimated yield impact: 5-10% potential loss.\n"
            f"Expected rain: {verification_output['expected_rain']}%\n"
            f"Observed rain: {verification_output['actual_rain']}%\n\n"
            f"Deviation detected → strategy adjusted to mitigate loss"
        )
        return {
            "recovered": True,
            "message":   rec_msg,
            "resolution": rec_msg
        }

    # --- Rule 3: low or medium deviation → no recovery ---
    return {
        "recovered": False,
        "message":   "No recovery needed",
        "resolution": "System stable. No recovery needed."
    }
