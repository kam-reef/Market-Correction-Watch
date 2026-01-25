import json
from pathlib import Path

OUTPUT_DIR = Path("data/output")

MONTHLY_IN = OUTPUT_DIR / "monthly_summary.json"
QUARTERLY_IN = OUTPUT_DIR / "quarterly_summary.json"

MONTHLY_OUT = OUTPUT_DIR / "monthly_narrative.json"
QUARTERLY_OUT = OUTPUT_DIR / "quarterly_narrative.json"

def load_json(path):
    if not path.exists():
        print(f"⚠️  Missing {path.name}; skipping")
        return {}
    with open(path) as f:
        return json.load(f)

def month_text(period, d):
    state = d["dominant_state"]
    weeks = d["weeks"]
    transitions = d["transitions"]
    max_sev = d["max_severity"]

    stability = (
        "no regime transitions"
        if transitions == 0
        else f"{transitions} regime transition{'s' if transitions != 1 else ''}"
    )

    sev_text = (
        "No elevated severity was observed."
        if max_sev == 0
        else f"Maximum severity reached level {max_sev}."
    )

    return (
        f"{period}: Market conditions were predominantly {state} over {weeks} weeks, "
        f"with {stability}. {sev_text}"
    )

def quarter_text(period, d):
    state = d["dominant_state"]
    weeks = d["weeks"]
    transitions = d["transitions"]
    max_sev = d["max_severity"]
    streak = d["longest_streak"]

    stability = (
        "no regime transitions"
        if transitions == 0
        else f"{transitions} regime transition{'s' if transitions != 1 else ''}"
    )

    streak_text = (
        f"The longest uninterrupted streak was {streak['weeks']} weeks in {streak['state']}."
        if streak and streak.get("state")
        else ""
    )

    sev_text = (
        "No elevated severity was observed."
        if max_sev == 0
        else f"Maximum severity reached level {max_sev}."
    )

    return (
        f"{period}: Market conditions were predominantly {state} across {weeks} weeks, "
        f"with {stability}. {streak_text} {sev_text}"
    )

def main():
    monthly = load_json(MONTHLY_IN)
    quarterly = load_json(QUARTERLY_IN)

    monthly_out = {
        period: {"text": month_text(period, d)}
        for period, d in monthly.items()
    }

    quarterly_out = {
        period: {"text": quarter_text(period, d)}
        for period, d in quarterly.items()
    }

    with open(MONTHLY_OUT, "w") as f:
        json.dump(monthly_out, f, indent=2)

    with open(QUARTERLY_OUT, "w") as f:
        json.dump(quarterly_out, f, indent=2)

    print("✅ Deterministic monthly and quarterly narratives written")

if __name__ == "__main__":
    main()