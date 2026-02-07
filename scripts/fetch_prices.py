# src/fetch_market_data.py

import pandas as pd
from pathlib import Path

# Stooq base URL for most symbols; VIX will be fetched via yfinance instead.
BASE_URL = "https://stooq.com/q/d/l/"
SYMBOLS = {
    "SPY": "spy.us",
    "QQQ": "qqq.us",
    "ARKK": "arkk.us",
    "HYG": "hyg.us",
    "IEF": "ief.us",
}

# VIX ticker for yfinance
VIX_SYMBOL = "^VIX"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch(symbol: str, stooq_code: str) -> None:
    """
    Fetch a single equity/CETF from Stooq and write it to CSV.
    """
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


def main() -> None:
    # First, fetch all symbols supported on Stooq
    for symbol, code in SYMBOLS.items():
        fetch(symbol, code)

    # Next, fetch VIX via yfinance
    try:
        import yfinance as yf

        print(f"🔍 Downloading VIX data from yfinance ({VIX_SYMBOL})")
        vix = yf.Ticker(VIX_SYMBOL)
        df_vix = vix.history(period="max").reset_index()

        if "Date" not in df_vix.columns:
            print("⚠️  Skipping VIX: no Date column returned from yfinance")
        else:
            df_vix = df_vix.dropna(subset=["Date"])
            df_vix.sort_values("Date", inplace=True)
            df_vix.to_csv(RAW_DIR / "VIX.csv", index=False)
            print("✅ Fetched VIX")

    except Exception as e:
        print(f"❌ Error fetching VIX from yfinance: {e}")


if __name__ == "__main__":
    main()