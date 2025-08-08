
import pandas as pd

def weighted_score(indicator_scores: pd.DataFrame, weights: dict) -> pd.Series:
    # indicator_scores columns are standardized to [-1,1]
    out = None
    for col, w in weights.items():
        if col in indicator_scores:
            contrib = indicator_scores[col] * float(w)
            out = contrib if out is None else out.add(contrib, fill_value=0)
    return out.fillna(0).rename('score')
