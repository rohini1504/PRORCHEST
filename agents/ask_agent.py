from llm_client import call_llm

def run(diff):
    prompt = f"""Generate 3 review questions for this PR.
Format: numbered list 1. 2. 3.
Each question: one short sentence, max 15 words.
Ask about the riskiest or most unclear parts only.
No preamble.

DIFF:
{diff[:3000]}"""

    response = call_llm(
        prompt,
        system_prompt="You are a senior reviewer. Ask sharp, specific questions."
    )

    lines = [
        line.strip() for line in response.strip().splitlines()
        if line.strip() and line.strip()[0].isdigit()
    ]
    return "\n".join(lines[:3]) if lines else response.strip().splitlines()[0]
