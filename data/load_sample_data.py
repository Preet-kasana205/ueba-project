import json
import os
from pathlib import Path
import requests

BASE_URL = os.getenv("UEBA_API_URL", "http://localhost:8000/api/v1")
SAMPLE_DIR = Path("data/sample_logs")


def create_users():
    users = [
        {"external_id": "AD\\preet.kasana", "username": "preet.kasana",
         "department": "Engineering", "role": "developer"},
        {"external_id": "AD\\john.smith", "username": "john.smith",
         "department": "Finance", "role": "analyst"},
        {"external_id": "AD\\sara.jones", "username": "sara.jones",
         "department": "HR", "role": "hr_manager"},
    ]
    for user in users:
        r = requests.post(f"{BASE_URL}/users", json=user, timeout=30)
        if r.status_code == 201:
            print(f"Created user: {user['username']}")
        elif r.status_code == 400:
            print(f"User already exists: {user['username']}")


def load_events():
    events = json.loads(
        (SAMPLE_DIR / "events.json").read_text(encoding="utf-8")
    )
    batch_size = 100
    stored = 0

    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        r = requests.post(
            f"{BASE_URL}/ingest/events/batch",
            json={"events": batch},
            timeout=30
        )
        result = r.json()
        stored += result["received"]
        print(f"Batch {i // batch_size + 1}: "
              f"{result['received']} stored, "
              f"{result['duplicate']} duplicate")

    print(f"Total stored: {stored} events")


def run_step(path: str, label: str):
    print(f"\n{label}...")
    r = requests.post(f"{BASE_URL}{path}", timeout=60)
    print(r.json())


if __name__ == "__main__":
    print("Creating users...")
    create_users()

    print("\nLoading events...")
    load_events()

    run_step("/ingest/normalize", "Normalizing events")
    run_step("/baseline/compute", "Computing baseline")
    run_step("/detection/run", "Running detection")
    run_step("/alerts/generate", "Generating alerts")

    print("\nDone. Open http://localhost:8501 to see the dashboard.")