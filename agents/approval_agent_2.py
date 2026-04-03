from db import save_output
from approval import wait_for_approval

def run(pr_id, pr_number):
    save_output(pr_id, "approval_step_8",
                "⏳ Waiting for final approval (/approve-step 8)")

    decision, user = wait_for_approval(pr_number, 8)

    if decision == "rejected":
        raise Exception("❌ Rejected at step 8")

    save_output(pr_id, "approval_step_8", f"✅ Approved by {user}")
