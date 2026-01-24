import pandas as pd
from pathlib import Path

BASE_URL = "https://stooq.com/q/d/l/"
SYMBOLS = {
    "SPY": "spy.us",
    "QQQ": "qqq.us",
    "ARKK": "arkk.us",
    "HYG": "hyg.us",
    "IEF": "ief.us",
    "VIX": "^vix"
}

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch(symbol, stooq_code):
    url = f"{BASE_URL}?s={stooq_code}&i=d"
    df = pd.read_csv(url)
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)
    df.to_csv(RAW_DIR / f"{symbol}.csv", index=False)

def main():
    for symbol, code in SYMBOLS.items():
        fetch(symbol, code)

if __name__ == "__main__":
    main()