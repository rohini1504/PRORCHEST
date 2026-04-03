from db import save_output

def run(pr_id):
    # TEMP: auto approve (replace later with real polling)
    decision = "✅ Auto-approved (Step 3)"
    save_output(pr_id, "approval_step_3", decision)
    return decision
