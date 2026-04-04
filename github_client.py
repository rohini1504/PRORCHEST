import os
from github import Github

COMMENT_MARKER = "<!-- PR_REVIEW_BOT_COMMENT -->"


def get_repo():
    g = Github(os.getenv("GITHUB_TOKEN"))
    return g.get_repo(os.getenv("REPO_NAME"))


def get_pr(pr_number):
    return get_repo().get_pull(pr_number)


def get_pr_diff(pr):
    files = pr.get_files()
    diff = ""

    for f in files:
        if f.patch:
            diff += f"\nFile: {f.filename}\n{f.patch}\n"

    return diff if diff else "No meaningful code changes detected"


def upsert_comment(pr, message):
    """
    Update existing bot comment OR create new one
    """

    comments = pr.get_issue_comments()

    for comment in comments:
        if COMMENT_MARKER in comment.body:
            comment.edit(COMMENT_MARKER + "\n" + message)
            return

    # if not found → create new
    pr.create_issue_comment(COMMENT_MARKER + "\n" + message)
