from db import save_output
from llm_client import call_llm

def run(pr_id, diff):
    review = call_llm(f"Review this code and find issues:\n{diff}")
    save_output(pr_id, "review", review)
    return review
