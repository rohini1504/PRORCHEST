
def render_summary(entries):
    total = len(entries)
    closed = len([e for e in entries if e["status"] == "closed"])

    return f"Total: {total}, Closed: {closed}"
