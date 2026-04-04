from llm_client import call_llm

def run(diff):
    flags = []

    checks = [
        ("print(",      "⚠️ `print()` debug statement"),
        ("console.log", "⚠️ `console.log` debug statement"),
        ("TODO",        "⚠️ Unresolved TODO"),
        ("FIXME",       "⚠️ Unresolved FIXME"),
        ("password",    "🔴 Possible hardcoded credential"),
        ("secret",      "🔴 Possible hardcoded secret"),
        ("token",       "⚠️ Hardcoded token reference"),
    ]

    for pattern, message in checks:
        if pattern.lower() in diff.lower():
            flags.append(message)

    prompt = f"""Check this diff for policy issues. Reply with max 3 bullet points.
Each bullet: one short phrase only (under 10 words). No sentences. No explanations.
Topics: security, naming, missing tests, docs.
If nothing notable, reply with exactly: No issues found.

DIFF:
{diff[:3000]}"""

    llm_out = call_llm(prompt, system_prompt="You are a static analysis tool. Be terse.")

    # Only keep actual bullet lines
    llm_lines = [
        line.strip() for line in llm_out.strip().splitlines()
        if line.strip() and line.strip()[0] in "-•*–" or
        (len(line.strip()) > 0 and line.strip()[0].isdigit() and "." in line.strip()[:3])
    ]
    llm_section = "\n".join(llm_lines[:3]) if llm_lines else llm_out.strip().splitlines()[0]

    if flags:
        return "\n".join(flags) + "\n" + llm_section
    return llm_section
