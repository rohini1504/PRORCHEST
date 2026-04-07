import requests

BASE = "http://127.0.0.1:8000"

def run():
    print("Creating task...")
    t = requests.post(f"{BASE}/tasks", json={"title":"Demo","description":"Test"})
    print(t.json())

    print("Listing tasks...")
    print(requests.get(f"{BASE}/tasks").json())

    print("Filtering pending...")
    print(requests.get(f"{BASE}/tasks/status/pending").json())

if __name__ == "__main__":
    run()
