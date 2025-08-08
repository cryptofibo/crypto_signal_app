
import pandas as pd
import numpy as np
from .settings import Settings

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = (delta.clip(lower=0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / (loss.replace(0, 1e-9))
    return 100 - (100 / (1 + rs))

def macd(close: pd.Series, fast=12, slow=26, signal=9):
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def standardize(series: pd.Series, lo: float, hi: float) -> pd.Series:
    return ((series - lo) / (hi - lo) * 2 - 1).clip(-1,1)

class SignalEngine:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self.df = pd.DataFrame(columns=['open','high','low','close','volume'])
        self.lasts = []

    @property
    def ws_interval(self) -> str:
        return self.cfg.ws_interval

    def on_kline(self, row: dict):
        ts = pd.to_datetime(row['timestamp'])
        self.df.loc[ts, ['open','high','low','close','volume']] = [row['open'],row['high'],row['low'],row['close'],row['volume']]
        self.df = self.df.sort_index()
        self._recalc()

    def _indicator_scores(self, df: pd.DataFrame):
        out = pd.DataFrame(index=df.index)
        r = rsi(df['close'], 14)
        out['rsi'] = (1 - standardize(r, 30, 70))
        _, _, hist = macd(df['close'], 12,26,9)
        roll = hist.rolling(100, min_periods=10).std().replace(0, 1e-9)
        out['macd'] = (hist / (3*roll)).clip(-1,1)
        fast = ema(df['close'], 12)
        slow = ema(df['close'], 26)
        out['ema_cross'] = ((fast > slow).astype(int)*2 - 1).astype(float)
        return out

    def _recalc(self):
        df = self.df.copy()
        if len(df) < 50:
            return
        scores = self._indicator_scores(df)
        total = (0.35*scores['rsi'] + 0.40*scores['macd'] + 0.25*scores['ema_cross']).rename('score')
        buy_thr, sell_thr = 0.6, -0.6
        sig = pd.Series(0, index=df.index)
        sig[total >= buy_thr] = 1
        sig[total <= sell_thr] = -1
        last = df.index[-1]
        out = {
            "timestamp": last.isoformat(),
            "score": float(total.iloc[-1]),
            "signal": int(sig.iloc[-1])
        }
        self.lasts.append(out)
        if len(self.lasts) > 1000:
            self.lasts = self.lasts[-1000:]

    def last_signal(self):
        return self.lasts[-1] if self.lasts else None

    def last_signals_tail(self, n: int):
        return self.lasts[-n:]
