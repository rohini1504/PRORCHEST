from tasks import TaskManager
from utils import validate_status

def test_add_task():
    manager = TaskManager()
    task = manager.add_task("Test task")
    assert task["title"] == "Test task"

def test_update_status():
    manager = TaskManager()
    task = manager.add_task("Update me")
    updated = manager.update_status(task["id"], "completed")
    assert updated["status"] == "completed"

def test_validate_status():
    assert validate_status("pending")
    assert not validate_status("wrong")

if __name__ == "__main__":
    test_add_task()
    test_update_status()
    test_validate_status()
    print("All tests passed!")
