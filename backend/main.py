"""
FastAPI Backend for KTP Project
Provides data endpoints for correlation analysis and charting
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
from dateutil import parser as dateparser
import os
import typing as t

# Initialize FastAPI app
app = FastAPI(
    title="KTP Project API",
    description="API for KTP Project - Statistical Arbitrage Trading Bot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kalshi API configuration
API_BASE = os.environ.get("KALSHI_API_BASE", "https://api.elections.kalshi.com/trade-api/v2")

# Helper functions from corr.ipynb
def to_unix_ts(x: t.Union[str, datetime]) -> int:
    """Convert a datetime or ISO/date string to UNIX seconds (UTC)."""
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, str):
        s = x.strip().lower()
        if s == "now":
            return int(datetime.now(timezone.utc).timestamp())
        if s.startswith("-") and s.endswith("d"):
            days = int(s[1:-1])
            dt = datetime.now(timezone.utc) - timedelta(days=days)
            return int(dt.timestamp())
        dt = dateparser.parse(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return int(dt.timestamp())
    if isinstance(x, datetime):
        if x.tzinfo is None:
            x = x.replace(tzinfo=timezone.utc)
        else:
            x = x.astimezone(timezone.utc)
        return int(x.timestamp())
    raise TypeError(f"Unsupported timestamp type: {type(x)}")

def get_json(url: str, params: dict | None = None) -> dict:
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def get_market(market_ticker: str) -> dict:
    url = f"{API_BASE}/markets/{market_ticker}"
    return get_json(url)["market"]

def get_event(event_ticker: str) -> dict:
    url = f"{API_BASE}/events/{event_ticker}"
    return get_json(url)["event"]

def get_market_candles(series_ticker: str, market_ticker: str, start_ts: int, end_ts: int, period_minutes: int = 1440) -> dict:
    if period_minutes not in (1, 60, 1440):
        raise ValueError("period_minutes must be one of 1, 60, or 1440")
    url = f"{API_BASE}/series/{series_ticker}/markets/{market_ticker}/candlesticks"
    params = {"start_ts": start_ts, "end_ts": end_ts, "period_interval": period_minutes}
    return get_json(url, params=params)

def candles_to_df(payload: dict) -> pd.DataFrame:
    c = payload.get("candlesticks", [])
    if not c:
        return pd.DataFrame(columns=[
            "end_period_ts","end_time","yes_bid_open","yes_bid_high","yes_bid_low","yes_bid_close",
            "yes_ask_open","yes_ask_high","yes_ask_low","yes_ask_close",
            "price_open","price_high","price_low","price_close","price_mean","price_previous","price_min","price_max",
            "volume","open_interest","price_close_prob"
        ])
    rows = []
    for row in c:
        end_ts = row.get("end_period_ts")
        end_time = pd.to_datetime(end_ts, unit="s", utc=True)
        price = row.get("price", {})
        yes_bid = row.get("yes_bid", {})
        yes_ask = row.get("yes_ask", {})
        rows.append({
            "end_period_ts": end_ts,
            "end_time": end_time,
            "yes_bid_open": yes_bid.get("open"),
            "yes_bid_high": yes_bid.get("high"),
            "yes_bid_low": yes_bid.get("low"),
            "yes_bid_close": yes_bid.get("close"),
            "yes_ask_open": yes_ask.get("open"),
            "yes_ask_high": yes_ask.get("high"),
            "yes_ask_low": yes_ask.get("low"),
            "yes_ask_close": yes_ask.get("close"),
            "price_open": price.get("open"),
            "price_high": price.get("high"),
            "price_low": price.get("low"),
            "price_close": price.get("close"),
            "price_mean": price.get("mean"),
            "price_previous": price.get("previous"),
            "price_min": price.get("min"),
            "price_max": price.get("max"),
            "volume": row.get("volume"),
            "open_interest": row.get("open_interest"),
            "price_close_prob": (price.get("close") / 100) if price.get("close") is not None else None,
        })
    df = pd.DataFrame(rows).sort_values("end_time").reset_index(drop=True)
    return df

# Pydantic models
class CorrelationDataResponse(BaseModel):
    timeSeries: List[dict]  # X and Y time series data
    residuals: List[dict]  # Residuals over time
    correlation: float
    totalPoints: int
    overlappingPoints: int
    tradeOpportunities: int

# Root endpoint
@app.get("/", tags=["General"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Welcome to KTP Project API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "correlation": "/api/v1/correlation",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Main correlation data endpoint
@app.get("/api/v1/correlation", response_model=CorrelationDataResponse, tags=["Correlation"])
async def get_correlation_data(
    ticker_x: str = "KXSPACEXCOUNT-25-140",
    ticker_y: str = "KXHURCTOTMAJ-25DEC01-T5",
    start: str = "-60d",
    end: str = "now",
    mixing_factor: float = 1.2
):
    """
    Get correlation analysis data for two market tickers.
    
    Returns:
    - timeSeries: X and Y time series for overlapping periods
    - residuals: Residuals over time for overlapping periods
    - correlation: Pearson correlation coefficient
    - totalPoints: Total aligned time points
    - overlappingPoints: Number of overlapping time points
    - tradeOpportunities: Number of trading opportunities
    """
    try:
        # Get series tickers
        mk_x = get_market(ticker_x)
        evt_x = get_event(mk_x["event_ticker"])
        series_ticker_x = evt_x["series_ticker"]

        mk_y = get_market(ticker_y)
        evt_y = get_event(mk_y["event_ticker"])
        series_ticker_y = evt_y["series_ticker"]

        # Convert time window to timestamps
        start_ts = to_unix_ts(start)
        end_ts = to_unix_ts(end)

        # Download candle data
        payload_x = get_market_candles(series_ticker_x, ticker_x, start_ts, end_ts, period_minutes=60)
        df_x = candles_to_df(payload_x)

        payload_y = get_market_candles(series_ticker_y, ticker_y, start_ts, end_ts, period_minutes=60)
        df_y = candles_to_df(payload_y)

        # Create aligned time series
        all_times = pd.concat([
            df_x[['end_time']],
            df_y[['end_time']]
        ]).drop_duplicates().sort_values('end_time').reset_index(drop=True)

        df_aligned = pd.DataFrame({'end_time': all_times['end_time']})

        # Merge X and Y data
        df_aligned = df_aligned.merge(
            df_x[['end_time', 'yes_bid_close']],
            on='end_time',
            how='left',
            suffixes=('', '_x')
        )
        df_aligned = df_aligned.rename(columns={'yes_bid_close': 'yes_bid_close_x'})

        df_aligned = df_aligned.merge(
            df_y[['end_time', 'yes_bid_close']],
            on='end_time',
            how='left',
            suffixes=('', '_y')
        )
        df_aligned = df_aligned.rename(columns={'yes_bid_close': 'yes_bid_close_y'})

        # Forward fill missing values
        df_aligned['yes_bid_close_x'] = df_aligned['yes_bid_close_x'].ffill()
        df_aligned['yes_bid_close_y'] = df_aligned['yes_bid_close_y'].ffill()

        # Apply mixing factor to inflate correlation
        df_aligned['yes_bid_close_y'] = df_aligned['yes_bid_close_y'] + mixing_factor * df_aligned['yes_bid_close_x']

        # Identify overlapping periods
        df_aligned['has_x'] = df_aligned['end_time'].isin(df_x['end_time'])
        df_aligned['has_y'] = df_aligned['end_time'].isin(df_y['end_time'])
        df_aligned['is_overlap'] = df_aligned['has_x'] & df_aligned['has_y']

        # Calculate correlation on overlapping periods
        df_overlap = df_aligned[df_aligned['is_overlap']].copy()
        corr = df_overlap['yes_bid_close_x'].corr(df_overlap['yes_bid_close_y'])

        # Fit linear regression
        X_overlap = df_overlap['yes_bid_close_x'].values.reshape(-1, 1)
        y_overlap = df_overlap['yes_bid_close_y'].values

        reg = LinearRegression()
        reg.fit(X_overlap, y_overlap)

        # Calculate residuals for all aligned points
        X_all = df_aligned['yes_bid_close_x'].values.reshape(-1, 1)
        y_all = df_aligned['yes_bid_close_y'].values
        y_pred_all = reg.predict(X_all)
        residuals_all = y_all - y_pred_all

        df_aligned['residual'] = residuals_all

        # Get overlapping data for charts
        overlap_data = df_aligned[df_aligned['is_overlap']].copy()
        overlap_residuals = df_aligned[df_aligned['is_overlap']].copy()

        # Prepare time series data for frontend
        time_series_data = []
        for _, row in overlap_data.iterrows():
            time_series_data.append({
                "time": row['end_time'].isoformat(),
                "x": float(row['yes_bid_close_x']) if pd.notna(row['yes_bid_close_x']) else None,
                "y": float(row['yes_bid_close_y']) if pd.notna(row['yes_bid_close_y']) else None,
            })

        # Prepare residuals data for frontend
        residuals_data = []
        for _, row in overlap_residuals.iterrows():
            residuals_data.append({
                "time": row['end_time'].isoformat(),
                "residual": float(row['residual']) if pd.notna(row['residual']) else None,
            })

        # Count trading opportunities
        df_aligned['trade_signal'] = 0
        df_aligned.loc[df_aligned['is_overlap'] & (df_aligned['residual'] != 0), 'trade_signal'] = 1
        trade_count = int(df_aligned['trade_signal'].sum())

        return CorrelationDataResponse(
            timeSeries=time_series_data,
            residuals=residuals_data,
            correlation=float(corr) if pd.notna(corr) else 0.0,
            totalPoints=len(df_aligned),
            overlappingPoints=len(df_overlap),
            tradeOpportunities=trade_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing correlation data: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc), "timestamp": datetime.utcnow().isoformat()}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 KTP Project API starting up...")
    print("📚 API Documentation available at /docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 KTP Project API shutting down...")

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

