
import pandas as pd

REQUIRED = ['open','high','low','close','volume']

def ensure_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in REQUIRED if c in df.columns]
    if len(cols) != len(REQUIRED):
        missing = set(REQUIRED) - set(cols)
        raise ValueError(f'Fehlende Spalten: {missing}')
    return df[REQUIRED]
