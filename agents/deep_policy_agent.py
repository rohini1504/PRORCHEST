from llm_client import call_llm

def run(diff):
    issues = []

    if "print(" in diff:
        issues.append("Debug print found")

    if "console.log" in diff:
        issues.append("Console log found")

    if "TODO" in diff:
        issues.append("TODO left in code")

    prompt = f"""
Analyze this diff for bad practices:

- security risks
- anti-patterns
- performance issues

Return bullet points.

DIFF:
{diff[:3000]}
"""

    llm_output = call_llm(prompt, system_prompt="You are a strict static analysis expert.")

    static_part = "\n".join(issues) if issues else "No obvious static issues"

    return f"{static_part}\n\nLLM Analysis:\n{llm_output}"
