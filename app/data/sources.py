
import pandas as pd
import numpy as np
from typing import Optional, Literal
import httpx
from datetime import datetime, timezone

def load_csv_candles(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df = df.set_index('timestamp').sort_index()
    else:
        raise ValueError('CSV braucht eine timestamp-Spalte')
    return df[['open','high','low','close','volume']]

def stream_simulator(df: pd.DataFrame):
    for i in range(len(df)):
        yield df.iloc[:i+1]

# -------- Live Exchange Support (Binance via REST polling) --------

ExchangeName = Literal['binance']

BINANCE_BASE = "https://api.binance.com"

def _binance_interval(tf: str) -> str:
    tf = tf.lower()
    mapping = {
        '1min': '1m','3min':'3m','5min':'5m','15min':'15m','30min':'30m',
        '1h':'1h','4h':'4h','1d':'1d'
    }
    return mapping.get(tf, '1m')

def fetch_exchange_candles(symbol: str, timeframe: str, limit: int = 1000, exchange: ExchangeName = 'binance') -> pd.DataFrame:
    if exchange != 'binance':
        raise NotImplementedError('Nur binance ist aktuell implementiert')
    interval = _binance_interval(timeframe)
    url = f"{BINANCE_BASE}/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    # Binance kline fields:
    # [ openTime, open, high, low, close, volume, closeTime, qav, trades, takerBase, takerQuote, ignore ]
    rows = []
    for k in data:
        ts = pd.to_datetime(k[0], unit='ms', utc=True)
        rows.append({
            "timestamp": ts,
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        })
    df = pd.DataFrame(rows).set_index("timestamp").sort_index()
    return df[['open','high','low','close','volume']]

class ExchangePoller:
    """Simple REST poller that fetches the latest N candles periodically."""
    def __init__(self, symbol: str, timeframe: str, limit: int = 500, exchange: ExchangeName='binance'):
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit
        self.exchange = exchange

    def fetch(self) -> pd.DataFrame:
        return fetch_exchange_candles(self.symbol, self.timeframe, self.limit, exchange=self.exchange)
