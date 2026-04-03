from db import get_outputs
from github_client import post_comment

def run(pr_id, pr):
    outputs = get_outputs(pr_id)

    final = "## 🤖 PR Review Report\n\n"

    for agent, output in outputs:
        final += f"### {agent}\n{output}\n\n"

    post_comment(pr, final)
