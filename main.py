import sys
import os
import time
import json
sys.path.append(os.getcwd())

from github_client import get_pr, post_agent_box, post_comment, read_output
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

DELAY = 2

init_db()

PR_NUMBER = int(os.getenv("PR_NUMBER"))
pr = get_pr(PR_NUMBER)

state_step, status = get_state(PR_NUMBER)

def post_box(agent_name, content, raw_data=None):
    post_agent_box(pr, agent_name, content, raw_data=raw_data)
    time.sleep(DELAY)

def post_new(content):
    post_comment(pr, content)
    time.sleep(DELAY)

def load_cached_outputs():
    """Read all agent outputs stored in PR comments — no LLM calls needed."""
    summary_raw   = read_output(pr, "summary")
    review_raw    = read_output(pr, "review")
    dp_raw        = read_output(pr, "deep_policy")
    questions_raw = read_output(pr, "ask_agent")

    review = json.loads(review_raw) if review_raw else {"HIGH": [], "MEDIUM": [], "LOW": []}

    return {
        "summary":   summary_raw or "",
        "review":    review,
        "deep_policy": dp_raw or "",
        "ask_agent": questions_raw or "",
    }


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
        update_state(PR_NUMBER, 8, "running")
        # Read from cached comments — zero LLM calls
        data = load_cached_outputs()
        post_new(coordinator.build_approval_summary(data))

    elif qa_status == "rejected":
        update_state(PR_NUMBER, 8, "rejected")
        data = load_cached_outputs()
        post_new(coordinator.build_rejection_summary("Step 8 (Final Approval)", data))

    elif qa_status == "done":
        post_new(coordinator.format_qa_done(payload))
        update_state(PR_NUMBER, state_step, "running")
        post_box("approval_step_8", coordinator.format_waiting_approval(8))

    elif qa_status == "question":
        answer = ask_agent.answer(payload, diff)
        post_new(coordinator.format_qa_answer(payload, answer))

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

# ── STEP 3: Analysis agents — save raw output into each comment ───────────────
summary = summarizer.run(diff)
post_box("summary", coordinator.format_summary(summary), raw_data=summary)

review = reviewer.run(diff)
post_box("review", coordinator.format_review(review), raw_data=json.dumps(review))

dp = deep_policy.run(diff)
post_box("deep_policy", coordinator.format_deep_policy(dp), raw_data=dp)

questions = ask_agent.run(diff)
post_box("ask_agent", coordinator.format_ask_agent(questions), raw_data=questions)

# ── Enter Q&A mode ────────────────────────────────────────────────────────────
update_state(PR_NUMBER, state_step, "qa")
