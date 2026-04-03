import sys
from github_client import get_pr
from agents import ingestion_agent, summarizer_agent, reviewer_agent, coordinator_agent

def main(pr_number):
    pr = get_pr(pr_number)
    pr_id = str(pr_number)

    diff = ingestion_agent.run(pr_id, pr)
    summarizer_agent.run(pr_id, diff)
    reviewer_agent.run(pr_id, diff)
    coordinator_agent.run(pr_id, pr)

if __name__ == "__main__":
    main(int(sys.argv[1]))
