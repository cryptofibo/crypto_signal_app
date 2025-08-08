
import pandas as pd

def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def ema_cross_signal(close: pd.Series, fast: int, slow: int) -> pd.Series:
    fast_ema = ema(close, fast)
    slow_ema = ema(close, slow)
    # +1 if fast > slow; -1 if fast < slow
    sig = (fast_ema > slow_ema).astype(int)*2 - 1
    return sig.rename('ema_cross')
