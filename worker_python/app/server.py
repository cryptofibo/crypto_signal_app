
import threading
import time
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .ws_binance import BinanceKlineWS
from .engine import SignalEngine
from .push import push_strong_signal
from .settings import Settings, load_settings

def create_app() -> FastAPI:
    cfg = load_settings()
    engine = SignalEngine(cfg)
    df_lock = threading.Lock()
    app = FastAPI()

    # shared state
    state = {
        "last_signals": [],  # list of dicts
        "last_push_ts": None
    }

    def on_closed_kline(row):
        # row: dict with timestamp, open, high, low, close, volume
        with df_lock:
            engine.on_kline(row)
            sig = engine.last_signal()
            state["last_signals"] = engine.last_signals_tail(200)
        # push if strong:
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
        """Fallback for cron: check last signal and push if strong."""
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
