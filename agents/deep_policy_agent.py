from db import save_output

def run(pr_id, diff):
    issues = []

    if "print(" in diff:
        issues.append("⚠️ Debug statements present")

    if "== None" in diff:
        issues.append("⚠️ Use 'is None' instead")

    result = "\n".join(issues) if issues else "✅ No violations"
    save_output(pr_id, "deep_policy", result)
    return result
