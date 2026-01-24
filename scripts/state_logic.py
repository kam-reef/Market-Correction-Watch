from datetime import date
import json
import random
import csv
from pathlib import Path
import pandas as pd

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

BANNER_TEXT = {
    "NOMINAL": [
        "Market conditions have remained broadly stable for the past {weeks} weeks.",
        "No sustained risk signals have been active over the last {weeks} weeks.",
    ],
    "DOWNTURN": [
        "Downturn indicators have persisted for {weeks} consecutive weeks.",
        "Market stress signals have remained elevated for {weeks} weeks.",
    ],
    "RECOVERY": [
        "Recovery signals have been active for {weeks} weeks, supported by trend improvement.",
        "Market conditions have shown sustained normalization over the past {weeks} weeks.",
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

    snapshot = {
        "date": str(date.today()),
        "state": state,
        "severity": severity,
        "weeks_in_state": weeks,
        "downturn_alerts": downturn_count,
        "recovery_alerts": recovery_count,
        week_label = "week" if weeks == 1 else "weeks"
        summary = random.choice(BANNER_TEXT[state]).format(weeks=f"{weeks} {week_label}"),
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

    print(f"✅ State snapshot written — {state}, week {weeks}")

if __name__ == "__main__":
    main()