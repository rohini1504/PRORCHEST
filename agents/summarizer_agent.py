from llm_client import call_llm

def run(diff):
    if not diff or diff.strip() == "":
        return "No code changes to summarize."

    prompt = f"""Summarize this PR diff in exactly 3 sentences:
1. What was changed.
2. Why it likely matters.
3. Which areas of the codebase are affected.

No bullet points. No headers. Plain prose only.

DIFF:
{diff[:4000]}"""

    return call_llm(prompt, system_prompt="You are a senior engineer writing concise PR summaries.")
