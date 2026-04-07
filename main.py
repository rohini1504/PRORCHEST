from tasks import TaskManager

def run_demo():
    manager = TaskManager()
    manager.add_task("Write code")
    manager.add_task("Review PR")

    tasks = manager.get_tasks()

    for t in tasks:
        print(f"{t['id']}: {t['title']} - {t['status']}")

if __name__ == "__main__":
    run_demo()
