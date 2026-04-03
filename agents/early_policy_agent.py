from db import save_output

def run(pr_id, pr):
    issues = []

    if not pr.body:
        issues.append("❌ Missing PR description")

    if pr.changed_files > 10:
        issues.append("⚠️ Large PR size")

    result = "\n".join(issues) if issues else "✅ No early policy issues"
    save_output(pr_id, "early_policy", result)
    return result
