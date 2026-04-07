def format_task(task):
    return f"[{task['id']}] {task['title']} ({task['status']})"


def validate_status(status):
    allowed = ["pending", "completed", "in-progress"]
    return status in allowed
