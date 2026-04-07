
from state_manager import StateManager
from priority_guard import PriorityGuard

class PipelineUnit:
    def __init__(self):
        self.store = []
        self.counter = 1
        self.guard = PriorityGuard()

    def create_entry(self, title, priority):
        if not self.guard.validate(priority):
            raise ValueError("Invalid priority")

        entry = {
            "id": self.counter,
            "title": title,
            "priority": priority,
            "status": "open"
        }

        self.store.append(entry)
        self.counter += 1
        return entry

    

    def update_status(self, entry_id, status):
        for e in self.store:
            if e["id"] == entry_id:
                e["status"] = status
                return e
        return None
