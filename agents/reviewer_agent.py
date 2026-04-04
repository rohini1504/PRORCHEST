from llm_client import call_llm
import json
import re

def run(diff):
    prompt = f"""Review this code diff. Reply ONLY with a JSON object, no other text.

Format:
{{"HIGH": ["..."], "MEDIUM": ["..."], "LOW": ["..."]}}

Rules:
- HIGH: bugs, crashes, security vulnerabilities
- MEDIUM: logic flaws, missing error handling, bad patterns
- LOW: style, naming, readability
- Each item must be one sentence under 15 words
- Empty list [] if nothing found at that level
- Maximum 3 items per level

DIFF:
{diff[:4000]}"""

    response = call_llm(
        prompt,
        system_prompt="You are a strict code reviewer. Reply only with the JSON object, nothing else."
    )

    # Strip markdown code fences if model wraps in ```json ... ```
    clean = re.sub(r"```(?:json)?|```", "", response).strip()

    try:
        parsed = json.loads(clean)
        # Ensure all keys exist and are lists
        return {
            "HIGH":   [str(i) for i in parsed.get("HIGH",   [])[:3]],
            "MEDIUM": [str(i) for i in parsed.get("MEDIUM", [])[:3]],
            "LOW":    [str(i) for i in parsed.get("LOW",    [])[:3]],
        }
    except Exception:
        return {"HIGH": [], "MEDIUM": ["Could not parse review output"], "LOW": []}
