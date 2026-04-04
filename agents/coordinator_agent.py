from llm_client import call_llm

SYSTEM = "You are a senior engineering lead. Be concise and direct."

def _box(emoji, title, body):
    return f"### {emoji} {title}\n---\n{body}\n"


# ── Per-agent formatters ───────────────────────────────────────────────────────

def format_ingestion(result):
    return _box("📥", "Ingestion", result["metadata"])

def format_early_policy(result):
    return _box("📋", "Early Policy", result)

def format_waiting_approval(step):
    body = (
        f"> `/approve-step {step}` — continue &nbsp;&nbsp; `/reject-step {step}` — halt"
    )
    return _box("⏳", "Awaiting Approval", body)

def format_approval_granted(step, user):
    return _box("✅", f"Step {step} Approved by {user}", "Pipeline continuing.")

def format_summary(result):
    return _box("📝", "Summary", result)

def format_review(result):
    def render_items(lst, show_fix):
        if not lst:
            return "_None_"
        lines = []
        for item in lst:
            if isinstance(item, dict):
                issue = item.get("issue", "")
                fname = item.get("file", "")
                fix   = item.get("fix", "")
                line  = f"- {issue}"
                if fname:
                    line += f" — `{fname}`"
                lines.append(line)
                if show_fix and fix:
                    lines.append(f"  ```\n  {fix}\n  ```")
            else:
                lines.append(f"- {item}")
        return "\n".join(lines)

    body = (
        f"**🔴 High**\n{render_items(result.get('HIGH', []), show_fix=True)}\n\n"
        f"**🟡 Medium**\n{render_items(result.get('MEDIUM', []), show_fix=True)}\n\n"
        f"**🟢 Low**\n{render_items(result.get('LOW', []), show_fix=False)}"
    )
    return _box("🔍", "Code Review", body)

def format_deep_policy(result):
    return _box("🛡️", "Policy Check", result)


# ── Terminal summaries ─────────────────────────────────────────────────────────

def build_rejection_summary(stage, data):
    context = ""
    if data.get("early_policy"):
        context += f"Policy: {data['early_policy']}\n"
    if data.get("summary"):
        context += f"Summary: {data['summary']}\n"
    if data.get("review") and isinstance(data["review"], dict):
        high = [i.get("issue", "") if isinstance(i, dict) else i for i in data["review"].get("HIGH", [])]
        if high:
            context += "High issues: " + ", ".join(high) + "\n"

    prompt = f"""PR rejected at: {stage}
Findings: {context[:800]}
Write ONE sentence: why it was rejected and what to fix. No fluff."""

    summary = call_llm(prompt, system_prompt=SYSTEM)
    body = f"{summary}\n\n_Push a fix or re-open to restart._"
    return _box("❌", f"Rejected — {stage}", body)


def build_approval_summary(data):
    """
    Build the final approval comment without any LLM call.
    Previously called call_llm() here, which added up to 21 s of
    latency (15 s timeout × up to 3 retries) on every approval.
    The sign-off is now generated deterministically from the cached
    review data that is already stored in PR comments.
    """
    review = data.get("review", {})
    high   = review.get("HIGH",   []) if isinstance(review, dict) else []
    medium = review.get("MEDIUM", []) if isinstance(review, dict) else []
    low    = review.get("LOW",    []) if isinstance(review, dict) else []

    h = len(high); m = len(medium); l = len(low)

    # Deterministic sign-off — no LLM required
    if h > 0:
        issues = ", ".join(i.get("issue", "") if isinstance(i, dict) else str(i) for i in high)
        sign_off = f"Approved — address {h} high-severity issue(s) before shipping: {issues}."
    elif m > 0:
        sign_off = f"Approved — {m} medium issue(s) noted; review before next release."
    else:
        sign_off = "Approved — no critical issues found. Safe to merge."

    badge_h = f"🔴 {h}"
    badge_m = f"🟡 {m}"
    badge_l = f"🟢 {l}"

    body = f"{sign_off}\n\n{badge_h} &nbsp; {badge_m} &nbsp; {badge_l}"
    return _box("✅", "Approved — Ready to Merge", body)


# ── Q&A formatters ────────────────────────────────────────────────────────────

def format_ask_agent(questions):
    body = (
        f"{questions}\n\n"
        f"---\n"
        f"💬 **Ask me anything about this PR** — reply with your question.\n"
        f"Type `/done` when you're ready to proceed to final approval."
    )
    return _box("💬", "Questions for Author", body)

def format_qa_answer(question, answer):
    body = f"**Q:** {question}\n\n**A:** {answer}"
    return _box("🤖", "Answer", body)

def format_qa_done(user):
    return _box("✅", "Q&A Complete", f"Proceeding to final approval. Thanks {user}.")
