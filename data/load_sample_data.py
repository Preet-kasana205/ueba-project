import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

BASE_URL = "http://localhost:8000/api/v1"

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
        r = requests.post(f"{BASE_URL}/users", json=user)
        if r.status_code == 201:
            print(f"Created user: {user['username']}")
        else:
            print(f"User exists or error: {user['username']} - {r.json()}")


def load_events():
    with open("data/sample_logs/events.json") as f:
        events = json.load(f)

    # Send in batches of 100
    batch_size = 100
    total_batches = 0

    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        r = requests.post(
            f"{BASE_URL}/ingest/events/batch",
            json={"events": batch}
        )
        result = r.json()
        total_batches += 1
        print(f"Batch {total_batches}: {result['received']} stored, "
              f"{result['duplicate']} duplicate")

    print(f"\nDone. {total_batches} batches sent.")


if __name__ == "__main__":
    print("Creating users...")
    create_users()
    print("\nLoading events...")
    load_events()