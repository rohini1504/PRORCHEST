import os
from github import Github

def get_repo():
    g = Github(os.getenv("GITHUB_TOKEN"))
    return g.get_repo(os.getenv("REPO_NAME"))

def get_pr(pr_number):
    return get_repo().get_pull(pr_number)

def get_pr_diff(pr):
    files = pr.get_files()
    diff = ""
    for f in files:
        diff += f"\nFile: {f.filename}\n{f.patch}\n"
    return diff

def post_comment(pr, message):
    pr.create_issue_comment(message)
