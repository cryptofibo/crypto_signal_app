
import pandas as pd
from typing import Dict
from ..indicators.rsi import rsi as rsi_func
from ..indicators.macd import macd as macd_func
from ..indicators.ema import ema_cross_signal
from .weighting import weighted_score
from .modes import adjust_thresholds
from .whale import whale_score

def standardize(series: pd.Series, lo: float, hi: float) -> pd.Series:
    return ((series - lo) / (hi - lo) * 2 - 1).clip(-1,1)

def build_indicator_scores(df: pd.DataFrame, cfg) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    # RSI -> low=oversold (30) high=overbought (70); invert so that oversold => +1
    r = rsi_func(df['close'], cfg.rsi.period)
    rsi_std = (1 - standardize(r, cfg.rsi.oversold, cfg.rsi.overbought)).rename('rsi')
    out['rsi'] = rsi_std

    # MACD histogram -> scale roughly to [-1,1] via rolling std
    _, _, hist = macd_func(df['close'], cfg.macd.fast, cfg.macd.slow, cfg.macd.signal)
    roll = hist.rolling(100, min_periods=10).std().replace(0, 1e-9)
    macd_std = (hist / (3*roll)).clip(-1,1).rename('macd')
    out['macd'] = macd_std

    # EMA Cross -> already in {-1, +1}
    ema_sig = ema_cross_signal(df['close'], cfg.ema.fast, cfg.ema.slow).astype(float)
    out['ema_cross'] = ema_sig

    return out

def combine_scores(base_scores: pd.DataFrame, cfg) -> pd.DataFrame:
    whale = whale_score(base_scores.index, enabled=cfg.whale_alerts.enabled)
    scores = base_scores.join(whale, how='left')
    weights = {**cfg.weights.dict(), 'whale': 0.1 if cfg.whale_alerts.enabled else 0.0}
    total = weighted_score(scores, weights)
    return scores.join(total)

def generate_signals(df_mtf: Dict[str, pd.DataFrame], cfg):
    # Erwartet dict: timeframe -> OHLCV DataFrame (gleich ausgerichtete Indizes)
    # Wir nutzen base_timeframe für Score, höhere TF nur zur Bestätigung
    base = df_mtf[cfg.base_timeframe]
    base_scores = build_indicator_scores(base, cfg)
    combined = combine_scores(base_scores, cfg)
    buy_thr, sell_thr = adjust_thresholds(cfg.thresholds.buy, cfg.thresholds.sell, cfg.risk_mode)

    # Higher TF Confirmation: einfache Regel – Score > 0 auf ALLEN höheren TF (konservativ)
    def tf_confirm(direction: int) -> pd.Series:
        confirms = []
        for tf, df in df_mtf.items():
            if tf == cfg.base_timeframe: 
                continue
            sc = build_indicator_scores(df, cfg)
            cm = combine_scores(sc, cfg)['score']
            confirms.append(cm > 0 if direction > 0 else cm < 0)
        if not confirms:
            return pd.Series(True, index=base.index)
        res = confirms[0]
        for c in confirms[1:]:
            res = res & c.reindex_like(base, method='ffill').fillna(False)
        return res.reindex_like(base, method='ffill').fillna(False)

    conf_buy_all = tf_confirm(+1)
    conf_sell_all = tf_confirm(-1)

    # Modi
    if cfg.risk_mode == 'konservativ':
        buy_mask = (combined['score'] >= buy_thr) & conf_buy_all
        sell_mask = (combined['score'] <= sell_thr) & conf_sell_all
    elif cfg.risk_mode == 'aggressiv':
        buy_mask = (combined['score'] >= buy_thr)
        sell_mask = (combined['score'] <= sell_thr)
    else:  # normal -> 2 von 3: wir approximieren über: entweder Score stark genug ODER mind. eine TF bestätigt
        buy_mask = (combined['score'] >= buy_thr) & (conf_buy_all | (combined['score'] >= buy_thr + 0.1))
        sell_mask = (combined['score'] <= sell_thr) & (conf_sell_all | (combined['score'] <= sell_thr - 0.1))

    signals = pd.Series(0, index=base.index, name='signal')
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return combined.join(signals)
