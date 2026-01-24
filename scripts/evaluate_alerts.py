import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/output")
OUT.mkdir(parents=True, exist_ok=True)

def load(symbol):
    df = pd.read_csv(RAW / f"{symbol}.csv", parse_dates=["Date"])
    return df

def pct_from_high(df, window):
    return (df["Close"] / df["Close"].rolling(window).max() - 1) * 100

def pct_from_low(df, window):
    return (df["Close"] / df["Close"].rolling(window).min() - 1) * 100

def main():
    alerts = []

    # --- SPY ---
    spy = load("SPY")
    spy["MA200"] = spy["Close"].rolling(200).mean()
    spy_last = spy.iloc[-1]

    alerts.append({
        "alert": "SPY below 200MA",
        "triggered": spy_last["Close"] < spy_last["MA200"]
    })

    alerts.append({
        "alert": "SPY above 200MA",
        "triggered": spy_last["Close"] > spy_last["MA200"]
    })

    # --- QQQ ---
    qqq = load("QQQ")
    qqq["MA100"] = qqq["Close"].rolling(100).mean()
    qqq["pct_high"] = pct_from_high(qqq, 63)
    qqq["pct_low"] = pct_from_low(qqq, 63)
    qqq_last = qqq.iloc[-1]

    alerts += [
        {"alert": "QQQ below 100MA", "triggered": qqq_last["Close"] < qqq_last["MA100"]},
        {"alert": "QQQ -12% from high", "triggered": qqq_last["pct_high"] <= -12},
        {"alert": "QQQ +15% from low", "triggered": qqq_last["pct_low"] >= 15},
    ]

    # --- ARKK ---
    arkk = load("ARKK")
    arkk["pct_high"] = pct_from_high(arkk, 63)
    arkk["pct_low"] = pct_from_low(arkk, 63)
    arkk_last = arkk.iloc[-1]

    alerts += [
        {"alert": "ARKK -15% from high", "triggered": arkk_last["pct_high"] <= -15},
        {"alert": "ARKK +20% from low", "triggered": arkk_last["pct_low"] >= 20},
    ]

    # --- VIX ---
    vix = load("VIX")
    vix_last = vix.iloc[-1]["Close"]

    alerts += [
        {"alert": "VIX > 25", "triggered": vix_last > 25},
        {"alert": "VIX > 30", "triggered": vix_last > 30},
        {"alert": "VIX < 20", "triggered": vix_last < 20},
        {"alert": "VIX < 18", "triggered": vix_last < 18},
    ]

    # --- Credit ---
    hyg = load("HYG")
    hyg["pct_high"] = pct_from_high(hyg, 63)
    hyg_last = hyg.iloc[-1]

    ief = load("IEF")
    ief["pct_low"] = pct_from_low(ief, 63)
    ief_last = ief.iloc[-1]

    alerts += [
        {"alert": "HYG -7%", "triggered": hyg_last["pct_high"] <= -7},
        {"alert": "HYG +7%", "triggered": hyg_last["pct_low"] >= 7},
        {"alert": "IEF +5%", "triggered": ief_last["pct_low"] >= 5},
        {"alert": "IEF -3%", "triggered": ief_last["pct_low"] <= -3},
    ]

    pd.DataFrame(alerts).to_csv(OUT / "alerts_snapshot.csv", index=False)

if __name__ == "__main__":
    main()