
import pandas as pd
import numpy as np

def compute_kpis(equity_curve: pd.Series) -> dict:
    ret = equity_curve.pct_change().fillna(0)
    total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1
    sharpe = (ret.mean() / (ret.std() + 1e-9)) * np.sqrt(252*24*60)  # überhöht für 1min, aber ok als Bsp.
    dd = (equity_curve / equity_curve.cummax() - 1).min()
    return {
        'total_return': float(total_return),
        'max_drawdown': float(dd),
        'sharpe_like': float(sharpe),
    }
