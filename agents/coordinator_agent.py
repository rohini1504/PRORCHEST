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
    return _box("⏳", f"Awaiting Approval", body)

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

def format_ask_agent(result):
    return _box("💬", "Questions for Author", result)


# ── Terminal summaries ─────────────────────────────────────────────────────────

def build_rejection_summary(stage, data):
    context = ""
    if data.get("early_policy"):
        context += f"Policy: {data['early_policy']}\n"
    if data.get("summary"):
        context += f"Summary: {data['summary']}\n"
    if data.get("review") and isinstance(data["review"], dict):
        high = [i.get("issue","") if isinstance(i,dict) else i for i in data["review"].get("HIGH",[])]
        if high:
            context += "High issues: " + ", ".join(high) + "\n"

    prompt = f"""PR rejected at: {stage}
Findings: {context[:800]}
Write ONE sentence: why it was rejected and what to fix. No fluff."""

    summary = call_llm(prompt, system_prompt=SYSTEM)
    body = f"{summary}\n\n_Push a fix or re-open to restart._"
    return _box("❌", f"Rejected — {stage}", body)


def build_approval_summary(data):
    review = data.get("review", {})
    high   = review.get("HIGH",   []) if isinstance(review, dict) else []
    medium = review.get("MEDIUM", []) if isinstance(review, dict) else []
    low    = review.get("LOW",    []) if isinstance(review, dict) else []

    def issues_text(lst):
        return ", ".join(
            i.get("issue","") if isinstance(i,dict) else str(i) for i in lst
        ) or "none"

    prompt = f"""PR approved. Summary: {data.get('summary','N/A')}
High: {issues_text(high)} | Medium: {issues_text(medium)}
Write ONE sentence sign-off noting any caveats. Start with "Approved —"."""

    summary = call_llm(prompt, system_prompt=SYSTEM)

    h = len(high); m = len(medium); l = len(low)
    badge_h = f"🔴 {h}" if h else f"🔴 0"
    badge_m = f"🟡 {m}" if m else f"🟡 0"
    badge_l = f"🟢 {l}" if l else f"🟢 0"

    body = f"{summary}\n\n{badge_h} &nbsp; {badge_m} &nbsp; {badge_l}"
    return _box("✅", "Approved — Ready to Merge", body)
