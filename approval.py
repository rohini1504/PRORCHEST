import time
from github_client import get_pr

def wait_for_approval(pr_number, step):
    pr = get_pr(pr_number)

    while True:
        comments = pr.get_issue_comments()

        for c in comments:
            body = c.body.lower()

            if f"/approve-step {step}" in body:
                return "approved", c.user.login

            if f"/reject-step {step}" in body:
                return "rejected", c.user.login

        time.sleep(10)
