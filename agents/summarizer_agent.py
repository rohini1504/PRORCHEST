from llm_client import call_llm

def run(diff):
    if not diff or diff.strip() == "":
        return "No PR info available"

    prompt = f"""
Summarize this pull request diff.

Focus on:
- what changed
- why it matters
- impacted areas

Be concise but informative.

DIFF:
{diff[:4000]}
"""

    return call_llm(prompt, system_prompt="You are a senior software engineer writing PR summaries.")
