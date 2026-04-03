from github_client import get_pr_diff
from db import save_output

def run(pr_id, pr):
    diff = get_pr_diff(pr)
    save_output(pr_id, "ingestion", diff)
    return diff
