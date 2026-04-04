from github import Github
import os

MARKER = "<!-- PR_REVIEW_BOT -->"

def get_client():
    return Github(os.getenv("GITHUB_TOKEN"))

def get_repo():
    return get_client().get_repo(os.getenv("GITHUB_REPOSITORY"))

def get_pr(pr_number):
    return get_repo().get_pull(pr_number)

def get_latest_comment(pr):
    comments = list(pr.get_issue_comments())
    return comments[-1].body if comments else ""

def upsert_comment(pr, body):
    comments = list(pr.get_issue_comments())

    for c in comments:
        if MARKER in c.body:
            c.edit(MARKER + "\n" + body)
            return

    pr.create_issue_comment(MARKER + "\n" + body)
