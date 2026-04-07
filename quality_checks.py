
def check_empty_titles(entries):
    return [e for e in entries if not e["title"]]


def check_high_priority(entries):
    return [e for e in entries if e["priority"] == "high"]
