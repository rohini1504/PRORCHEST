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

    # 🔹 STEP 1: ingestion + early policy
    diff = ingestion_agent.run(pr_id, pr)
    early_policy_agent.run(pr_id, pr)

    # 🔹 STEP 2: APPROVAL 1 (SHOW MESSAGE + STOP)
    approved = approval_agent_1.run(pr_id, pr_number)

    # 🔹 SHOW CURRENT STATE
    coordinator_agent.run(pr_id, pr)

    if not approved:
        return  # ⛔ STOP HERE until approval

    # 🔹 STEP 3: MAIN AGENTS
    summarizer_agent.run(pr_id, diff)
    reviewer_agent.run(pr_id, diff)
    deep_policy_agent.run(pr_id, diff)
    ask_agent.run(pr_id)

    # 🔹 STEP 4: APPROVAL 2
    approved = approval_agent_2.run(pr_id, pr_number)

    # 🔹 SHOW UPDATED STATE
    coordinator_agent.run(pr_id, pr)

    if not approved:
        return

    # 🔹 FINAL OUTPUT
    coordinator_agent.run(pr_id, pr)


if __name__ == "__main__":
    main(int(sys.argv[1]))
