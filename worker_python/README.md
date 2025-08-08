
# Worker (Railway)

## Env Vars required
- ONESIGNAL_REST_API_KEY = <your key>
- ONESIGNAL_APP_ID = <your app id>
- WORKER_CONFIG = /app/config.yaml  (optional)

## Deploy (Railway)
1. GitHub-Repo verbinden (Ordner `worker_python/` als Root).
2. Build command automatisch (Dockerfile / Nixpacks).
3. Expose Port 8000 (Auto).
4. Env-Variablen setzen.
5. Deploy.

## Endpoints
- GET /health
- GET /signals?limit=100
- POST /check-strong-signals
