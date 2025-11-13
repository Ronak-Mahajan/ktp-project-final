# Quick Fix Guide

## Problem 1: Missing `cryptography` Module

**Error**: `ModuleNotFoundError: No module named 'cryptography'`

**Solution**: Run this command:

```bash
pip install cryptography kalshi-python
```

Or install everything:
```bash
pip install -r requirements.txt
```

---

## Problem 2: API 400 Error - JSON Not Generating

The API is rejecting your request for 1-minute candles over 60 days. Here's the fix:

### Option A: Quick Fix (Change Time Window)

In `find_our_model.ipynb`, **Cell 3**, change this line:

```python
START = "-60d"  # last 60 days
```

To:

```python
START = "-7d"  # last 7 days (1-minute candles work better for shorter periods)
```

Or use hourly candles instead:

```python
# Change this line:
payload_x = get_market_candles(series_ticker_x, TICKER_X, start_ts, end_ts, period_minutes=1)

# To this:
payload_x = get_market_candles(series_ticker_x, TICKER_X, start_ts, end_ts, period_minutes=60)  # Hourly
```

### Option B: Use the Improved Code (Recommended)

Replace **Cell 3** in your notebook with this improved version that has automatic fallback:

```python
# Set time window
START = "-30d"  # Reduced to 30 days
END = "now"

# Define the two market tickers (our "pair")
TICKER_X = "KXHURCTOTMAJ-25DEC01-T4"
TICKER_Y = "KXHURCTOTMAJ-25DEC01-T5"

# Get series ticker for both markets
try:
    mk_x = get_market(TICKER_X)
    evt_x = get_event(mk_x["event_ticker"])
    series_ticker_x = evt_x["series_ticker"]

    mk_y = get_market(TICKER_Y)
    evt_y = get_event(mk_y["event_ticker"])
    series_ticker_y = evt_y["series_ticker"]

    print(f"Series for X: {series_ticker_x}")
    print(f"Series for Y: {series_ticker_y}")
except Exception as e:
    print(f"Error fetching market info: {e}")
    raise

# Convert time window to timestamps
start_ts = to_unix_ts(START)
end_ts = to_unix_ts(END)
print(f"Window UTC: {datetime.fromtimestamp(start_ts, timezone.utc)} -> {datetime.fromtimestamp(end_ts, timezone.utc)}")

# Download candle data with fallback logic
def download_with_fallback(series_ticker, market_ticker, start_ts, end_ts, ticker_name):
    """Try different candle periods if one fails."""
    periods = [
        (1, "1-minute"),
        (60, "hourly"),
        (1440, "daily")
    ]
    
    for period_minutes, period_name in periods:
        try:
            print(f"\nTrying {period_name} candles for {ticker_name}...")
            payload = get_market_candles(series_ticker, market_ticker, start_ts, end_ts, period_minutes=period_minutes)
            df = candles_to_df(payload)
            if len(df) > 0:
                print(f"✅ Success! Got {len(df)} rows using {period_name} candles")
                return df, period_minutes
            else:
                print(f"⚠️  Got empty data for {period_name} candles, trying next...")
        except Exception as e:
            print(f"⚠️  Error with {period_name} candles: {e}")
            if period_minutes == 1440:  # Last option failed
                raise
            continue
    
    raise ValueError(f"Could not download data for {ticker_name} with any candle period")

# Download data for both tickers
print(f"\n{'='*60}")
print(f"Downloading data for {TICKER_X}...")
df_x, period_x = download_with_fallback(series_ticker_x, TICKER_X, start_ts, end_ts, TICKER_X)

print(f"\n{'='*60}")
print(f"Downloading data for {TICKER_Y}...")
df_y, period_y = download_with_fallback(series_ticker_y, TICKER_Y, start_ts, end_ts, TICKER_Y)

# Warn if different periods were used
if period_x != period_y:
    print(f"\n⚠️  WARNING: Using different candle periods (X: {period_x}min, Y: {period_y}min)")
```

---

## Step-by-Step Fix

1. **Install cryptography**:
   ```bash
   pip install cryptography
   ```

2. **Open `find_our_model.ipynb`**

3. **Go to Cell 3** (the one that downloads data)

4. **Replace the entire cell content** with the improved code above (Option B)

5. **Run all cells** from the beginning

6. **Check for `model.json`** - it should be created in the same folder

---

## Why This Happens

- **1-minute candles** are only available for recent/short time periods
- **60 days of 1-minute data** = 86,400 data points, which the API may reject
- **Solution**: Use shorter periods (7-30 days) or fall back to hourly/daily candles

---

## Test It Works

After running the notebook, you should see:
```
✅ Success! Got 1234 rows using hourly candles
✅ Saved model to model.json!
```

And a file named `model.json` should appear in your folder.

---

## Still Having Issues?

1. Try even shorter period: `START = "-7d"`
2. Use daily candles: `period_minutes=1440`
3. Check if markets are still active/open
4. Try different tickers if these markets don't have enough history

Good luck! 🚀

