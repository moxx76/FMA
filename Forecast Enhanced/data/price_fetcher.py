# File: data/price_fetcher.py

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
from utils.logging import log


def get_price_data(symbol, timeframe, lookback_minutes):
    tz_utc = pytz.timezone('Etc/UTC')
    tz_local = pytz.timezone('Europe/Rome')

    try:
        end = datetime.now(tz_utc)
        start = end - timedelta(minutes=lookback_minutes)
        rates = mt5.copy_rates_range(symbol, timeframe, start, end)

        if rates is None or len(rates) == 0:
            log(f"Errore: dati non disponibili per {symbol}.")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
        df.set_index('time', inplace=True)
        df = df.tz_convert(tz_local)

        log(f"Dati recuperati per {symbol}: {len(df)} candele.")
        return df
    except Exception as e:
        log(f"Errore durante il recupero dei dati per {symbol}: {str(e)}")
        return None


def get_current_price(symbol):
    try:
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            log(f"Errore: impossibile ottenere il tick attuale per {symbol}.")
            return None
        return (tick.bid + tick.ask) / 2
    except Exception as e:
        log(f"Errore durante il recupero del prezzo corrente per {symbol}: {str(e)}")
        return None
