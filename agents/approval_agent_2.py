from db import save_output
from approval import check_approval

def run(pr_id, pr_number):
    decision, user = check_approval(pr_number, 8)

    if decision == "approved":
        save_output(pr_id, "approval_step_8", f"✅ Approved by {user}")
        return True

    if decision == "rejected":
        save_output(pr_id, "approval_step_8", f"❌ Rejected by {user}")
        raise Exception("Stopped at step 8")

    save_output(pr_id, "approval_step_8",
                "⏳ Awaiting approval (/approve-step 8)")
    raise Exception("Waiting for approval")
