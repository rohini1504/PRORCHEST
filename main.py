import sys
import os
import time
sys.path.append(os.getcwd())

from github_client import get_pr, post_agent_box, post_comment
from db import init_db, get_state, update_state
from approval import check_approval, check_qa_comment

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

DELAY = 3

init_db()

PR_NUMBER = int(os.getenv("PR_NUMBER"))
pr = get_pr(PR_NUMBER)

state_step, status = get_state(PR_NUMBER)

def post_box(agent_name, content):
    post_agent_box(pr, agent_name, content)
    time.sleep(DELAY)

def post_new(content):
    post_comment(pr, content)
    time.sleep(DELAY)


# ── REJECTED ──────────────────────────────────────────────────────────────────
if status == "rejected":
    ingested = ingestion.run(pr)
    stage = "Step 3 (Early Policy)" if state_step < 8 else "Step 8 (Final Approval)"
    post_new(coordinator.build_rejection_summary(stage, {"early_policy": early_policy.run(pr)}))
    exit(0)


# ── Q&A MODE ──────────────────────────────────────────────────────────────────
if status == "qa":
    ingested = ingestion.run(pr)
    diff = ingested["diff"]

    qa_status, payload = check_qa_comment(PR_NUMBER)

    if qa_status == "approved":
        # User approved directly from Q&A — skip /done, go straight to final
        update_state(PR_NUMBER, 8, "running")
        summary   = summarizer.run(diff)
        review    = reviewer.run(diff)
        dp        = deep_policy.run(diff)
        questions = ask_agent.run(diff)
        data = {"summary": summary, "review": review, "deep_policy": dp, "ask_agent": questions}
        post_new(coordinator.build_approval_summary(data))

    elif qa_status == "rejected":
        update_state(PR_NUMBER, 8, "rejected")
        summary = summarizer.run(diff)
        review  = reviewer.run(diff)
        dp      = deep_policy.run(diff)
        post_new(coordinator.build_rejection_summary(
            "Step 8 (Final Approval)",
            {"summary": summary, "review": review, "deep_policy": dp}
        ))

    elif qa_status == "done":
        # User done with questions — switch back to running and show approval gate
        post_new(coordinator.format_qa_done(payload))
        update_state(PR_NUMBER, state_step, "running")
        post_box("approval_step_8", coordinator.format_waiting_approval(8))

    elif qa_status == "question":
        answer = ask_agent.answer(payload, diff)
        post_new(coordinator.format_qa_answer(payload, answer))
        # Stay in qa — label unchanged

    # else: no new comment this run, nothing to do
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
        post_new(coordinator.build_rejection_summary("Step 3 (Early Policy)", {"early_policy": early}))
    else:
        post_box("approval_step_3", coordinator.format_waiting_approval(3))
    exit(0)

approver_3 = msg_3.split("by ")[-1] if "by " in msg_3 else "reviewer"
post_box("approval_step_3", coordinator.format_approval_granted(3, approver_3))

# ── STEP 3: Analysis agents ───────────────────────────────────────────────────
summary = summarizer.run(diff)
post_box("summary", coordinator.format_summary(summary))

review = reviewer.run(diff)
post_box("review", coordinator.format_review(review))

dp = deep_policy.run(diff)
post_box("deep_policy", coordinator.format_deep_policy(dp))

# ── ASK AGENT — post seed questions, enter Q&A mode ──────────────────────────
questions = ask_agent.run(diff)
post_box("ask_agent", coordinator.format_ask_agent(questions))

# Switch label to qa — next run routes to the Q&A branch above
update_state(PR_NUMBER, state_step, "qa")
