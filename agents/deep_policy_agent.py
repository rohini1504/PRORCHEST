from llm_client import call_llm

def run(diff):
    static_flags = []

    checks = [
        ("print(",      "⚠️ Debug `print()` statement found"),
        ("console.log", "⚠️ `console.log` left in code"),
        ("TODO",        "⚠️ Unresolved `TODO` comment"),
        ("FIXME",       "⚠️ Unresolved `FIXME` comment"),
        ("hardcoded",   "⚠️ Possible hardcoded value"),
        ("password",    "🔴 Possible hardcoded credential"),
        ("secret",      "🔴 Possible hardcoded secret"),
    ]

    for pattern, message in checks:
        if pattern.lower() in diff.lower():
            static_flags.append(message)

    prompt = f"""Analyze this diff for code quality issues.
Reply with 3-5 bullet points ONLY. One sentence each. No headers, no sub-points.
Cover: security risks, anti-patterns, missing tests, naming issues.
If nothing notable, reply: No significant policy violations found.

DIFF:
{diff[:3000]}"""

    llm_out = call_llm(prompt, system_prompt="You are a static analysis expert. Be concise.")

    # Keep only bullet lines
    llm_lines = [
        line.strip() for line in llm_out.strip().splitlines()
        if line.strip() and (line.strip().startswith(("-", "•", "*", "–")) or line.strip()[0].isdigit())
    ]
    llm_section = "\n".join(llm_lines[:5]) if llm_lines else llm_out.strip().splitlines()[0]

    if static_flags:
        return "\n".join(static_flags) + "\n\n" + llm_section
    return llm_section
