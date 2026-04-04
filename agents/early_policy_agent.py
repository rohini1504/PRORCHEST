def run(pr):
    issues = []

    if not pr.title or len(pr.title) < 5:
        issues.append("PR title too short")

    if not pr.body:
        issues.append("PR description missing")

    return "\n".join(issues) if issues else "No policy violations"
