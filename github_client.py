from github import Github
import os
import base64

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

def _data_marker(agent_name):
    return f"<!-- PR_BOT_DATA:{agent_name}:"

def post_agent_box(pr, agent_name, content, raw_data=None):
    """
    Post a comment box for this agent. Skip if already posted.
    Returns True if a new comment was created, False if skipped.
    raw_data: optional string to store invisibly for later retrieval.
              Stored as base64 inside an HTML comment so it survives
              across runs without any DB.
    """
    marker = _agent_marker(agent_name)
    for c in pr.get_issue_comments():
        if marker in c.body:
            return False  # already posted, never replace

    hidden = ""
    if raw_data is not None:
        encoded = base64.b64encode(raw_data.encode()).decode()
        hidden = f"\n{_data_marker(agent_name)}{encoded}-->"

    pr.create_issue_comment(f"{BOT_MARKER}\n{marker}{hidden}\n{content}")
    return True

def read_output(pr, agent_name):
    """
    Retrieve the raw_data stored by post_agent_box for a given agent.
    Returns None if not found.
    """
    marker = _agent_marker(agent_name)
    data_prefix = _data_marker(agent_name)

    for c in pr.get_issue_comments():
        if marker not in c.body:
            continue
        for line in c.body.splitlines():
            if line.startswith(data_prefix):
                encoded = line[len(data_prefix):].rstrip("-->").strip()
                try:
                    return base64.b64decode(encoded.encode()).decode()
                except Exception:
                    return None
    return None

def post_comment(pr, content):
    """Always post a new comment (used for coordinator summaries)."""
    pr.create_issue_comment(f"{BOT_MARKER}\n{content}")

def upsert_comment(pr, body):
    post_comment(pr, body)
