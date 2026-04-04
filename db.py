"""
State persistence via GitHub PR labels.

Labels used:
  pr-review:step={N}          — last completed step
  pr-review:status=rejected   — PR was rejected
  pr-review:status=running    — PR is in progress (default)

This works across GitHub Actions runs because labels live on the PR itself.
"""

from github_client import get_repo

LABEL_PREFIX = "pr-review:"


def _get_pr(pr_number):
    return get_repo().get_pull(pr_number)


def _ensure_label_exists(repo, name, color="ededed"):
    try:
        repo.get_label(name)
    except Exception:
        repo.create_label(name, color)


def _get_review_labels(pr):
    return [l.name for l in pr.get_labels() if l.name.startswith(LABEL_PREFIX)]


def _remove_labels_with_prefix(pr, repo, prefix):
    for name in _get_review_labels(pr):
        if name.startswith(prefix):
            try:
                pr.remove_from_labels(name)
            except Exception:
                pass


def init_db():
    # Nothing to initialise — labels are created on demand.
    pass


def get_state(pr_number):
    pr = _get_pr(pr_number)
    labels = _get_review_labels(pr)

    last_step = 0
    status = "running"

    for name in labels:
        key = name[len(LABEL_PREFIX):]  # strip "pr-review:"
        if key.startswith("step="):
            try:
                last_step = int(key.split("=")[1])
            except ValueError:
                pass
        elif key.startswith("status="):
            status = key.split("=")[1]

    return last_step, status


def update_state(pr_number, step, status="running"):
    pr = _get_pr(pr_number)
    repo = get_repo()

    # Remove old step + status labels
    _remove_labels_with_prefix(pr, repo, LABEL_PREFIX + "step=")
    _remove_labels_with_prefix(pr, repo, LABEL_PREFIX + "status=")

    # Add new labels
    step_label = f"{LABEL_PREFIX}step={step}"
    status_label = f"{LABEL_PREFIX}status={status}"

    _ensure_label_exists(repo, step_label, "0075ca")
    _ensure_label_exists(repo, status_label, "e4e669" if status == "running" else "d93f0b")

    pr.add_to_labels(step_label, status_label)


def save_output(pr_number, step, content):
    # Outputs are stored in the bot's running comment (coordinator already
    # does this via upsert_comment). Nothing extra needed here.
    pass


def get_all_outputs(pr_number):
    # We can't recover structured LLM outputs from labels.
    # Return empty dict — main.py will show "N/A" for un-run steps,
    # which is correct since the rejection report is built live.
    return {}
