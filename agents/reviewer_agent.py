from llm_client import call_llm
import json

def run(diff):
    prompt = f"""
Review the following code diff.

Return STRICT JSON in this format:

{{
  "HIGH": ["..."],
  "MEDIUM": ["..."],
  "LOW": ["..."]
}}

Rules:
- HIGH = bugs, security issues
- MEDIUM = logic flaws, bad patterns
- LOW = style, readability

DIFF:
{diff[:4000]}
"""

    response = call_llm(prompt, system_prompt="You are a strict senior code reviewer.")

    try:
        parsed = json.loads(response)
    except:
        parsed = {
            "HIGH": [],
            "MEDIUM": ["LLM output parsing failed"],
            "LOW": []
        }

    return parsed
