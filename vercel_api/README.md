
# Vercel API

## ENV in Vercel
- WORKER_URL = https://<your-railway-service>.up.railway.app

## Routes
- GET /api/health
- GET /api/signals -> proxy zu Worker /signals
- GET /api/push-strong-signals (Cron) -> triggert Worker /check-strong-signals

## Cron
Configured to run every 10 minutes in vercel.json. Adjust as needed.
