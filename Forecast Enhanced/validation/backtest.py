# File: validation/backtest.py

import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from utils.logging import log


def validate_prediction(df, steps):
    try:
        close = df['close']
        window_size = 240
        total = len(close)

        errors = []

        for start in range(0, total - window_size - steps, steps):
            train = close.iloc[start:start + window_size]
            test = close.iloc[start + window_size:start + window_size + steps]

            if len(test) < steps:
                continue

            try:
                model = ARIMA(train, order=(3, 1, 0))
                fit = model.fit()
                pred = fit.forecast(steps=steps)

                rmse = np.sqrt(np.mean((pred.values - test.values) ** 2))
                errors.append(rmse)
            except:
                continue

        if errors:
            avg_rmse = np.mean(errors)
            log(f"Backtest completato su {len(errors)} finestre - RMSE medio: {avg_rmse:.4f}")
        else:
            log("Backtest non eseguito: dati insufficienti o errore nei modelli.")

    except Exception as e:
        log(f"Errore nella validazione storica: {str(e)}")
