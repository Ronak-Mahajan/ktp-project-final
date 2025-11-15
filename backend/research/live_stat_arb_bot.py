# live_stat_arb_bot.py
# This bot loads our model and finds live signals!

import kalshi_python
import time
import logging
import json
import math
import signal
from datetime import datetime

# --- Student TODO: Put your real email/password in here ---
# (but for the project, we'll just leave it as-is)
YOUR_EMAIL = 'YOUR_EMAIL'
YOUR_PASSWORD = 'YOUR_PASSWORD'

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_requested
    logging.info("Shutdown signal received. Stopping gracefully...")
    shutdown_requested = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# This helper gets the mid price from an order book
# We use mid price (average of best bid and ask) to match historical data
def get_mid_price(orderbook_yes):
    """Get mid price from orderbook. Returns None if unavailable."""
    if not orderbook_yes:
        return None
    
    asks = orderbook_yes.get('asks', [])
    bids = orderbook_yes.get('bids', [])
    
    if not asks or not bids:
        return None
    
    best_ask = asks[0][0] / 100.0  # Prices are in cents
    best_bid = bids[0][0] / 100.0
    
    return (best_ask + best_bid) / 2.0  # Mid price

def run_bot():
    print("--- Starting Live Statistical Bot ---")

    # 1. Set up logging (to both file and console)
    log_filename = f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Logging to {log_filename}")
    
    # 2. Load our model from the notebook
    try:
        with open('model.json', 'r') as f:
            model = json.load(f)
        
        TICKER_X = model['ticker_x']
        TICKER_Y = model['ticker_y']
        SLOPE = model['slope']
        INTERCEPT = model['intercept']
        THRESHOLD = model['trade_threshold']
        R_SQUARED = model.get('r_squared', None)  # Optional, for reference
        
        # Validate model parameters
        if not all(isinstance(v, (int, float)) and not math.isnan(v) and math.isfinite(v)
                   for v in [SLOPE, INTERCEPT, THRESHOLD]):
            raise ValueError("Invalid model parameters: contains NaN, None, or non-finite values")
        
        logging.info(f"Loaded model! Trading {TICKER_Y} vs {TICKER_X}.")
        logging.info(f"Model: {TICKER_Y} = {SLOPE:.4f} * {TICKER_X} + {INTERCEPT:.4f}")
        logging.info(f"Trade threshold (error > {THRESHOLD:.4f})")
        if R_SQUARED is not None:
            logging.info(f"Model R²: {R_SQUARED:.4f}")

    except FileNotFoundError:
        logging.error("ERROR: model.json not found! Please run the `find_our_model.ipynb` notebook first.")
        return
    except KeyError as e:
        logging.error(f"ERROR: Missing required field in model.json: {e}")
        return
    except Exception as e:
        logging.exception(f"Error loading model.json: {e}")
        return

    # 3. Log in to Kalshi
    # We use the real API, not the public one
    try:
        if YOUR_EMAIL == 'YOUR_EMAIL' or YOUR_PASSWORD == 'YOUR_PASSWORD':
            logging.error("ERROR: Please set YOUR_EMAIL and YOUR_PASSWORD in the script!")
            return
        
        # Use demo exchange for testing
        # api_client = kalshi_python.ApiInstance(email=YOUR_EMAIL, password=YOUR_PASSWORD, exchange_api_base='httpsbeta.kalshi.com')
        
        # Use this for real money
        api_client = kalshi_python.ApiInstance(email=YOUR_EMAIL, password=YOUR_PASSWORD)
        
        # We need to log in to get our user_id
        api_client.login()
        logging.info("Kalshi API login successful.")
    except Exception as e:
        logging.exception(f"Error logging in: {e}")
        logging.error("Please check your YOUR_EMAIL and YOUR_PASSWORD variables.")
        return

    # 4. Start the main loop
    logging.info("--- Starting main scan loop ---")
    retry_delay = 10  # Start with 10 seconds
    max_retry_delay = 300  # Max 5 minutes
    consecutive_errors = 0
    
    while not shutdown_requested:
        try:
            # Get the live order book for both markets
            # This is the "live" part
            orderbook_x = api_client.get_market_orderbook(ticker=TICKER_X)
            orderbook_y = api_client.get_market_orderbook(ticker=TICKER_Y)

            # Get orderbook data (handle both dict and object structures)
            orderbook_x_yes = orderbook_x.yes if hasattr(orderbook_x, 'yes') else orderbook_x.get('yes', {})
            orderbook_y_yes = orderbook_y.yes if hasattr(orderbook_y, 'yes') else orderbook_y.get('yes', {})
            
            if not orderbook_x_yes or not orderbook_y_yes:
                logging.warning("Unexpected orderbook structure. Skipping this tick.")
                time.sleep(5)
                continue

            # Get the current live mid price (to match historical data)
            live_price_x = get_mid_price(orderbook_x_yes)
            live_price_y = get_mid_price(orderbook_y_yes)

            if live_price_x is None or live_price_y is None:
                logging.warning("One market has no live price (missing bid/ask). Skipping this tick.")
                time.sleep(5)
                continue
            
            # Reset retry delay on successful iteration
            retry_delay = 10
            consecutive_errors = 0

            # 5. Run our model on the LIVE data!
            # This is the "statistical method"
            
            # First, find the "predicted" price of Y based on X
            predicted_y = (live_price_x * SLOPE) + INTERCEPT
            
            # Second, find the "live error"
            live_error = live_price_y - predicted_y

            logging.info(f"Live Prices: X={live_price_x:.2f}, Y={live_price_y:.2f} | Live Error: {live_error:.4f}")

            # 6. Check for a trade signal
            if live_error > THRESHOLD:
                # Error is high. Y is "too expensive"
                # We bet on it going down (Sell Y) and X going up (Buy X).
                logging.warning("*****************************************")
                logging.warning(f"TRADE SIGNAL: SELL PAIR (Error {live_error:.4f} > {THRESHOLD:.4f})")
                logging.warning(f"--> SELL {TICKER_Y} (it's too high)")
                logging.warning(f"--> BUY {TICKER_X} (it's too low)")
                logging.warning("*****************************************")

            elif live_error < -THRESHOLD:
                # Error is low. Y is "too cheap"
                # We bet on it going up (Buy Y) and X going down (Sell X).
                logging.warning("*****************************************")
                logging.warning(f"TRADE SIGNAL: BUY PAIR (Error {live_error:.4f} < {-THRESHOLD:.4f})")
                logging.warning(f"--> BUY {TICKER_Y} (it's too low)")
                logging.warning(f"--> SELL {TICKER_X} (it's too high)")
                logging.warning("*****************************************")
            
            # Wait 10 seconds before checking again
            time.sleep(10)

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            logging.info("Interrupted by user. Shutting down...")
            break
        except Exception as e:
            consecutive_errors += 1
            logging.exception(f"Error in main loop (consecutive errors: {consecutive_errors}): {e}")
            
            # Exponential backoff on repeated errors
            if consecutive_errors > 3:
                retry_delay = min(retry_delay * 2, max_retry_delay)
                logging.warning(f"Increasing retry delay to {retry_delay}s due to repeated errors")
            
            # Don't crash, just wait and retry
            time.sleep(retry_delay)
    
    logging.info("Bot stopped.")

# This is how you run a python file
if __name__ == "__main__":
    run_bot()


