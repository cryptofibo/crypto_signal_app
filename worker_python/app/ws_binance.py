
import json
import pandas as pd
from websocket import WebSocketApp

STREAM_URL = "wss://stream.binance.com:9443/ws"

def _kline_stream(symbol: str, interval: str) -> str:
    return f"{symbol.lower()}@kline_{interval}"

class BinanceKlineWS:
    def __init__(self, symbol: str, interval: str, on_closed_kline):
        self.symbol = symbol.upper()
        self.interval = interval
        self.on_closed_kline = on_closed_kline
        self.ws = None

    def _on_message(self, ws, msg):
        data = json.loads(msg)
        k = data.get('k')
        if not k:
            return
        if not k.get('x', False):
            return
        ts = pd.to_datetime(k['T'], unit='ms', utc=True)
        row = {
            "timestamp": ts.isoformat(),
            "open": float(k['o']),
            "high": float(k['h']),
            "low": float(k['l']),
            "close": float(k['c']),
            "volume": float(k['v']),
        }
        try:
            self.on_closed_kline(row)
        except Exception as e:
            print("[WS] on_closed_kline error:", e)

    def _on_error(self, ws, err):
        print("[WS] error:", err)

    def _on_close(self, ws, code, msg):
        print("[WS] closed", code, msg)

    def _on_open(self, ws):
        print("[WS] connected")

    def run_forever(self):
        url = f"{STREAM_URL}/{_kline_stream(self.symbol, self.interval)}"
        self.ws = WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        self.ws.run_forever()
