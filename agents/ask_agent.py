from db import save_output

def run(pr_id):
    questions = [
        "Why was this change made?",
        "Are there test cases?",
        "Any edge cases handled?"
    ]

    result = "\n".join(questions)
    save_output(pr_id, "ask_agent", result)
    return result
