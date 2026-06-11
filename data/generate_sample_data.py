import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUTPUT_DIR = Path("data/sample_logs")

USERS = [
    {"username": "preet.kasana", "department": "Engineering", "normal_hours": (9, 18)},
    {"username": "john.smith", "department": "Finance", "normal_hours": (8, 17)},
    {"username": "sara.jones", "department": "HR", "normal_hours": (9, 17)},
]

DEVICES = {
    "preet.kasana": ["LAPTOP-DEV-01", "LAPTOP-DEV-02"],
    "john.smith": ["LAPTOP-FIN-01"],
    "sara.jones": ["LAPTOP-HR-01"],
}

IPS = {
    "preet.kasana": ["192.168.1.101", "192.168.1.102"],
    "john.smith": ["192.168.1.201"],
    "sara.jones": ["192.168.1.301"],
}


def random_time_in_range(date, start_hour, end_hour):
    hour = random.randint(start_hour, end_hour - 1)
    minute = random.randint(0, 59)
    return date.replace(hour=hour, minute=minute, second=0, tzinfo=timezone.utc)


def generate_normal_events(days=30):
    events = []
    base_date = datetime.now(timezone.utc) - timedelta(days=days)

    for day_offset in range(days):
        current_date = base_date + timedelta(days=day_offset)

        # Skip weekends
        if current_date.weekday() >= 5:
            continue

        for user in USERS:
            username = user["username"]
            start_h, end_h = user["normal_hours"]

            # Morning login
            login_time = random_time_in_range(current_date, start_h, start_h + 2)
            events.append({
                "source_type": "auth",
                "source_id": "active-directory-01",
                "payload": {
                    "username": username,
                    "action": "login_success",
                    "ip_address": random.choice(IPS[username]),
                    "timestamp": login_time.isoformat(),
                    "device_id": random.choice(DEVICES[username])
                }
            })

            # Some file activity
            for _ in range(random.randint(2, 8)):
                activity_time = random_time_in_range(
                    current_date, start_h + 1, end_h - 1
                )
                events.append({
                    "source_type": "file_access",
                    "source_id": "file-server-01",
                    "payload": {
                        "user": username,
                        "operation": random.choice(["view", "download", "upload"]),
                        "file_path": f"/shared/{user['department'].lower()}/doc_{random.randint(1,100)}.xlsx",
                        "bytes": random.randint(10000, 500000),
                        "time": activity_time.isoformat(),
                        "workstation": random.choice(DEVICES[username])
                    }
                })

            # Evening logout
            logout_time = random_time_in_range(current_date, end_h - 1, end_h + 1)
            events.append({
                "source_type": "auth",
                "source_id": "active-directory-01",
                "payload": {
                    "username": username,
                    "action": "logout",
                    "ip_address": random.choice(IPS[username]),
                    "timestamp": logout_time.isoformat(),
                    "device_id": random.choice(DEVICES[username])
                }
            })

    return events


def generate_anomalous_events():
    """The story scenario for the demo"""
    now = datetime.now(timezone.utc)
    events = []

    # john.smith logs in at 2am from unknown device and unknown IP
    events.append({
        "source_type": "auth",
        "source_id": "active-directory-01",
        "payload": {
            "username": "john.smith",
            "action": "login_success",
            "ip_address": "203.0.113.99",       # never seen before
            "timestamp": now.replace(hour=2, minute=13).isoformat(),
            "device_id": "UNKNOWN-DEVICE-888"   # never seen before
        }
    })

    # Followed by massive data download
    events.append({
        "source_type": "file_access",
        "source_id": "file-server-01",
        "payload": {
            "user": "john.smith",
            "operation": "download",
            "file_path": "/finance/payroll/ALL_EMPLOYEES_2025.xlsx",
            "bytes": 52428800,                  # 50MB, way above normal
            "time": now.replace(hour=2, minute=17).isoformat(),
            "workstation": "UNKNOWN-DEVICE-888"
        }
    })

    return events


def write_events(filename: str, events: list[dict]) -> None:
    output_path = OUTPUT_DIR / filename
    output_path.write_text(
        json.dumps(events, indent=2),
        encoding="utf-8"
    )


if __name__ == "__main__":
    normal = generate_normal_events(30)
    anomalous = generate_anomalous_events()
    write_events("normal_events.json", normal)
    write_events("anomalous_events.json", anomalous)
    write_events("events.json", normal + anomalous)

    print(f"Generated {len(normal)} normal events")
    print(f"Generated {len(anomalous)} anomalous events")
    print(f"Saved sample files to {OUTPUT_DIR}")
