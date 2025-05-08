# File: main.py

import os
from datetime import datetime
from scenarios.montecarlo import generate_monte_carlo_scenarios
from models.forecast_combiner import combined_forecast
from utils.analysis_report import generate_market_analysis, save_analysis, describe_all_scenarios
from data.price_fetcher import get_price_data, get_current_price
from utils.logging import log
import pandas as pd
import numpy as np


def main():
    symbol = input("Inserisci simbolo da analizzare (es. XGER30): ").upper()
    try:
        df = get_price_data(symbol, timeframe=1, lookback_minutes=1440)
        if df is None or df.empty or not df['close'].apply(np.isfinite).all():
            log("Dataset non valido per la previsione: dati vuoti o non finiti.")
            return

        # Salva i dati puliti per debug
        df.to_csv(f"output/{symbol}_dataset_cleaned.csv")

        forecast_steps = 60
        arima_forecast, garch_vol, trend = combined_forecast(df, forecast_steps)

        if arima_forecast is None:
            log("Forecast combinato non disponibile. Procedura interrotta.")
            return

        forecast_price = float(arima_forecast[-1])
        forecast_range = (float(min(arima_forecast)), float(max(arima_forecast)))

        current_price = df['close'].iloc[-1]
        scenarios, probs = generate_monte_carlo_scenarios(current_price, garch_vol, trend)

        if scenarios is None or len(scenarios) == 0 or any(s is None or not np.isfinite(s).all() for s in scenarios) or not np.isfinite(probs).all():
            log("Simulazioni Monte Carlo non valide. Procedura interrotta.")
            return

        log("Generati 6 scenari Monte Carlo avanzati.")

        all_scenarios_tuple = describe_all_scenarios(scenarios, probs, current_price)
        log("Descrizione di tutti gli scenari completata.")

        report_md = generate_market_analysis(
            symbol=symbol,
            current_price=current_price,
            scenarios=scenarios,
            probs=probs,
            hist_vol=garch_vol,
            all_scenarios_tuple=all_scenarios_tuple,
            df=df,
            validity_minutes=60,
            forecast_price=forecast_price,
            forecast_range=forecast_range
        )

        output_path = f"output/{symbol}_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        save_analysis(report_md, output_path)
        log(f"Analisi {symbol} completata e salvata in {output_path}.")

    except Exception as e:
        log(f"Errore in main: {str(e)}")


if __name__ == '__main__':
    main()

