import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/output")
OUT.mkdir(parents=True, exist_ok=True)

def load(symbol):
    path = RAW / f"{symbol}.csv"
    if not path.exists():
        print(f"⚠️  Missing data for {symbol}")
        return None
    return pd.read_csv(path, parse_dates=["Date"])

def pct_from_high(df, window):
    return (df["Close"] / df["Close"].rolling(window).max() - 1) * 100

def pct_from_low(df, window):
    return (df["Close"] / df["Close"].rolling(window).min() - 1) * 100

def main():
    alerts = []

    # --- SPY ---
    spy = load("SPY")
    if spy is not None and len(spy) >= 200:
        spy["MA200"] = spy["Close"].rolling(200).mean()
        last = spy.iloc[-1]
        alerts += [
            {"alert": "SPY below 200MA", "triggered": last["Close"] < last["MA200"]},
            {"alert": "SPY above 200MA", "triggered": last["Close"] > last["MA200"]},
        ]

    # --- QQQ ---
    qqq = load("QQQ")
    if qqq is not None and len(qqq) >= 100:
        qqq["MA100"] = qqq["Close"].rolling(100).mean()
        qqq["pct_high"] = pct_from_high(qqq, 63)
        qqq["pct_low"] = pct_from_low(qqq, 63)
        last = qqq.iloc[-1]

        alerts += [
            {"alert": "QQQ below 100MA", "triggered": last["Close"] < last["MA100"]},
            {"alert": "QQQ -12% from high", "triggered": last["pct_high"] <= -12},
            {"alert": "QQQ +15% from low", "triggered": last["pct_low"] >= 15},
        ]

    # --- ARKK ---
    arkk = load("ARKK")
    if arkk is not None:
        arkk["pct_high"] = pct_from_high(arkk, 63)
        arkk["pct_low"] = pct_from_low(arkk, 63)
        last = arkk.iloc[-1]

        alerts += [
            {"alert": "ARKK -15% from high", "triggered": last["pct_high"] <= -15},
            {"alert": "ARKK +20% from low", "triggered": last["pct_low"] >= 20},
        ]

    # --- VIX ---
    vix = load("VIX")
    if vix is not None:
        vix_last = vix.iloc[-1]["Close"]
        alerts += [
            {"alert": "VIX > 25", "triggered": vix_last > 25},
            {"alert": "VIX > 30", "triggered": vix_last > 30},
            {"alert": "VIX < 20", "triggered": vix_last < 20},
            {"alert": "VIX < 18", "triggered": vix_last < 18},
        ]
    else:
        print("ℹ️  VIX alerts skipped this run")

    # --- Credit ---
    hyg = load("HYG")
    ief = load("IEF")

    if hyg is not None:
        hyg["pct_high"] = pct_from_high(hyg, 63)
        last = hyg.iloc[-1]
        alerts += [
            {"alert": "HYG -7%", "triggered": last["pct_high"] <= -7},
            {"alert": "HYG +7%", "triggered": pct_from_low(hyg, 63).iloc[-1] >= 7},
        ]

    if ief is not None:
        ief["pct_low"] = pct_from_low(ief, 63)
        last = ief.iloc[-1]
        alerts += [
            {"alert": "IEF +5%", "triggered": last["pct_low"] >= 5},
            {"alert": "IEF -3%", "triggered": last["pct_low"] <= -3},
        ]

    pd.DataFrame(alerts).to_csv(OUT / "alerts_snapshot.csv", index=False)
    print("✅ Alert snapshot written")

if __name__ == "__main__":
    main()