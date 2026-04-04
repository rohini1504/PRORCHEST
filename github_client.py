import os
from github import Github

MARKER = "<!-- PR_REVIEW_BOT -->"


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
    Always keep ONE bot comment.
    Update if exists, else create.
    """
    try:
        comments = pr.get_issue_comments()

        for c in comments:
            if MARKER in c.body:
                c.edit(f"{MARKER}\n{message}")
                return

        pr.create_issue_comment(f"{MARKER}\n{message}")

    except Exception as e:
        print("COMMENT ERROR:", str(e))
