from datetime import date
import json
import random
import csv
from pathlib import Path
import pandas as pd
import os
import requests

# Paths
OUTPUT = Path("data/output")
HISTORY_DIR = Path("data/history")

OUTPUT.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = HISTORY_DIR / "state_history.csv"

# Alert priority groups (ordered)
DOWNTURN_ALERTS = [
    "SPY below 200MA",
    "VIX > 25",
    "ARKK -15% from high",
    "QQQ below 100MA",
    "HYG -7%",
    "IEF +5%",
]

RECOVERY_ALERTS = [
    "SPY above 200MA",
    "VIX < 20",
    "QQQ +15% from low",
    "ARKK +20% from low",
    "HYG +7%",
    "IEF -3%",
]

# Banner language (editable)
BANNER_TEXT = {
    "NOMINAL": [
        "Market conditions have remained broadly stable for the past {weeks}.",
        "No sustained risk signals have been active over the last {weeks}.",
    ],
    "DOWNTURN": [
        "Downturn indicators have persisted for {weeks}.",
        "Market stress signals have remained elevated for {weeks}.",
    ],
    "RECOVERY": [
        "Recovery signals have been active for {weeks}, supported by trend improvement.",
        "Market conditions have shown sustained normalization over the past {weeks}.",
    ],
}

def load_alerts():
    df = pd.read_csv("data/output/alerts_snapshot.csv")
    return {row["alert"]: bool(row["triggered"]) for _, row in df.iterrows()}

def load_history():
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, newline="") as f:
        return list(csv.DictReader(f))

def weeks_in_state(history, state):
    count = 0
    for row in reversed(history):
        if row["state"] == state:
            count += 1
        else:
            break
    return count

def should_create_issue(history, current_state, current_severity):
    if not history:
        return False, None

    last = history[-1]
    prev_state = last["state"]
    prev_severity = int(last["severity"])

    if current_state != prev_state:
        return True, f"State change: {prev_state} → {current_state}"

    if current_severity > prev_severity:
        return True, f"Severity increase within {current_state}"

    return False, None

def create_github_issue(title, body):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo:
        print("ℹ️  GitHub token or repository not available; skipping issue creation")
        return

    url = f"https://api.github.com/repos/{repo}/issues"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    payload = {
        "title": title,
        "body": body,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("✅ GitHub issue created")
    else:
        print(f"⚠️  Failed to create issue: {response.status_code}")
        print(response.text)

def main():
    alerts = load_alerts()
    history = load_history()

    downturn_count = sum(alerts.get(a, False) for a in DOWNTURN_ALERTS)
    recovery_count = sum(alerts.get(a, False) for a in RECOVERY_ALERTS)

    # Anchor logic
    if alerts.get("SPY below 200MA"):
        state = "DOWNTURN"
        severity = min(3, max(0, downturn_count - 2))
    elif alerts.get("SPY above 200MA") and recovery_count >= 3:
        state = "RECOVERY"
        severity = min(3, max(0, recovery_count - 2))
    else:
        state = "NOMINAL"
        severity = 0

    previous_weeks = weeks_in_state(history, state)
    weeks = previous_weeks + 1

    week_label = "week" if weeks == 1 else "weeks"

    summary = random.choice(BANNER_TEXT[state]).format(
        weeks=f"{weeks} {week_label}"
    )

    snapshot = {
        "date": str(date.today()),
        "state": state,
        "severity": severity,
        "weeks_in_state": weeks,
        "downturn_alerts": downturn_count,
        "recovery_alerts": recovery_count,
        "summary": summary,
    }

    # Write snapshot JSON
    with open(OUTPUT / "state_snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    # Append to history
    write_header = not HISTORY_FILE.exists()
    with open(HISTORY_FILE, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "state", "severity"]
        )
        if write_header:
            writer.writeheader()
        writer.writerow({
            "date": snapshot["date"],
            "state": state,
            "severity": severity,
        })

        # ---- GitHub Issue Logic ----
    create_issue, reason = should_create_issue(history, state, severity)

    if create_issue:
        title = f"Market Risk State Update: {state} ({snapshot['date']})"

        body = f"""## Market Risk State Update

**State:** {state}  
**Severity:** {severity}  
**Weeks in State:** {weeks}

**Reason:** {reason}

**Summary:**  
{summary}

---

This issue was generated automatically by the Market Risk Monitor.
It is informational only and does not constitute investment advice.
"""

        create_github_issue(title, body)

    print(f"✅ State snapshot written — {state}, week {weeks}")

if __name__ == "__main__":
    main()