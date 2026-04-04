from db import get_state, update_state
from approval import check_approval

STEP = 8

def run(pr_number):
    last_step, status = get_state(pr_number)

    # ❌ HARD STOP if rejected
    if status == "rejected":
        return False, "❌ PR already rejected"

    decision, user = check_approval(pr_number, STEP)

    # ✅ APPROVED
    if decision == "approved":
        update_state(pr_number, STEP)
        return True, f"✅ Approved by {user}"

    # ❌ REJECTED
    if decision == "rejected":
        update_state(pr_number, STEP, "rejected")
        return False, f"❌ Rejected by {user}"

    # ✅ ONLY mark "already approved" if:
    # step reached AND NOT rejected
    if last_step >= STEP:
        return True, "✅ Already approved"

    # ⏳ WAITING
    return False, (
        "⏳ Waiting for final approval\n\n"
        "👉 Comment `/approve-step 8`\n"
        "👉 Comment `/reject-step 8`"
    )
