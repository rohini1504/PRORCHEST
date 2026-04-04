from db import get_state, update_state
from approval import check_approval

STEP = 3

def run(pr_number):
    last_step, status = get_state(pr_number)

    # Always check the latest comment first — it may override DB state
    decision, user = check_approval(pr_number, STEP)

    if decision == "approved":
        update_state(pr_number, STEP, "running")
        return True, f"✅ Approved by {user}"

    if decision == "rejected":
        update_state(pr_number, STEP, "rejected")
        return False, f"❌ Rejected by {user}"

    # No new comment — fall back to DB state
    if status == "rejected":
        return False, "❌ PR already rejected"

    if last_step >= STEP:
        return True, "✅ Already approved"

    return False, (
        "⏳ Waiting for approval\n\n"
        "👉 Comment `/approve-step 3`\n"
        "👉 Comment `/reject-step 3`"
    )
