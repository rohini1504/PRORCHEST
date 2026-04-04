import sys
import os
sys.path.append(os.getcwd())

from github_client import get_pr, upsert_comment
from db import init_db, get_state

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

# ❌ STOP if rejected
if status == "rejected":
    data = {
        "final": "❌ PR was rejected. Pipeline stopped."
    }
    upsert_comment(pr, coordinator.build_report(data))
    exit(0)

data = {}

# ---------------- STEP 1 ----------------
if state_step < 3:
    diff = ingestion.run(pr)

    data["ingestion"] = diff
    data["early_policy"] = early_policy.run(pr)

    approved, msg = approval_step_3.run(PR_NUMBER)
    data["approval_step_3"] = msg

    if not approved:
        upsert_comment(pr, coordinator.build_report(data))
        exit(0)

# ---------------- STEP 2 ----------------
if state_step < 8:
    diff = ingestion.run(pr)

    data["summary"] = summarizer.run(diff)
    data["review"] = reviewer.run(diff)
    data["deep_policy"] = deep_policy.run(diff)
    data["ask_agent"] = ask_agent.run(diff)

    approved, msg = approval_step_8.run(PR_NUMBER)
    data["approval_step_8"] = msg

    if not approved:
        upsert_comment(pr, coordinator.build_report(data))
        exit(0)

# ---------------- FINAL ----------------
data["final"] = "✅ PR Approved and Ready to Merge"

upsert_comment(pr, coordinator.build_report(data))
