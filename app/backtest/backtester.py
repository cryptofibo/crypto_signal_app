
import pandas as pd
import numpy as np
from typing import Dict
from ..engine.signals import generate_signals

def backtest(df_mtf: Dict[str, pd.DataFrame], cfg, fee: float = 0.0005):
    base = list(df_mtf.values())[0].copy()
    base = base.sort_index()
    sigs = generate_signals(df_mtf, cfg)
    close = base['close'].reindex(sigs.index)

    position = sigs['signal'].replace(0, method='ffill').fillna(0)  # -1,0,1
    # PnL: pos(t-1) * return(t)
    ret = close.pct_change().fillna(0)
    pnl = position.shift(1).fillna(0) * ret
    # Gebühren bei Signalwechsel
    trades = (position != position.shift(1)).astype(int)
    fee_cost = trades * fee * abs(position)  # approximiert
    pnl = pnl - fee_cost

    equity = (1 + pnl).cumprod().rename('equity')
    return sigs, equity
