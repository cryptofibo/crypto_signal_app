
import os
import yaml
from dataclasses import dataclass

@dataclass
class Settings:
    symbol: str
    base_timeframe: str
    higher_timeframes: list
    strong_threshold: float
    notify_enabled: bool
    notify_provider: str
    onesignal_api_key: str | None
    onesignal_app_id: str | None

    @property
    def ws_interval(self) -> str:
        m = {
            '1min':'1m','3min':'3m','5min':'5m','15min':'15m','30min':'30m',
            '1h':'1h','4h':'4h','1d':'1d'
        }
        return m.get(self.base_timeframe.lower(), '1m')

def load_settings() -> Settings:
    path = os.environ.get("WORKER_CONFIG", "config.yaml")
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    return Settings(
        symbol=raw.get("symbol","BTCUSDT"),
        base_timeframe=raw.get("base_timeframe","1min"),
        higher_timeframes=raw.get("higher_timeframes",["5min","1h"]),
        strong_threshold=float(raw.get("strong_threshold", 0.9)),
        notify_enabled=bool(raw.get("notify",{}).get("enabled", False)),
        notify_provider=str(raw.get("notify",{}).get("provider","onesignal")),
        onesignal_api_key=os.environ.get("ONESIGNAL_REST_API_KEY", ""),
        onesignal_app_id=os.environ.get("ONESIGNAL_APP_ID", ""),
    )
