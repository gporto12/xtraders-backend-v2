import ccxt
import pandas as pd
from datetime import datetime, timedelta

def carregar_dados_binance(symbol='BTC/USDT', timeframe='5m', desde=None, ate=None, limite=1000):
    binance = ccxt.binance()
    binance.load_markets()

    if not desde:
        desde = datetime.utcnow() - timedelta(days=1)
    if not ate:
        ate = datetime.utcnow()

    desde_ms = int(desde.timestamp() * 1000)
    all_data = []

    while True:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe, since=desde_ms, limit=limite)
        if not ohlcv:
            break
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        all_data.append(df)
        desde_ms = ohlcv[-1][0] + 1
        if datetime.utcfromtimestamp(desde_ms / 1000) > ate:
            break

    full_df = pd.concat(all_data, ignore_index=True)
    full_df['datetime'] = pd.to_datetime(full_df['timestamp'], unit='ms')
    full_df.set_index('datetime', inplace=True)
    return full_df[['open', 'high', 'low', 'close', 'volume']]
