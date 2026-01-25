from datetime import date, timedelta
import pandas as pd
from pathlib import Path
import csv

# ---- CONFIG ----
WEEKS_BACK = 52
ANCHOR_WEEKDAY = 4  # Friday
RAW_DIR = Path("data/raw")
HISTORY_DIR = Path("data/history")
HISTORY_FILE = HISTORY_DIR / "state_history.csv"

HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# ---- ALERT GROUPS (same as state_logic.py) ----
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

def friday_before(d):
    while d.weekday() != ANCHOR_WEEKDAY:
        d -= timedelta(days=1)
    return d

def load(symbol, cutoff):
    path = RAW_DIR / f"{symbol}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, parse_dates=["Date"])
    return df[df["Date"] <= cutoff]

def pct_from_high(df, window):
    return (df["Close"] / df["Close"].rolling(window).max() - 1) * 100

def pct_from_low(df, window):
    return (df["Close"] / df["Close"].rolling(window).min() - 1) * 100

def evaluate_week(cutoff):
    alerts = {}

    # --- SPY ---
    spy = load("SPY", cutoff)
    if spy is not None and len(spy) >= 200:
        spy["MA200"] = spy["Close"].rolling(200).mean()
        last = spy.iloc[-1]
        alerts["SPY below 200MA"] = last["Close"] < last["MA200"]
        alerts["SPY above 200MA"] = last["Close"] > last["MA200"]

    # --- QQQ ---
    qqq = load("QQQ", cutoff)
    if qqq is not None and len(qqq) >= 100:
        qqq["MA100"] = qqq["Close"].rolling(100).mean()
        qqq["pct_high"] = pct_from_high(qqq, 63)
        qqq["pct_low"] = pct_from_low(qqq, 63)
        last = qqq.iloc[-1]
        alerts["QQQ below 100MA"] = last["Close"] < last["MA100"]
        alerts["QQQ -12% from high"] = last["pct_high"] <= -12
        alerts["QQQ +15% from low"] = last["pct_low"] >= 15

    # --- ARKK ---
    arkk = load("ARKK", cutoff)
    if arkk is not None:
        arkk["pct_high"] = pct_from_high(arkk, 63)
        arkk["pct_low"] = pct_from_low(arkk, 63)
        last = arkk.iloc[-1]
        alerts["ARKK -15% from high"] = last["pct_high"] <= -15
        alerts["ARKK +20% from low"] = last["pct_low"] >= 20

    # --- CREDIT ---
    hyg = load("HYG", cutoff)
    if hyg is not None:
        hyg["pct_high"] = pct_from_high(hyg, 63)
        alerts["HYG -7%"] = hyg.iloc[-1]["pct_high"] <= -7
        alerts["HYG +7%"] = pct_from_low(hyg, 63).iloc[-1] >= 7

    ief = load("IEF", cutoff)
    if ief is not None:
        ief["pct_low"] = pct_from_low(ief, 63)
        alerts["IEF +5%"] = ief.iloc[-1]["pct_low"] >= 5
        alerts["IEF -3%"] = ief.iloc[-1]["pct_low"] <= -3

    downturn_count = sum(alerts.get(a, False) for a in DOWNTURN_ALERTS)
    recovery_count = sum(alerts.get(a, False) for a in RECOVERY_ALERTS)

    if alerts.get("SPY below 200MA"):
        state = "DOWNTURN"
        severity = min(3, max(0, downturn_count - 2))
    elif alerts.get("SPY above 200MA") and recovery_count >= 3:
        state = "RECOVERY"
        severity = min(3, max(0, recovery_count - 2))
    else:
        state = "NOMINAL"
        severity = 0

    return state, severity

def main():
    start = friday_before(date.today()) - timedelta(weeks=WEEKS_BACK)
    weeks = [start + timedelta(weeks=i) for i in range(WEEKS_BACK)]

    with open(HISTORY_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "state", "severity"])
        writer.writeheader()

        for w in weeks:
            state, severity = evaluate_week(pd.Timestamp(w))
            writer.writerow({
                "date": w.isoformat(),
                "state": state,
                "severity": severity,
            })
            print(f"{w}: {state} (sev {severity})")

    print("✅ 1-year backfill complete")

if __name__ == "__main__":
    main()