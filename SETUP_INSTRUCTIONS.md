# Setup Instructions for Statistical Arbitrage Bot

## Quick Fix for Your Current Issues

### Issue 1: Missing `cryptography` Module

**Error**: `ModuleNotFoundError: No module named 'cryptography'`

**Solution**: Install the missing dependency:

```bash
pip install cryptography
```

Or install all dependencies at once:

```bash
pip install -r requirements.txt
```

### Issue 2: API 400 Error (JSON Not Generating)

**Error**: `HTTPError: 400 Client Error: Bad Request` when downloading historical data

**Solution**: The notebook has been updated with:
1. **Fallback logic** - Tries 1-minute, then hourly, then daily candles if one fails
2. **Shorter time window** - Changed from 60 days to 30 days (1-minute candles may not be available for long periods)
3. **Better error handling** - Shows what went wrong and tries alternatives

---

## Complete Setup Guide

### Step 1: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests pandas scipy matplotlib python-dateutil pytz kalshi-python cryptography
```

### Step 2: Run the Research Notebook

1. Open `find_our_model.ipynb` in Jupyter
2. Run all cells from top to bottom
3. The notebook will:
   - Download historical data (with automatic fallback if 1-minute fails)
   - Calculate the statistical model
   - Save `model.json` to the current directory

**If you get API errors:**
- The notebook will automatically try hourly (60min) or daily (1440min) candles
- You can manually change `START = "-30d"` to a shorter period like `"-7d"` if needed
- Make sure the markets are still open/active

### Step 3: Configure the Live Bot

1. Open `live_stat_arb_bot.py`
2. Set your credentials:
   ```python
   YOUR_EMAIL = 'your-email@example.com'
   YOUR_PASSWORD = 'your-password'
   ```

### Step 4: Run the Live Bot

```bash
python live_stat_arb_bot.py
```

---

## Troubleshooting

### Problem: "model.json not found"

**Solution**: Run the notebook first! The notebook generates `model.json`.

### Problem: API returns 400 error

**Possible causes:**
1. **Time window too long** - Try shorter periods (7-14 days instead of 30)
2. **Market doesn't have enough history** - Try different tickers
3. **1-minute candles not available** - The notebook will auto-fallback to hourly/daily

**Fix**: The notebook now has automatic fallback. If it still fails:
- Change `START = "-30d"` to `START = "-7d"` (shorter period)
- Or manually set `period_minutes=60` (hourly) or `period_minutes=1440` (daily)

### Problem: "No module named 'kalshi_python'"

**Solution**: 
```bash
pip install kalshi-python
```

### Problem: "No module named 'cryptography'"

**Solution**: 
```bash
pip install cryptography
```

### Problem: Bot crashes immediately

**Check:**
1. Is `model.json` in the same directory as the bot?
2. Are your credentials set correctly?
3. Check the log file for detailed error messages

---

## Expected Output

### Notebook Output:
```
Series for X: KXHURCTOTMAJ
Series for Y: KXHURCTOTMAJ
Window UTC: 2025-10-14 ... -> 2025-11-13 ...

Trying 1-minute candles for KXHURCTOTMAJ-25DEC01-T4...
✅ Success! Got 1234 rows using 1-minute candles

R-Squared (R^2): 0.9234
✅ R² is high enough (0.9234) - markets are well correlated!

✅ Saved model to model.json!
```

### Bot Output:
```
--- Starting Live Statistical Bot ---
Logging to bot_20251113_123456.log
Loaded model! Trading KXHURCTOTMAJ-25DEC01-T5 vs KXHURCTOTMAJ-25DEC01-T4.
Kalshi API login successful.
--- Starting main scan loop ---
Live Prices: X=20.50, Y=6.25 | Live Error: 0.1234
```

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Run notebook to generate `model.json`
3. ✅ Set credentials in `live_stat_arb_bot.py`
4. ✅ Test bot with demo account first
5. ✅ Monitor logs for 24 hours before going live

Good luck! 🚀

