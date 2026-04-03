from db import get_outputs
from github_client import post_comment

def run(pr_id, pr):
    outputs = dict(get_outputs(pr_id))

    comment = "## 🤖 PR Review Report\n\n"

    comment += f"### ingestion\n{outputs.get('ingestion','')[:200]}...\n\n"
    comment += f"### early_policy\n{outputs.get('early_policy','')}\n\n"
    comment += f"### approval_step_3\n{outputs.get('approval_step_3','')}\n\n"
    comment += f"### summary\n{outputs.get('summary','')}\n\n"
    comment += f"### review\n{outputs.get('review','')}\n\n"
    comment += f"### deep_policy\n{outputs.get('deep_policy','')}\n\n"
    comment += f"### ask_agent\n{outputs.get('ask_agent','')}\n\n"
    comment += f"### approval_step_8\n{outputs.get('approval_step_8','')}\n"

    post_comment(pr, comment)
