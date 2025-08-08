
import argparse, time
from app.config import load_settings
from app.data.sources import ExchangePoller
from app.data.resample import resample_ohlcv
from app.engine.signals import generate_signals

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--interval', type=float, default=5.0, help='Polling interval in seconds')
    ap.add_argument('--limit', type=int, default=500, help='Number of candles to fetch each poll')
    args = ap.parse_args()

    cfg = load_settings(args.config)
    poller = ExchangePoller(symbol=cfg.symbol, timeframe=cfg.base_timeframe, limit=args.limit)
    last_signal = None

    while True:
        try:
            base = poller.fetch()
            mtf = {cfg.base_timeframe: base}
            for tf in cfg.higher_timeframes:
                mtf[tf] = resample_ohlcv(base, tf)
            sigs = generate_signals(mtf, cfg)
            last = sigs.iloc[-1]
            if last_signal != int(last['signal']):
                last_signal = int(last['signal'])
                if last_signal != 0:
                    print(f"{base.index[-1]} -> LIVE SIGNAL: {last_signal}, Score={last['score']:.3f}")
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print('beende...')
            break
        except Exception as e:
            print('Fehler:', e)
            time.sleep(args.interval)

if __name__ == '__main__':
    main()
