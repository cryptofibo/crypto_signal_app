
import httpx
from .settings import Settings

def push_strong_signal(cfg: Settings, symbol: str, direction: str, score: float, ts: str):
    if cfg.notify_provider == 'onesignal':
        _push_onesignal(cfg, title=f"{symbol} {direction}", body=f"Score {score:.2f} | {ts}")
    else:
        print("[PUSH noop]", symbol, direction, score, ts)

def _push_onesignal(cfg: Settings, title: str, body: str):
    headers = {
        "Authorization": f"Basic {cfg.onesignal_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "app_id": cfg.onesignal_app_id,
        "included_segments": ["All"],
        "headings": {"en": title},
        "contents": {"en": body}
    }
    try:
        with httpx.Client(timeout=10) as client:
            r = client.post("https://api.onesignal.com/notifications", headers=headers, json=payload)
            if 200 <= r.status_code < 300:
                print("[PUSH OneSignal] sent")
            else:
                print("[PUSH OneSignal] error", r.status_code, r.text)
    except Exception as e:
        print("[PUSH OneSignal] exception", e)
