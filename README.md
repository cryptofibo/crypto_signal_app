# Crypto Signal App – Starterkit

Dieses Starterprojekt liefert dir eine saubere Basis für **verlässliche Kauf-/Verkaufssignale** mit
Multi‑Zeitrahmen‑Analyse, gewichteten Indikatoren, Backtesting, Whale‑Alerts (Stub) und Push-Benachrichtigungen (Stub).

## Schnellstart

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Dummy-Daten erzeugen (BTCUSDT 1m)
python scripts/generate_dummy_data.py --symbol BTCUSDT --minutes 3000

# Backtest ausführen (nutzt config.example.yaml)
python scripts/run_backtest.py --config config.example.yaml

# Live-Modus (Simulation mit Dummy-Datenstrom)
python scripts/run_live.py --config config.example.yaml
```

## Struktur

- `app/data/` Datenquellen & Resampling (Multi-Timeframe)
- `app/indicators/` RSI, MACD, EMA
- `app/engine/` Signalgewichtung, Modi, Kombinationslogik, Whale-Alerts (Stub)
- `app/backtest/` Backtester & Metriken
- `app/notify/` Push-Benachrichtigungen (FCM/OneSignal als Stubs)
- `app/api/` FastAPI-Server (optional)
- `scripts/` Hilfsskripte für Backtest & Live
- `config.example.yaml` Beispielkonfiguration

## Hinweis
- **Kein Live-Exchange-API-Key** enthalten. Ersetze die Stubs in `app/data/sources.py` und `app/engine/whale.py`.
- Die Implementierung ist bewusst kompakt gehalten, damit du schnell erweitern kannst.
