
import pandas as pd
from .ema import ema

def macd(close: pd.Series, fast: int=12, slow: int=26, signal: int=9):
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line.rename('macd'), signal_line.rename('signal'), hist.rename('hist')
