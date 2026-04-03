from db import save_output
from llm_client import call_llm

def run(pr_id, diff):
    summary = call_llm(f"""
Summarize this PR in 2-3 lines only.
Do not mention issues.

{diff}
""")

    save_output(pr_id, "summary", summary)
    return summary
