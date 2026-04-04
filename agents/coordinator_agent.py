def build_report(data):
    sections = ["## 🤖 PR Review Report"]

    for key, value in data.items():
        if not value:
            continue

        if key == "review" and isinstance(value, dict):
            formatted = f"""
HIGH:
{chr(10).join(value.get("HIGH", []))}

MEDIUM:
{chr(10).join(value.get("MEDIUM", []))}

LOW:
{chr(10).join(value.get("LOW", []))}
"""
            sections.append(f"\n### {key}\n{formatted}")
        else:
            sections.append(f"\n### {key}\n{value}")

    return "\n".join(sections)
