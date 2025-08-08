
from __future__ import annotations
from pydantic import BaseModel
from typing import List, Dict, Literal, Optional
import yaml

RiskMode = Literal['konservativ','normal','aggressiv']

class Weights(BaseModel):
    rsi: float = 0.35
    macd: float = 0.40
    ema_cross: float = 0.25

class Thresholds(BaseModel):
    buy: float = 0.6
    sell: float = -0.6

class RSIConf(BaseModel):
    period: int = 14
    oversold: float = 30
    overbought: float = 70

class MACDConf(BaseModel):
    fast: int = 12
    slow: int = 26
    signal: int = 9

class EMAConf(BaseModel):
    fast: int = 12
    slow: int = 26

class WhaleConf(BaseModel):
    enabled: bool = False
    min_value_usd: float = 1_000_000

class NotifyConf(BaseModel):
    enabled: bool = False
    provider: Literal['fcm','onesignal'] = 'fcm'
    api_key: str = 'REPLACE_ME'

class DataConf(BaseModel):
    source: Literal['csv','exchange'] = 'csv'
    csv_path: str = 'data/BTCUSDT_1min.csv'

class Settings(BaseModel):
    symbol: str = 'BTCUSDT'
    base_timeframe: str = '1min'
    higher_timeframes: List[str] = ['5min','1H']
    risk_mode: Literal['konservativ','normal','aggressiv','normal'] = 'normal'
    weights: Weights = Weights()
    thresholds: Thresholds = Thresholds()
    rsi: RSIConf = RSIConf()
    macd: MACDConf = MACDConf()
    ema: EMAConf = EMAConf()
    whale_alerts: WhaleConf = WhaleConf()
    notify: NotifyConf = NotifyConf()
    data: DataConf = DataConf()

def load_settings(path: str) -> Settings:
    with open(path, 'r') as f:
        raw = yaml.safe_load(f)
    return Settings(**raw)
