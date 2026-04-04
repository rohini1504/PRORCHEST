from github_client import get_pr

def check_approval(pr_number, step):
    pr = get_pr(pr_number)
    comments = list(pr.get_issue_comments())

    if not comments:
        return None, None

    latest = comments[-1]
    body = latest.body.strip()
    user = latest.user.login

    if body.startswith(f"/approve-step {step}"):
        return "approved", user

    if body.startswith(f"/reject-step {step}"):
        return "rejected", user

    return None, None
