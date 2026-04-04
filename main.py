import sys
import os
sys.path.append(os.getcwd())

from github_client import get_pr, upsert_comment
from db import init_db, get_state, get_all_outputs, save_output

from agents import (
    ingestion,
    early_policy,
    summarizer,
    reviewer,
    deep_policy,
    ask_agent,
    coordinator,
    approval_step_3,
    approval_step_8
)

init_db()

PR_NUMBER = int(os.getenv("PR_NUMBER"))
pr = get_pr(PR_NUMBER)

state_step, status = get_state(PR_NUMBER)

data = {}

# ---------------- REJECTION HANDLING ----------------
if status == "rejected":
    saved = get_all_outputs(PR_NUMBER)

    # Restore whatever was already computed — no need to re-run LLM agents
    data["ingestion"] = saved.get("ingestion", "N/A")
    data["early_policy"] = saved.get("early_policy", "N/A")

    # Step 3 rejection: never reached step 2 agents
    if state_step < 8:
        data["approval_step_3"] = "❌ Rejected — pipeline stopped here"
    else:
        data["approval_step_3"] = saved.get("approval_step_3", "✅ Approved")
        data["summary"] = saved.get("summary", "N/A")
        data["review"] = saved.get("review", "N/A")
        data["deep_policy"] = saved.get("deep_policy", "N/A")
        data["ask_agent"] = saved.get("ask_agent", "N/A")
        data["approval_step_8"] = "❌ Rejected — pipeline stopped here"

    data["final"] = "❌ PR Review Halted due to rejection"
    upsert_comment(pr, coordinator.build_report(data))
    exit(0)

# ---------------- STEP 1 ----------------
diff = ingestion.run(pr)
data["ingestion"] = diff
save_output(PR_NUMBER, "ingestion", diff)

early = early_policy.run(pr)
data["early_policy"] = early
save_output(PR_NUMBER, "early_policy", early)

approved_3, msg_3 = approval_step_3.run(PR_NUMBER)
data["approval_step_3"] = msg_3
save_output(PR_NUMBER, "approval_step_3", msg_3)

# STOP if step 3 not approved
if not approved_3:
    upsert_comment(pr, coordinator.build_report(data))
    exit(0)

# ---------------- STEP 2 ----------------
summary = summarizer.run(diff)
data["summary"] = summary
save_output(PR_NUMBER, "summary", summary)

review = reviewer.run(diff)
data["review"] = review
save_output(PR_NUMBER, "review", str(review))

dp = deep_policy.run(diff)
data["deep_policy"] = dp
save_output(PR_NUMBER, "deep_policy", dp)

ask = ask_agent.run(diff)
data["ask_agent"] = ask
save_output(PR_NUMBER, "ask_agent", ask)

approved_8, msg_8 = approval_step_8.run(PR_NUMBER)
data["approval_step_8"] = msg_8

# STOP if step 8 not approved
if not approved_8:
    upsert_comment(pr, coordinator.build_report(data))
    exit(0)

# ---------------- FINAL ----------------
data["final"] = "✅ PR Approved and Ready to Merge"
upsert_comment(pr, coordinator.build_report(data))
