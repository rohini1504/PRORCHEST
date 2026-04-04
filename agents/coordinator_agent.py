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


# ── Shared renderer helpers ────────────────────────────────────────────────────

def _render_review_items(lst, show_fix):
    if not lst:
        return "_None_"
    lines = []
    for item in lst:
        if isinstance(item, dict):
            line = f"- {item.get('issue', '')}"
            fname = item.get('file', '')
            fix   = item.get('fix', '')
            if fname:
                line += f" — `{fname}`"
            lines.append(line)
            if show_fix and fix:
                lines.append(f"  ```\n  {fix}\n  ```")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _compile_review_section(review):
    high   = review.get("HIGH",   []) if isinstance(review, dict) else []
    medium = review.get("MEDIUM", []) if isinstance(review, dict) else []
    low    = review.get("LOW",    []) if isinstance(review, dict) else []
    h, m, l = len(high), len(medium), len(low)

    return high, medium, low, h, m, l


# ── APPROVED: full structured review report ────────────────────────────────────

def build_approval_summary(data):
    summary     = data.get("summary", "")     or "_Not available_"
    deep_policy = data.get("deep_policy", "") or "_No issues found_"
    ask_agent   = data.get("ask_agent", "")   or "_No questions raised_"
    review      = data.get("review", {})

    high, medium, low, h, m, l = _compile_review_section(review)

    if h > 0:
        verdict_line = f"> 🟡 **Approved with concerns** — {h} high-severity issue(s) must be addressed before shipping."
    elif m > 0:
        verdict_line = f"> 🟢 **Approved** — {m} medium issue(s) noted. Review before next release."
    else:
        verdict_line = "> 🟢 **Approved** — No critical issues found. Safe to merge."

    body = f"""{verdict_line}

&nbsp;

## 📝 What Changed
{summary}

&nbsp;

## 🔍 Code Review
| Severity | Count |
|----------|-------|
| 🔴 High | {h} |
| 🟡 Medium | {m} |
| 🟢 Low | {l} |

**🔴 High severity**
{_render_review_items(high, show_fix=True)}

**🟡 Medium severity**
{_render_review_items(medium, show_fix=True)}

**🟢 Low severity**
{_render_review_items(low, show_fix=False)}

&nbsp;

## 🛡️ Policy Check
{deep_policy}

&nbsp;

## 💬 Questions Raised During Review
{ask_agent}

&nbsp;

---
_Review completed by PR Review Bot. Merge at your discretion._"""

    return _box("✅", "PR Review Complete — Approved", body)


# ── REJECTED: clear reason report ─────────────────────────────────────────────

def build_rejection_summary(stage, data):
    summary     = data.get("summary", "")     or "_Not available_"
    deep_policy = data.get("deep_policy", "") or "_No policy issues_"
    early_policy_out = data.get("early_policy", "") or "_No early policy issues_"
    review      = data.get("review", {})

    high, medium, low, h, m, l = _compile_review_section(review)

    # Build a specific rejection reason from what actually failed
    reasons = []

    # Early policy failures (step 3 rejections)
    if data.get("early_policy"):
        for line in str(data["early_policy"]).splitlines():
            line = line.strip()
            if line.startswith("❌"):
                reasons.append(line)

    # High severity code issues
    for item in high:
        issue = item.get("issue", "") if isinstance(item, dict) else str(item)
        fname = item.get("file", "") if isinstance(item, dict) else ""
        reason = f"🔴 Code issue: {issue}"
        if fname:
            reason += f" in `{fname}`"
        reasons.append(reason)

    # Policy flags
    if deep_policy and deep_policy != "_No policy issues_":
        for line in deep_policy.splitlines():
            line = line.strip()
            if line.startswith(("⚠️", "🔴", "-", "•")):
                reasons.append(f"🛡️ Policy: {line.lstrip('-•⚠️🔴').strip()}")

    if reasons:
        reason_block = "\n".join(f"- {r}" for r in reasons)
    else:
        reason_block = "- Rejected at reviewer discretion."

    # Summary section — only show if we have data
    summary_section = ""
    if summary and summary != "_Not available_":
        summary_section = f"""
&nbsp;

## 📝 What Was in This PR
{summary}"""

    review_section = ""
    if h > 0 or m > 0:
        review_section = f"""
&nbsp;

## 🔍 Code Review Findings
**🔴 High severity**
{_render_review_items(high, show_fix=True)}

**🟡 Medium severity**
{_render_review_items(medium, show_fix=True)}"""

    body = f"""> ❌ **Rejected at: {stage}**

&nbsp;

## ❌ Reason for Rejection
This PR was rejected because:

{reason_block}
{summary_section}
{review_section}

&nbsp;

## 🛡️ Policy Check
{deep_policy}

&nbsp;

---
_Fix the issues above and push a new commit, or re-open this PR to restart the review._"""

    return _box("❌", f"PR Review Complete — Rejected at {stage}", body)


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
