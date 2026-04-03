from db import save_output
from llm_client import call_llm

def run(pr_id, diff):
    review = call_llm(f"""
You are a senior code reviewer.

Return STRICT format:

HIGH:
- ...

MEDIUM:
- ...

LOW:
- ...

No explanations.

{diff}
""")

    save_output(pr_id, "review", review)
    return review
