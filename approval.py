from github_client import get_pr

BOT_MARKER = "<!-- PR_REVIEW_BOT -->"

def _human_comments(pr):
    """Return all comments NOT posted by the bot, in order."""
    return [
        c for c in pr.get_issue_comments()
        if BOT_MARKER not in c.body
    ]

def check_approval(pr_number, step):
    """Check if the latest human comment is an approve/reject for this step."""
    pr = get_pr(pr_number)
    comments = _human_comments(pr)

    if not comments:
        return None, None

    latest = comments[-1]
    body = latest.body.strip()
    user = latest.user.login

    if body.startswith(f"/approve-step {step}"):
        return "approved", user

    if body.startswith(f"/reject-step {step}"):
        return "rejected", user

    return None, None


def check_qa_comment(pr_number):
    """
    Called when status=qa. Reads the latest human comment and returns:
      ("done", user)      — user typed /done
      ("question", text)  — user asked something
      (None, None)        — no new human comment since bot last posted
    """
    pr = get_pr(pr_number)
    all_comments = list(pr.get_issue_comments())

    if not all_comments:
        return None, None

    # Find the last bot comment index
    last_bot_idx = -1
    for i, c in enumerate(all_comments):
        if BOT_MARKER in c.body:
            last_bot_idx = i

    # Any human comments AFTER the last bot comment?
    new_human = [
        c for c in all_comments[last_bot_idx + 1:]
        if BOT_MARKER not in c.body
    ]

    if not new_human:
        return None, None

    latest = new_human[-1]
    body = latest.body.strip()
    user = latest.user.login

    if body.lower().startswith("/done"):
        return "done", user

    return "question", body
