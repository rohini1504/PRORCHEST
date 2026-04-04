import sys
from github_client import get_pr
from db import clear_outputs

from agents import (
    ingestion_agent,
    early_policy_agent,
    approval_agent_1,
    summarizer_agent,
    reviewer_agent,
    deep_policy_agent,
    ask_agent,
    approval_agent_2,
    coordinator_agent
)


def main(pr_number):
    pr = get_pr(pr_number)
    pr_id = str(pr_number)

    clear_outputs(pr_id)

    # STEP 1
    diff = ingestion_agent.run(pr_id, pr)
    early_policy_agent.run(pr_id, pr)

    approved = approval_agent_1.run(pr_id, pr_number)

    # 🔥 ALWAYS SHOW REPORT
    coordinator_agent.run(pr_id, pr)

    if not approved:
        return

    # STEP 2
    summarizer_agent.run(pr_id, diff)
    reviewer_agent.run(pr_id, diff)
    deep_policy_agent.run(pr_id, diff)
    ask_agent.run(pr_id)

    approved = approval_agent_2.run(pr_id, pr_number)

    # 🔥 UPDATE REPORT AGAIN
    coordinator_agent.run(pr_id, pr)

    if not approved:
        return

    # FINAL
    coordinator_agent.run(pr_id, pr)


if __name__ == "__main__":
    main(int(sys.argv[1]))
