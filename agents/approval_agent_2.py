from db import save_output

def run(pr_id):
    # TEMP: auto approve
    decision = "✅ Auto-approved (Step 8)"
    save_output(pr_id, "approval_step_8", decision)
    return decision
