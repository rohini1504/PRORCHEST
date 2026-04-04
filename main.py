import os
from github_client import get_pr, upsert_comment, get_latest_comment
from db import init_db, get_state, update_state

from agents import ingestion, early_policy, summarizer, reviewer, deep_policy, ask_agent, coordinator

init_db()

PR_NUMBER = int(os.getenv("PR_NUMBER"))
pr = get_pr(PR_NUMBER)

state_step, status = get_state(PR_NUMBER)
latest_comment = get_latest_comment(pr)

def check_approval(step):
    if f"/approve-step {step}" in latest_comment:
        return "approved"
    if f"/reject-step {step}" in latest_comment:
        return "rejected"
    return "waiting"

data = {}

# ---------------- STEP 1 ----------------
if state_step < 3:
    data["ingestion"] = ingestion.run(pr)
    data["early_policy"] = early_policy.run(pr)

    decision = check_approval(3)

    if decision == "waiting":
        data["approval_step_3"] = "⏳ Waiting for approval\n👉 Comment /approve-step 3"
        upsert_comment(pr, coordinator.build_report(data))
        exit(0)

    if decision == "rejected":
        data["approval_step_3"] = "❌ Rejected"
        update_state(PR_NUMBER, 3, "rejected")
        upsert_comment(pr, coordinator.build_report(data))
        exit(0)

    update_state(PR_NUMBER, 3)

# ---------------- STEP 2 ----------------
if state_step < 8:
    diff = ingestion.run(pr)

    data["summary"] = summarizer.run(diff)

    review = reviewer.run(diff)
    data["review"] = f"""
HIGH:
{chr(10).join(review['HIGH'])}

MEDIUM:
{chr(10).join(review['MEDIUM'])}

LOW:
{chr(10).join(review['LOW'])}
"""

    data["deep_policy"] = deep_policy.run(diff)
    data["ask_agent"] = ask_agent.run()

    decision = check_approval(8)

    if decision == "waiting":
        data["approval_step_8"] = "⏳ Waiting for approval\n👉 Comment /approve-step 8"
        upsert_comment(pr, coordinator.build_report(data))
        exit(0)

    if decision == "rejected":
        data["approval_step_8"] = "❌ Rejected"
        update_state(PR_NUMBER, 8, "rejected")
        upsert_comment(pr, coordinator.build_report(data))
        exit(0)

    update_state(PR_NUMBER, 8)

# ---------------- FINAL ----------------
data["final"] = "✅ PR Approved and Ready to Merge"

upsert_comment(pr, coordinator.build_report(data))
