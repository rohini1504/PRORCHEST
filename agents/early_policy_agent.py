from llm_client import call_llm

def run(pr):
    flags = []

    if not pr.title or len(pr.title.strip()) < 5:
        flags.append("❌ PR title is too short or missing")

    if not pr.body or len(pr.body.strip()) < 10:
        flags.append("❌ PR description is missing or too short")

    changed_files = list(pr.get_files())
    if len(changed_files) > 20:
        flags.append(f"⚠️ Large PR — {len(changed_files)} files changed (consider splitting)")

    if pr.additions + pr.deletions > 500:
        flags.append(f"⚠️ High churn — {pr.additions + pr.deletions} total line changes")

    prompt = f"""PR Title: {pr.title}
PR Description: {pr.body or "(none)"}

List any issues with this PR's title and description in 2-3 bullet points maximum.
Each bullet must be one short sentence. No headers, no scores, no explanations.
If everything looks fine, reply with exactly: All checks passed."""

    llm_out = call_llm(prompt, system_prompt="You are a strict engineering manager. Be brief.")

    # Clean up — remove any preamble the LLM adds
    llm_lines = [
        line.strip() for line in llm_out.strip().splitlines()
        if line.strip() and not line.strip().lower().startswith(("here", "the pr", "overall", "note"))
    ]
    llm_bullets = "\n".join(llm_lines[:3])

    if flags:
        policy_section = "\n".join(flags)
        return f"{policy_section}\n\n{llm_bullets}"
    else:
        return f"✅ No policy violations\n\n{llm_bullets}"
