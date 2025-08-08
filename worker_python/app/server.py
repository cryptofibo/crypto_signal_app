
import threading
import time
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .ws_binance import BinanceKlineWS
from .engine import SignalEngine
from .push import push_strong_signal
from .settings import Settings, load_settings

import httpx
def preload_history(symbol: str, interval: str = "1m", limit: int = 200):
    url = "https://api.binance.com/api/v3/klines"
    params = { "symbol": symbol.upper(), "interval": interval, "limit": limit }
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    rows = []
    for k in data:
        rows.append({
            "timestamp": pd.to_datetime(k[0], unit="ms", utc=True).isoformat(),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        })
    return rows

def create_app() -> FastAPI:
    cfg = load_settings()
    engine = SignalEngine(cfg)
    df_lock = threading.Lock()
    app = FastAPI()

    state = {
        "last_signals": [],
        "last_push_ts": None
    }

    def preload_async():
        try:
            rows = preload_history(cfg.symbol, interval=engine.ws_interval, limit=200)
            with df_lock:
                for row in rows:
                    engine.on_kline(row)
                state["last_signals"] = engine.last_signals_tail(200)
            print(f"[PRELOAD] loaded {len(rows)} candles")
        except Exception as e:
            print("[PRELOAD] failed:", e)

    threading.Thread(target=preload_async, daemon=True).start()

    def on_closed_kline(row):
        with df_lock:
            engine.on_kline(row)
            sig = engine.last_signal()
            state["last_signals"] = engine.last_signals_tail(200)
        if sig is not None:
            direction = 'BUY' if sig['signal'] > 0 else 'SELL'
            score = float(sig['score'])
            if cfg.notify_enabled and abs(score) >= cfg.strong_threshold:
                push_strong_signal(cfg, symbol=cfg.symbol, direction=direction, score=score, ts=str(sig['timestamp']))

    def ws_thread():
        client = BinanceKlineWS(symbol=cfg.symbol, interval=engine.ws_interval, on_closed_kline=on_closed_kline)
        while True:
            try:
                client.run_forever()
            except Exception as e:
                print("WS error loop:", e)
                time.sleep(3)

    t = threading.Thread(target=ws_thread, daemon=True)
    t.start()

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/signals")
    def signals(limit: int = 100):
        with df_lock:
            data = state["last_signals"][-limit:]
        return JSONResponse(content=data)

    @app.post("/check-strong-signals")
    def check_strong():
        with df_lock:
            last = state["last_signals"][-1] if state["last_signals"] else None
        if not last:
            return {"ok": True, "pushed": False, "reason": "no signals"}
        score = float(last["score"])
        if abs(score) >= cfg.strong_threshold and cfg.notify_enabled:
            direction = 'BUY' if last['signal'] > 0 else 'SELL'
            push_strong_signal(cfg, symbol=cfg.symbol, direction=direction, score=score, ts=str(last['timestamp']))
            return {"ok": True, "pushed": True}
        return {"ok": True, "pushed": False}

    return app
