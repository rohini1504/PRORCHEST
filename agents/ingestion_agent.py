def run(pr):
    files_data = []

    for f in pr.get_files():
        if f.patch:
            files_data.append(f"### {f.filename}\n{f.patch[:1500]}")

    if not files_data:
        return "No meaningful code changes detected"

    return "\n\n".join(files_data[:10])  # limit files
