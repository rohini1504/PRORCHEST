from db import get_outputs
from github_client import upsert_comment


def run(pr_id, pr):
    outputs = dict(get_outputs(pr_id))

    comment = "## 🤖 PR Review Report\n\n"

    if "ingestion" in outputs:
        comment += f"### ingestion\n{outputs['ingestion'][:200]}...\n\n"

    if "early_policy" in outputs:
        comment += f"### early_policy\n{outputs['early_policy']}\n\n"

    if "approval_step_3" in outputs:
        comment += f"### approval_step_3\n{outputs['approval_step_3']}\n\n"

    if "summary" in outputs:
        comment += f"### summary\n{outputs['summary']}\n\n"

    if "review" in outputs:
        comment += f"### review\n{outputs['review']}\n\n"

    if "deep_policy" in outputs:
        comment += f"### deep_policy\n{outputs['deep_policy']}\n\n"

    if "ask_agent" in outputs:
        comment += f"### ask_agent\n{outputs['ask_agent']}\n\n"

    if "approval_step_8" in outputs:
        comment += f"### approval_step_8\n{outputs['approval_step_8']}\n\n"

    # 🔥 ALWAYS update same comment
    upsert_comment(pr, comment)
