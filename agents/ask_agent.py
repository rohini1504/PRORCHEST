from db import save_output

def run(pr_id):
    questions = """- What is expected behavior?
- Are edge cases handled?
- Is input validated?"""

    save_output(pr_id, "ask_agent", questions)
    return questions
