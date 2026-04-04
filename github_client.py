from github import Github
import os

BOT_MARKER = "<!-- PR_REVIEW_BOT -->"

def get_client():
    return Github(os.getenv("GITHUB_TOKEN"))

def get_repo():
    return get_client().get_repo(os.getenv("GITHUB_REPOSITORY"))

def get_pr(pr_number):
    return get_repo().get_pull(pr_number)

def get_latest_comment(pr):
    comments = list(pr.get_issue_comments())
    return comments[-1].body if comments else ""

def _agent_marker(agent_name):
    return f"<!-- PR_BOT_AGENT:{agent_name} -->"

def post_agent_box(pr, agent_name, content):
    """Post a new comment box for this agent. Skip if already posted."""
    marker = _agent_marker(agent_name)
    for c in pr.get_issue_comments():
        if marker in c.body:
            return  # already posted, never replace

    pr.create_issue_comment(f"{BOT_MARKER}\n{marker}\n{content}")

def post_comment(pr, content):
    """Always post a new comment (used for coordinator summaries)."""
    pr.create_issue_comment(f"{BOT_MARKER}\n{content}")

# kept for backwards compat if anything still imports it
def upsert_comment(pr, body):
    post_comment(pr, body)
