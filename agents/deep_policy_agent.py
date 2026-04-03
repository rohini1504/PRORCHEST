from db import save_output

def run(pr_id, diff):
    issues = []

    if "print(" in diff:
        issues.append("⚠️ Debug print statements found")

    if len(diff) < 20:
        issues.append("⚠️ Very small PR")

    result = "\n".join(issues) if issues else "✅ Code follows policies"
    save_output(pr_id, "deep_policy", result)
    return result
