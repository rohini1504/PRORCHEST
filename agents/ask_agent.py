from llm_client import call_llm

def run(diff):
    prompt = f"""Generate exactly 3 clarification questions for this PR.
Each question must be one sentence. Focus on the most important unknowns only.
Reply as a plain numbered list 1. 2. 3. — nothing else.

DIFF:
{diff[:3000]}"""

    response = call_llm(
        prompt,
        system_prompt="You are a senior reviewer asking sharp, specific questions."
    )

    # Keep only numbered lines
    lines = [
        line.strip() for line in response.strip().splitlines()
        if line.strip() and line.strip()[0].isdigit()
    ]
    return "\n".join(lines[:3]) if lines else response.strip().splitlines()[0]
