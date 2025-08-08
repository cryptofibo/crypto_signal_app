
import pandas as pd
from typing import List, Dict

def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    rule = timeframe_rule(timeframe)
    o = df['open'].resample(rule).first()
    h = df['high'].resample(rule).max()
    l = df['low'].resample(rule).min()
    c = df['close'].resample(rule).last()
    v = df['volume'].resample(rule).sum()
    out = pd.concat({'open':o,'high':h,'low':l,'close':c,'volume':v}, axis=1).dropna()
    return out

def timeframe_rule(tf: str) -> str:
    tf = tf.lower()
    mapping = {
        '1min': '1min', '3min':'3min','5min':'5min','15min':'15min','30min':'30min',
        '1h':'1H','4h':'4H','1d':'1D'
    }
    return mapping.get(tf, tf)
