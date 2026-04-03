from db import save_output
from approval import wait_for_approval

def run(pr_id, pr_number):
    save_output(pr_id, "approval_step_3",
                "⏳ Waiting for approval (/approve-step 3)")

    decision, user = wait_for_approval(pr_number, 3)

    if decision == "rejected":
        raise Exception("❌ Rejected at step 3")

    save_output(pr_id, "approval_step_3", f"✅ Approved by {user}")
