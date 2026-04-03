from github_client import get_pr


def check_approval(pr_number, step):
    pr = get_pr(pr_number)
    comments = pr.get_issue_comments()

    for comment in comments:
        body = comment.body.lower().strip()

        if f"/approve-step {step}" in body:
            return "approved", comment.user.login

        if f"/reject-step {step}" in body:
            return "rejected", comment.user.login

    return None, None
