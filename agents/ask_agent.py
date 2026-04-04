from llm_client import call_llm

def run(diff):
    prompt = f"""
Generate developer questions for this PR.

Focus on:
- edge cases
- performance
- missing tests
- design decisions

Return 5-7 sharp questions.

DIFF:
{diff[:3000]}
"""

    return call_llm(prompt, system_prompt="You are a senior reviewer preparing PR discussion questions.")
