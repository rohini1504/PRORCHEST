def run(pr):
    files_data = []

    for f in pr.get_files():
        if f.patch:
            files_data.append(f"### {f.filename}\n{f.patch[:2000]}")

    return "\n\n".join(files_data) if files_data else "No changes detected"
