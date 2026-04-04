from llm_client import call_llm

SYSTEM = "You are a senior engineering lead. Be concise and direct."

# ── Box wrapper ────────────────────────────────────────────────────────────────

def _box(emoji, title, body):
    return f"### {emoji} {title}\n---\n{body}\n"


# ── Per-agent formatters ───────────────────────────────────────────────────────

def format_ingestion(result):
    return _box("📥", "Ingestion", result["metadata"])

def format_early_policy(result):
    return _box("📋", "Early Policy Check", result)

def format_waiting_approval(step):
    body = (
        f"Automated checks complete. A human reviewer must approve before the pipeline continues.\n\n"
        f"> `/approve-step {step}` — continue\n"
        f"> `/reject-step {step}` — halt"
    )
    return _box("⏳", f"Awaiting Human Approval (Step {step})", body)

def format_approval_granted(step, user):
    return _box("✅", f"Step {step} Approved", f"Approved by **{user}**. Proceeding to next stage.")

def format_summary(result):
    return _box("📝", "PR Summary", result)

def format_review(result):
    def items(lst):
        return "\n".join(f"- {i}" for i in lst) if lst else "_None found_"

    body = (
        f"**🔴 High** (bugs / security)\n{items(result.get('HIGH', []))}\n\n"
        f"**🟡 Medium** (logic / patterns)\n{items(result.get('MEDIUM', []))}\n\n"
        f"**🟢 Low** (style / readability)\n{items(result.get('LOW', []))}"
    )
    return _box("🔍", "Code Review", body)

def format_deep_policy(result):
    return _box("🛡️", "Policy & Standards Check", result)

def format_ask_agent(result):
    return _box("💬", "Clarification Questions", result)


# ── Coordinator summaries (terminal points only) ──────────────────────────────

def build_rejection_summary(stage, data):
    context = ""
    if data.get("early_policy"):
        context += f"Early Policy:\n{data['early_policy']}\n\n"
    if data.get("summary"):
        context += f"Summary:\n{data['summary']}\n\n"
    if data.get("review") and isinstance(data["review"], dict):
        high = data["review"].get("HIGH", [])
        if high:
            context += "Critical Issues:\n" + "\n".join(f"- {i}" for i in high) + "\n\n"

    prompt = f"""A PR review was rejected at: {stage}

Available findings:
{context[:2000]}

Write 2-3 sentences: what was rejected, the main reason, and what the author must fix.
No bullet points. Plain prose only."""

    summary = call_llm(prompt, system_prompt=SYSTEM)
    body = (
        f"{summary}\n\n"
        f"_Push a new commit or re-open the PR to restart the review._"
    )
    return _box("❌", f"Review Rejected — {stage}", body)


def build_approval_summary(data):
    review = data.get("review", {})
    high   = review.get("HIGH",   []) if isinstance(review, dict) else []
    medium = review.get("MEDIUM", []) if isinstance(review, dict) else []
    low    = review.get("LOW",    []) if isinstance(review, dict) else []

    prompt = f"""A PR passed all review stages and is approved to merge.

Summary: {data.get('summary', 'N/A')}
High issues: {', '.join(high) or 'none'}
Medium issues: {', '.join(medium) or 'none'}
Policy notes: {data.get('deep_policy', 'N/A')}

Write 3 sentences: what the PR does, any important caveats, and a clear merge sign-off.
Plain prose only."""

    summary = call_llm(prompt, system_prompt=SYSTEM)

    stats = (
        f"| | Count |\n"
        f"|---|---|\n"
        f"| 🔴 High | {len(high)} |\n"
        f"| 🟡 Medium | {len(medium)} |\n"
        f"| 🟢 Low | {len(low)} |\n"
    )

    body = f"{summary}\n\n{stats}"
    return _box("✅", "Approved — Ready to Merge", body)
