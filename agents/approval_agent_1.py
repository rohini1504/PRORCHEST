from db import get_state, update_state
from approval import check_approval

STEP = 3

def run(pr_number):
    last_step, status = get_state(pr_number)

    # ❌ Stop if already rejected
    if status == "rejected":
        return False, "❌ PR already rejected"

    # ✅ Skip if already approved
    if last_step >= STEP:
        return True, "✅ Already approved"

    decision, user = check_approval(pr_number, STEP)

    if decision == "approved":
        update_state(pr_number, STEP)
        return True, f"✅ Approved by {user}"

    if decision == "rejected":
        update_state(pr_number, STEP, "rejected")
        return False, f"❌ Rejected by {user}"

    return False, (
        "⏳ Waiting for approval\n\n"
        "👉 Comment `/approve-step 3`\n"
        "👉 Comment `/reject-step 3`"
    )
