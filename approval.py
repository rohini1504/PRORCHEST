from github_client import get_pr

def check_approval(pr_number, step):
    pr = get_pr(pr_number)
    comments = list(pr.get_issue_comments())

    if not comments:
        return None, None

    # ✅ ONLY CHECK LATEST COMMENT
    last_comment = comments[-1]
    body = last_comment.body.lower().strip()

    if f"/approve-step {step}" in body:
        return "approved", last_comment.user.login

    if f"/reject-step {step}" in body:
        return "rejected", last_comment.user.login

    return None, None
