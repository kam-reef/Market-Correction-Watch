import pandas as pd
from pathlib import Path

BASE_URL = "https://stooq.com/q/d/l/"
SYMBOLS = {
    "SPY": "spy.us",
    "QQQ": "qqq.us",
    "ARKK": "arkk.us",
    "HYG": "hyg.us",
    "IEF": "ief.us",
    "VIX": ".vix"
}

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch(symbol, stooq_code):
    url = f"{BASE_URL}?s={stooq_code}&i=d"
    try:
        df = pd.read_csv(url)

        # Normalize column names
        df.columns = [c.strip().capitalize() for c in df.columns]

        if "Date" not in df.columns:
            print(f"⚠️  Skipping {symbol}: no Date column returned")
            return

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df.sort_values("Date", inplace=True)

        if df.empty:
            print(f"⚠️  Skipping {symbol}: no valid rows")
            return

        df.to_csv(RAW_DIR / f"{symbol}.csv", index=False)
        print(f"✅ Fetched {symbol}")

    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")

def main():
    for symbol, code in SYMBOLS.items():
        fetch(symbol, code)

if __name__ == "__main__":
    main()
