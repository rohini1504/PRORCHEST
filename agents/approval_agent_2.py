from db import save_output, get_state, update_state
from approval import check_approval

STEP = 8

def run(pr_id, pr_number):
    last_step, status = get_state(pr_number)

    # ✅ Stop if already rejected
    if status == "rejected":
        return False

    # ✅ Prevent re-processing
    if last_step >= STEP:
        return True

    decision, user = check_approval(pr_number, STEP)

    if decision == "approved":
        msg = f"✅ Approved by {user}"
        save_output(pr_id, "approval_step_8", msg)
        update_state(pr_number, STEP)
        return True

    if decision == "rejected":
        msg = f"❌ Rejected by {user}"
        save_output(pr_id, "approval_step_8", msg)
        update_state(pr_number, STEP, "rejected")
        return False

    msg = (
        "⏳ Waiting for final approval\n\n"
        "👉 Comment `/approve-step 8`\n"
        "👉 Comment `/reject-step 8`"
    )

    save_output(pr_id, "approval_step_8", msg)
    return False
