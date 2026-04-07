
from pipeline_unit import PipelineUnit

def boot():
    pipeline = PipelineUnit()
    pipeline.create_entry("Implement feature A", "high")
    pipeline.create_entry("Fix bug B", "medium")

    entries = pipeline.get_entries()

    print("\n=== DEVFLOW TASKS ===")
    for e in entries:
        print(f"{e['id']} | {e['title']} | {e['priority']} | {e['status']}")

if __name__ == "__main__":
    boot()
