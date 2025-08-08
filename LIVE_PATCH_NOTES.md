
# Live-Patch

Dieses Patch fügt **Binance REST Polling** als Live-Datenquelle hinzu.

## Neue/Geänderte Dateien
- app/data/sources.py — implementiert `fetch_exchange_candles(...)` und `ExchangePoller`
- scripts/run_live_exchange.py — Pollt alle x Sekunden und druckt neue Signale
- config.live.yaml — Beispielkonfiguration für Live-Daten

## Nutzung
```bash
# In deiner bestehenden venv:
source .venv/bin/activate

# Live-Runner (Binance):
python3 -m scripts.run_live_exchange --config config.live.yaml --interval 5 --limit 500
```
Hinweis: Das ist REST-Polling, kein WebSocket. Für niedrige Latenzen können wir später WebSockets einbauen.
