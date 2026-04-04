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
    body = f"> `/approve-step {step}` — continue &nbsp;&nbsp; `/reject-step {step}` — halt"
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


# ── internal helpers ───────────────────────────────────────────────────────────

def _flatten_issues(lst):
    """Return list of plain issue strings from reviewer output."""
    return [i.get("issue", "") if isinstance(i, dict) else str(i) for i in lst if i]

def _join(items, sep=", "):
    cleaned = [s.strip() for s in items if s.strip()]
    return sep.join(cleaned) if cleaned else ""

def _policy_prose(raw):
    """Turn raw policy output into a readable sentence."""
    if not raw or not raw.strip():
        return "No policy issues were detected."
    lines = [ln.strip().lstrip("⚠️🔴-•").strip() for ln in raw.splitlines() if ln.strip()]
    lines = [l for l in lines if l and l.lower() != "no issues found."]
    if not lines:
        return "No policy issues were detected."
    return "Policy checks flagged: " + "; ".join(lines) + "."


# ── APPROVED — full narrative report ──────────────────────────────────────────

def build_approval_summary(data):
    """
    Called after /approve-step 8. Has access to: summary, review, deep_policy, ask_agent.
    Produces a clean narrative paragraph report — no tables, no bullet points.
    """
    summary     = (data.get("summary") or "").replace("\n", " ").strip()
    deep_policy = (data.get("deep_policy") or "").strip()
    review      = data.get("review") or {}

    high   = review.get("HIGH",   []) if isinstance(review, dict) else []
    medium = review.get("MEDIUM", []) if isinstance(review, dict) else []
    low    = review.get("LOW",    []) if isinstance(review, dict) else []
    h, m, l = len(high), len(medium), len(low)

    # Verdict
    if h > 0:
        verdict = "This PR has been **approved**, though it carries high-severity findings that should be resolved before the next production deployment."
    elif m > 0:
        verdict = "This PR has been **approved**. There are no blocking issues, though a few medium-severity observations are worth addressing in a follow-up."
    else:
        verdict = "This PR has been **approved**. The automated review found no critical or blocking issues and the code is considered safe to merge."

    # What changed
    change_para = f"**Changes:** {summary}" if summary else ""

    # Code review narrative
    all_high   = _join(_flatten_issues(high))
    all_medium = _join(_flatten_issues(medium))
    all_low    = _join(_flatten_issues(low))

    review_parts = []
    if h > 0:
        review_parts.append(f"{h} high-severity issue(s) were raised: {all_high}")
    if m > 0:
        review_parts.append(f"{m} medium-severity observation(s): {all_medium}")
    if l > 0:
        review_parts.append(f"{l} minor/low item(s): {all_low}")

    if review_parts:
        review_para = "**Code review:** " + ". ".join(review_parts) + "."
    else:
        review_para = "**Code review:** No issues were identified in the diff."

    # Policy narrative
    policy_para = f"**Policy:** {_policy_prose(deep_policy)}"

    # Assemble
    paragraphs = [p for p in [verdict, change_para, review_para, policy_para] if p]
    body = "\n\n".join(paragraphs) + "\n\n---\n_Reviewed by PR Review Bot. Merge at your discretion._"

    return _box("✅", "PR Review Complete — Approved", body)


# ── REJECTED — clear narrative explaining exactly why ─────────────────────────

def build_rejection_summary(stage, data):
    """
    Called either at Step 3 (early policy failure) or Step 8 (reviewer rejection).
    At Step 3: data has only early_policy.
    At Step 8: data has summary, review, deep_policy, ask_agent.
    Produces a clear paragraph explaining exactly why the PR was rejected.
    """
    early_policy = (data.get("early_policy") or "").strip()
    summary      = (data.get("summary") or "").replace("\n", " ").strip()
    deep_policy  = (data.get("deep_policy") or "").strip()
    review       = data.get("review") or {}

    high   = review.get("HIGH",   []) if isinstance(review, dict) else []
    medium = review.get("MEDIUM", []) if isinstance(review, dict) else []
    h, m   = len(high), len(medium)

    # Collect specific rejection reasons
    reasons = []

    # Early policy failures (missing title, description, oversized PR etc.)
    if early_policy:
        for line in early_policy.splitlines():
            line = line.strip().lstrip("❌⚠️").strip()
            if line:
                reasons.append(line)

    # High severity code issues
    for item in high:
        issue = item.get("issue", "") if isinstance(item, dict) else str(item)
        fname = item.get("file", "")  if isinstance(item, dict) else ""
        text  = issue + (f" (in `{fname}`)" if fname else "")
        if text.strip():
            reasons.append(text)

    # Medium severity if no high ones
    if not high:
        for item in medium:
            issue = item.get("issue", "") if isinstance(item, dict) else str(item)
            if issue.strip():
                reasons.append(issue)

    # Policy flags
    for ln in deep_policy.splitlines():
        ln = ln.strip().lstrip("⚠️🔴-•").strip()
        if ln and ln.lower() != "no issues found.":
            reasons.append(ln)

    # Build the rejection reason sentence
    if reasons:
        if len(reasons) == 1:
            reason_sentence = f"This PR was rejected because {reasons[0].lower()}."
        else:
            joined = "; ".join(r.rstrip(".") for r in reasons[:-1])
            reason_sentence = f"This PR was rejected because of the following: {joined}; and {reasons[-1].rstrip('.')}."
    else:
        reason_sentence = "This PR was rejected at reviewer discretion."

    # What changed (only available at step 8)
    change_sentence = f" The PR {summary.lower()}" if summary else ""

    body = (
        f"This PR did not pass the review at **{stage}**.{change_sentence}\n\n"
        f"{reason_sentence}\n\n"
        f"Please address the issues above, push a new commit, or re-open this PR to restart the review pipeline."
    )

    return _box("❌", "PR Review Complete — Rejected", body)


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
