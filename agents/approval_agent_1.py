from db import save_output, get_state, update_state
from approval import check_approval

STEP = 3

def run(pr_id, pr_number):
    last_step, status = get_state(pr_number)

    # ✅ Prevent re-processing
    if status == "rejected":
        return False

    if last_step >= STEP:
        return True

    decision, user = check_approval(pr_number, STEP)

    if decision == "approved":
        msg = f"✅ Approved by {user}"
        save_output(pr_id, "approval_step_3", msg)
        update_state(pr_number, STEP)
        return True

    if decision == "rejected":
        msg = f"❌ Rejected by {user}"
        save_output(pr_id, "approval_step_3", msg)
        update_state(pr_number, STEP, "rejected")
        return False

    # ⏳ Waiting state
    msg = (
        "⏳ Waiting for approval\n\n"
        "👉 Comment `/approve-step 3`\n"
        "👉 Comment `/reject-step 3`"
    )

    save_output(pr_id, "approval_step_3", msg)
    return False
