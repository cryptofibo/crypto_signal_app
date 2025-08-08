
import pandas as pd
import numpy as np

def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = (delta.clip(lower=0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / (loss.replace(0, 1e-9))
    return 100 - (100 / (1 + rs))
