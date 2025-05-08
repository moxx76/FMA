# File: models/forecast_combiner.py

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from utils.logging import log


def combined_forecast(df, forecast_steps=60):
    try:
        y = df['close'].copy()

        if not np.isfinite(y).all():
            log("Serie storica contiene valori non finiti (NaN o inf).")
            return None, None, None

        y.index = pd.to_datetime(y.index)
        y = y.asfreq('min')
        y = y.ffill()  # Sostituito fillna(method='ffill') con ffill()

        # Forecast ARIMA
        model_arima = ARIMA(y, order=(2, 1, 2))
        arima_fit = model_arima.fit()
        arima_forecast = arima_fit.forecast(steps=forecast_steps)

        # GARCH sulla serie di ritorni
        returns = 100 * y.pct_change().dropna()
        if not np.isfinite(returns).all():
            log("Serie dei ritorni non valida per GARCH.")
            return None, None, None

        model_garch = arch_model(returns, vol='Garch', p=1, q=1, rescale=True)
        garch_fit = model_garch.fit(disp='off')
        garch_vol = garch_fit.forecast(horizon=forecast_steps).variance.values[-1, :]

        # Stimare trend direzionale
        if len(y) >= 20:
            trend = 'up' if y.iloc[-1] > y.iloc[-20] else 'down' if y.iloc[-1] < y.iloc[-20] else 'flat'
        else:
            trend = 'flat'

        return arima_forecast.values, garch_vol, trend

    except Exception as e:
        log(f"Errore nella previsione combinata: {str(e)}")
        return None, None, None
