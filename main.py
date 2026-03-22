from agents.decision import decision
from agents.guardrail import guardrail
from agents.commit import commit
from agents.verification import verify, recover


def print_timeline(timeline):
    """
    Prints the full execution trace for the current pipeline run.
    Reads directly from the timeline list — no hardcoded values.
    """
    print("\n" + "=" * 27)
    print("  SYSTEM TIMELINE")
    print("=" * 27)
    for entry in timeline:
        label = entry["stage"].upper()
        print(f"\n[{label}]")
        for key, value in entry["output"].items():
            print(f"  {key}: {value}")


def run_pipeline(input_data):
    """
    Core Decision Engine Pipeline.
    Lifecycle: Input → Decision → Guardrail → Commit
    commit() runs ONLY when guardrail status is 'approved'.
    """

    timeline = []

    # --- Step 1: Decision ---
    decision_output = decision(input_data)
    print("\n[DECISION OUTPUT]")
    for key, value in decision_output.items():
        print(f"  {key}: {value}")
    timeline.append({"stage": "decision", "output": decision_output})

    # --- Step 2: Guardrail ---
    guardrail_output = guardrail(decision_output, input_data)
    print("\n[GUARDRAIL OUTPUT]")
    for key, value in guardrail_output.items():
        print(f"  {key}: {value}")
    timeline.append({"stage": "guardrail", "output": guardrail_output})

    if guardrail_output.get("status") in ["blocked", "need_more_data"]:
        print("\nPipeline Halted: Downstream Commit/Verify/Recover agents bypassed to save resources.")
        return {
            "decision":     decision_output,
            "guardrail":    guardrail_output,
            "commit":       {"system_state": "idle", "action": "None"},
            "verification": {"verified": False, "deviation": None, "reason": "No action to verify"},
            "recovery":     {"recovered": False, "message": "No recovery needed"},
            "timeline":     timeline
        }

    # --- Step 3: Commit (runs only when approved) ---
    commit_output = commit(guardrail_output)
    print("\n[COMMIT OUTPUT]")
    for key, value in commit_output.items():
        print(f"  {key}: {value}")
    timeline.append({"stage": "commit", "output": commit_output})

    # --- Step 4: Verify ---
    verification_output = verify(commit_output, input_data)
    print("\n[VERIFICATION OUTPUT]")
    for key, value in verification_output.items():
        print(f"  {key}: {value}")
    timeline.append({"stage": "verify", "output": verification_output})

    # --- Step 5: Recover ---
    recovery_output = recover(verification_output, commit_output)
    print("\n[RECOVERY OUTPUT]")
    for key, value in recovery_output.items():
        print(f"  {key}: {value}")
    timeline.append({"stage": "recover", "output": recovery_output})

    return {
        "decision":     decision_output,
        "guardrail":    guardrail_output,
        "commit":       commit_output,
        "verification": verification_output,
        "recovery":     recovery_output,
        "timeline":     timeline
    }


if __name__ == "__main__":
    # Professional Step 6 test case
    input_data = {
        "crop": "wheat",
        "location": "Moradabad",
        "rain_prob": 78,
        "humidity": 82,
        "temp": 30,
        "soil": "medium"
    }

    print("=" * 40)
    print("  AI Autonomous Farming Operator")
    print("  Decision System — Step 6")
    print("=" * 40)

    result = run_pipeline(input_data)
    print_timeline(result["timeline"])

    print("\n" + "=" * 40)
    print("  Pipeline complete.")
    print("=" * 40)
