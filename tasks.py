class TaskManager:
    def __init__(self):
        self.tasks = []
        self.counter = 1

    def add_task(self, title):
        task = {
            "id": self.counter,
            "title": title,
            "status": "pending"
        }
        self.tasks.append(task)
        self.counter += 1
        return task

    def get_tasks(self):
        return self.tasks

    def update_status(self, task_id, status):
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = status
                return task
        
