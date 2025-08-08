
from fastapi import FastAPI
from ..config import load_settings
from ..data.sources import load_csv_candles
from ..data.resample import resample_ohlcv
from ..engine.signals import generate_signals
from ..backtest.backtester import backtest
from ..backtest.metrics import compute_kpis

import pandas as pd

app = FastAPI()

@app.get('/health')
def health():
    return {'ok': True}

@app.post('/signals')
def api_signals(config_path: str):
    cfg = load_settings(config_path)
    base = load_csv_candles(cfg.data.csv_path)
    mtf = {cfg.base_timeframe: base}
    for tf in cfg.higher_timeframes:
        mtf[tf] = resample_ohlcv(base, tf)
    sigs = generate_signals(mtf, cfg)
    return sigs.tail(300).reset_index().to_dict(orient='records')

@app.post('/backtest')
def api_backtest(config_path: str):
    cfg = load_settings(config_path)
    base = load_csv_candles(cfg.data.csv_path)
    mtf = {cfg.base_timeframe: base}
    for tf in cfg.higher_timeframes:
        mtf[tf] = resample_ohlcv(base, tf)
    sigs, equity = backtest(mtf, cfg)
    kpis = compute_kpis(equity)
    return {'kpis': kpis, 'last_equity': float(equity.iloc[-1])}
