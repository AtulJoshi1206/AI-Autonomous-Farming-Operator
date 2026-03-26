def commit(guardrail_output):
    """
    Commit Agent.
    Simulates a system state change based on guardrail approval.

    Input:
        guardrail_output: {
            "status":       "approved" | "blocked" | "need_more_data",
            "final_action": str | None,
            "reason":       str
        }

    Returns:
        {
            "action_committed": bool,
            "action":           str | None,
            "state_lock":       str | None,
            "system_state":     "locked" | "idle",
            "message":          str
        }

    Execution:
        - Checks status FIRST
        - Returns immediately if status != "approved"
        - final_action is only accessed when status == "approved"

    State Transitions:
        approved     → system_state = "locked"
        not approved → system_state = "idle"

    Constraints:
    - Deterministic only
    - No randomness
    - No external state
    - No hidden logic
    - No extra output fields
    - None values are Python None (JSON-serializable)
    """

    # --- Guard: exit immediately if not approved ---
    if guardrail_output["status"] != "approved":
        return {
            "action_committed": False,
            "action":           None,
            "state_lock":       None,
            "system_state":     "idle",
            "message":          "No action taken"
        }

    # --- Approved: commit and lock ---
    return {
        "action_committed": True,
        "action":           guardrail_output["final_action"],
        "state_lock":       "48_hours",
        "system_state":     "locked",
        "message":          "Action committed successfully"
    }
