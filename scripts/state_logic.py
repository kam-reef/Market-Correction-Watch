from datetime import date
import json
import random
from pathlib import Path

OUTPUT = Path("data/output")
OUTPUT.mkdir(parents=True, exist_ok=True)

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
    "QQQ below 100MA",  # used directionally
    "ARKK +20% from low",
    "HYG +7%",
    "IEF -3%",
]

BANNER_TEXT = {
    "NOMINAL": [
        "Market conditions remain broadly stable.",
        "No sustained risk signals are currently active.",
    ],
    "DOWNTURN": [
        "Downturn indicators have been active for {weeks} consecutive weeks.",
        "Market stress signals remain elevated for {weeks} weeks.",
    ],
    "RECOVERY": [
        "Recovery signals have persisted for {weeks} weeks, supported by trend improvement.",
        "Market conditions continue to normalize over the past {weeks} weeks.",
    ],
}

def load_alerts():
    import pandas as pd
    df = pd.read_csv("data/output/alerts_snapshot.csv")
    return {row["alert"]: row["triggered"] for _, row in df.iterrows()}

def main():
    alerts = load_alerts()

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

    snapshot = {
        "date": str(date.today()),
        "state": state,
        "severity": severity,
        "downturn_alerts": downturn_count,
        "recovery_alerts": recovery_count,
        "summary": random.choice(BANNER_TEXT[state]).format(weeks=1),
    }

    with open(OUTPUT / "state_snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    print("✅ State snapshot written")

if __name__ == "__main__":
    main()