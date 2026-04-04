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

data = {}

# ---------------- REJECTION HANDLING (FIXED) ----------------
if status == "rejected":
    diff = ingestion.run(pr)

    # Always rebuild full pipeline view
    data["ingestion"] = diff
    data["early_policy"] = early_policy.run(pr)

    # Since rejection happens after step 3, we assume it was approved
    data["approval_step_3"] = "✅ Approved"

    # Always show step 2 content
    data["summary"] = summarizer.run(diff)
    data["review"] = reviewer.run(diff)
    data["deep_policy"] = deep_policy.run(diff)
    data["ask_agent"] = ask_agent.run(diff)

    data["approval_step_8"] = "❌ Rejected"

    data["final"] = "❌ PR Review Halted due to rejection"

    upsert_comment(pr, coordinator.build_report(data))
    exit(0)

# ---------------- STEP 1 ----------------
diff = ingestion.run(pr)

data["ingestion"] = diff
data["early_policy"] = early_policy.run(pr)

approved_3, msg_3 = approval_step_3.run(PR_NUMBER)
data["approval_step_3"] = msg_3

# STOP if step 3 not approved
if not approved_3:
    upsert_comment(pr, coordinator.build_report(data))
    exit(0)

# ---------------- STEP 2 ----------------
data["summary"] = summarizer.run(diff)
data["review"] = reviewer.run(diff)
data["deep_policy"] = deep_policy.run(diff)
data["ask_agent"] = ask_agent.run(diff)

approved_8, msg_8 = approval_step_8.run(PR_NUMBER)
data["approval_step_8"] = msg_8

# STOP if step 8 not approved
if not approved_8:
    upsert_comment(pr, coordinator.build_report(data))
    exit(0)

# ---------------- FINAL ----------------
data["final"] = "✅ PR Approved and Ready to Merge"

upsert_comment(pr, coordinator.build_report(data))
