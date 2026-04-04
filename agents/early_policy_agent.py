from llm_client import call_llm

def run(pr):
    issues = []

    if not pr.title or len(pr.title.strip()) < 5:
        issues.append("PR title too short")

    if not pr.body or len(pr.body.strip()) < 10:
        issues.append("PR description missing or too short")

    prompt = f"""
Evaluate this PR metadata:

Title: {pr.title}
Description: {pr.body}

Check for:
- clarity
- completeness
- professionalism

Return short bullet points.
"""

    llm_feedback = call_llm(prompt, system_prompt="You are a strict engineering manager.")

    result = "\n".join(issues) if issues else "No basic policy violations"

    return f"{result}\n\nLLM Feedback:\n{llm_feedback}"
