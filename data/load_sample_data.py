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
        response = requests.post(
            f"{BASE_URL}/users/",
            json=user,
            timeout=30
        )
        if response.status_code == 201:
            print(f"Created user: {user['username']}")
        elif response.status_code == 400:
            print(f"User already exists: {user['username']}")
        else:
            response.raise_for_status()


def load_events(filename: str):
    events = json.loads(
        (SAMPLE_DIR / filename).read_text(encoding="utf-8")
    )

    batch_size = 100
    stored = 0

    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        response = requests.post(
            f"{BASE_URL}/ingest/events/batch",
            json={"events": batch},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        stored += result["received"]
        print(f"Batch {i // batch_size + 1}: {result['received']} stored, "
              f"{result['duplicate']} duplicate")

    print(f"Loaded {stored} events from {filename}")


def run_pipeline_step(path: str) -> dict:
    response = requests.post(f"{BASE_URL}{path}", timeout=60)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print("Creating users...")
    create_users()

    print("\nLoading normal history...")
    load_events("normal_events.json")

    print("\nNormalizing history...")
    print(run_pipeline_step("/ingest/normalize"))

    print("\nComputing clean baselines...")
    print(run_pipeline_step("/baseline/compute"))

    print("\nLoading anomalous story events...")
    load_events("anomalous_events.json")

    print("\nNormalizing anomalous events...")
    print(run_pipeline_step("/ingest/normalize"))

    print("\nGenerating alerts...")
    result = run_pipeline_step("/alerts/generate?lookback_hours=24")
    print(
        f"Findings: {result['findings_count']}, "
        f"alerts created: {result['alerts_created']}"
    )
    for alert in result["alerts"]:
        print(
            f"- [{alert['risk_level'].upper()}] "
            f"score={alert['risk_score']} {alert['title']}"
        )
