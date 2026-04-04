import sys
import os
sys.path.append(os.getcwd())

from github_client import get_pr, post_agent_box, post_comment
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

def post_box(agent_name, content):
    post_agent_box(pr, agent_name, content)

# ── ALREADY REJECTED — just post coordinator rejection box ────────────────────
if status == "rejected":
    ingested = ingestion.run(pr)
    stage = "Step 3 (Early Policy)" if state_step < 8 else "Step 8 (Final Approval)"
    data = {
        "early_policy": early_policy.run(pr),
        "diff": ingested["diff"],
    }
    post_comment(pr, coordinator.build_rejection_summary(stage, data))
    exit(0)

# ── STEP 1: Ingestion ─────────────────────────────────────────────────────────
ingested = ingestion.run(pr)
diff = ingested["diff"]

post_box("ingestion", coordinator.format_ingestion(ingested))

# ── STEP 2: Early Policy ──────────────────────────────────────────────────────
early = early_policy.run(pr)
post_box("early_policy", coordinator.format_early_policy(early))

# ── APPROVAL GATE 1 (Step 3) ──────────────────────────────────────────────────
approved_3, msg_3 = approval_step_3.run(PR_NUMBER)

if not approved_3:
    if "Rejected" in msg_3:
        data = {"early_policy": early}
        post_comment(pr, coordinator.build_rejection_summary("Step 3 (Early Policy)", data))
    else:
        post_box("approval_step_3", coordinator.format_waiting_approval(3))
    exit(0)

# Extract approving user from msg e.g. "✅ Approved by alice"
approver_3 = msg_3.split("by ")[-1] if "by " in msg_3 else "reviewer"
post_box("approval_step_3", coordinator.format_approval_granted(3, approver_3))

# ── STEP 3: Analysis agents ───────────────────────────────────────────────────
summary = summarizer.run(diff)
post_box("summary", coordinator.format_summary(summary))

review = reviewer.run(diff)
post_box("review", coordinator.format_review(review))

dp = deep_policy.run(diff)
post_box("deep_policy", coordinator.format_deep_policy(dp))

ask = ask_agent.run(diff)
post_box("ask_agent", coordinator.format_ask_agent(ask))

# ── APPROVAL GATE 2 (Step 8) ──────────────────────────────────────────────────
approved_8, msg_8 = approval_step_8.run(PR_NUMBER)

if not approved_8:
    if "Rejected" in msg_8:
        data = {"summary": summary, "review": review, "deep_policy": dp}
        post_comment(pr, coordinator.build_rejection_summary("Step 8 (Final Approval)", data))
    else:
        post_box("approval_step_8", coordinator.format_waiting_approval(8))
    exit(0)

# ── FINAL: Coordinator approval summary ───────────────────────────────────────
data = {"summary": summary, "review": review, "deep_policy": dp, "ask_agent": ask}
post_comment(pr, coordinator.build_approval_summary(data))
