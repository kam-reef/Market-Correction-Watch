import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("data/history/state_history.csv")
OUTPUT_DIR = Path("data/output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

def quarter_key(dt):
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{q}"

def count_transitions(states):
    transitions = 0
    for prev, curr in zip(states, states[1:]):
        if prev != curr:
            transitions += 1
    return transitions

def longest_streak(states):
    longest_state = None
    longest_len = 0

    current_state = None
    current_len = 0

    for s in states:
        if s == current_state:
            current_len += 1
        else:
            if current_len > longest_len:
                longest_state = current_state
                longest_len = current_len
            current_state = s
            current_len = 1

    if current_len > longest_len:
        longest_state = current_state
        longest_len = current_len

    return {
        "state": longest_state,
        "weeks": longest_len
    }

def load_history():
    if not HISTORY_FILE.exists():
        print("⚠️  No history file found; skipping summaries")
        return []

    with open(HISTORY_FILE, newline="") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        r["date"] = parse_date(r["date"])
        r["severity"] = int(r["severity"])

    return rows

def summarize_monthly(history):
    by_month = defaultdict(list)

    for r in history:
        key = r["date"].strftime("%Y-%m")
        by_month[key].append(r)

    summary = {}

    for month, rows in by_month.items():
        states = [r["state"] for r in rows]
        severities = [r["severity"] for r in rows]

        state_counts = Counter(states)

        summary[month] = {
            "weeks": len(rows),
            "dominant_state": state_counts.most_common(1)[0][0],
            "weeks_by_state": dict(state_counts),
            "transitions": count_transitions(states),
            "max_severity": max(severities),
        }

    return summary

def summarize_quarterly(history):
    by_quarter = defaultdict(list)

    for r in history:
        key = quarter_key(r["date"])
        by_quarter[key].append(r)

    summary = {}

    for quarter, rows in by_quarter.items():
        states = [r["state"] for r in rows]
        severities = [r["severity"] for r in rows]

        state_counts = Counter(states)
        total = len(states)

        summary[quarter] = {
            "weeks": total,
            "dominant_state": state_counts.most_common(1)[0][0],
            "percent_by_state": {
                k: round((v / total) * 100, 1)
                for k, v in state_counts.items()
            },
            "transitions": count_transitions(states),
            "longest_streak": longest_streak(states),
            "max_severity": max(severities),
        }

    return summary

def main():
    history = load_history()
    if not history:
        return

    monthly = summarize_monthly(history)
    quarterly = summarize_quarterly(history)

    with open(OUTPUT_DIR / "monthly_summary.json", "w") as f:
        json.dump(monthly, f, indent=2)

    with open(OUTPUT_DIR / "quarterly_summary.json", "w") as f:
        json.dump(quarterly, f, indent=2)

    print("✅ Monthly and quarterly summaries written")

if __name__ == "__main__":
    main()