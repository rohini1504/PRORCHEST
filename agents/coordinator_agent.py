from llm_client import call_llm

SYSTEM = "You are a senior engineering lead summarizing a multi-agent PR review pipeline."

# ─────────────────────────────────────────────
#  Box formatting helpers
# ─────────────────────────────────────────────

def _box(title, emoji, content):
    return (
        f"## {emoji} {title}\n\n"
        f"{content}\n"
    )


# ─────────────────────────────────────────────
#  Individual agent boxes (called from main.py)
# ─────────────────────────────────────────────

def format_ingestion(diff):
    return _box("Ingestion", "📥", f"```diff\n{diff[:2000]}\n```")

def format_early_policy(result):
    return _box("Early Policy Check", "📋", result)

def format_waiting_approval(step):
    return _box(
        f"Awaiting Approval — Step {step}", "⏳",
        f"👉 Comment `/approve-step {step}` to continue\n"
        f"👉 Comment `/reject-step {step}` to halt"
    )

def format_summary(result):
    return _box("PR Summary", "📝", result)

def format_review(result):
    if isinstance(result, dict):
        high   = "\n".join(f"- {i}" for i in result.get("HIGH",   [])) or "_None_"
        medium = "\n".join(f"- {i}" for i in result.get("MEDIUM", [])) or "_None_"
        low    = "\n".join(f"- {i}" for i in result.get("LOW",    [])) or "_None_"
        body = (
            f"**🔴 HIGH**\n{high}\n\n"
            f"**🟡 MEDIUM**\n{medium}\n\n"
            f"**🟢 LOW**\n{low}"
        )
    else:
        body = str(result)
    return _box("Code Review", "🔍", body)

def format_deep_policy(result):
    return _box("Deep Policy Analysis", "🛡️", result)

def format_ask_agent(result):
    return _box("Discussion Questions", "💬", result)


# ─────────────────────────────────────────────
#  Coordinator summaries (posted as final boxes)
# ─────────────────────────────────────────────

def build_rejection_summary(stage, data):
    """
    Called when a step is rejected.
    stage: human-readable name of where rejection happened e.g. "Step 3 (Early Policy)"
    data: dict of whatever outputs exist so far
    """
    context_parts = []
    for key, val in data.items():
        if val:
            context_parts.append(f"[{key}]\n{val}")
    context = "\n\n".join(context_parts)[:3000]

    prompt = f"""
A PR review pipeline was REJECTED at: {stage}

Here is everything that was collected before rejection:
{context}

Write a concise rejection summary (3-5 sentences) covering:
- What stage it was rejected at and why (based on available data)
- The most critical issues found
- What the author should fix before re-submitting
"""
    llm_summary = call_llm(prompt, system_prompt=SYSTEM)

    return _box(
        f"Review Rejected at {stage}", "❌",
        f"{llm_summary}\n\n"
        f"---\n_Re-open or push a new commit to restart the review pipeline._"
    )


def build_approval_summary(data):
    """
    Called on final approval. Synthesizes all agent outputs into a gist.
    data: dict of all agent outputs
    """
    review = data.get("review", {})
    if isinstance(review, dict):
        high   = review.get("HIGH",   [])
        medium = review.get("MEDIUM", [])
        low    = review.get("LOW",    [])
        review_text = (
            f"HIGH: {', '.join(high) or 'none'}\n"
            f"MEDIUM: {', '.join(medium) or 'none'}\n"
            f"LOW: {', '.join(low) or 'none'}"
        )
    else:
        review_text = str(review)

    prompt = f"""
A PR has passed all review stages and is approved for merge.

Summary: {data.get('summary', 'N/A')}

Code Review findings:
{review_text}

Deep Policy: {data.get('deep_policy', 'N/A')}

Write a final approval gist (4-6 sentences) covering:
- What this PR does (from the summary)
- Key findings across all review types (consolidate HIGH/MEDIUM/LOW)
- Any remaining notes or caveats the merger should know
- A clear "approved to merge" sign-off
"""
    llm_summary = call_llm(prompt, system_prompt=SYSTEM)

    high_count   = len(review.get("HIGH",   [])) if isinstance(review, dict) else "?"
    medium_count = len(review.get("MEDIUM", [])) if isinstance(review, dict) else "?"
    low_count    = len(review.get("LOW",    [])) if isinstance(review, dict) else "?"

    stats = (
        f"| Severity | Count |\n"
        f"|----------|-------|\n"
        f"| 🔴 HIGH   | {high_count} |\n"
        f"| 🟡 MEDIUM | {medium_count} |\n"
        f"| 🟢 LOW    | {low_count} |\n"
    )

    return _box(
        "Final Review — Approved to Merge", "✅",
        f"{llm_summary}\n\n"
        f"### Review Stats\n{stats}"
    )
