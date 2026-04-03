from db import save_output
from approval import check_approval

def run(pr_id, pr_number):
    decision, user = check_approval(pr_number, 3)

    if decision == "approved":
        save_output(pr_id, "approval_step_3", f"✅ Approved by {user}")
        return True

    if decision == "rejected":
        save_output(pr_id, "approval_step_3", f"❌ Rejected by {user}")
        return False

    save_output(
        pr_id,
        "approval_step_3",
        "⏳ Waiting for approval\n\n👉 Comment `/approve-step 3`\n👉 Comment `/reject-step 3`"
    )

    return False
