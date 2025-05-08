# File: scenarios/montecarlo.py

import numpy as np
from utils.logging import log


def generate_monte_carlo_scenarios(current_price, volatility, trend, num_scenarios=7, steps=60):
    try:
        if volatility is None or not np.isfinite(volatility) or volatility == 0:
            log("Volatilità nulla o non valida, impossibile generare scenari Monte Carlo.")
            return [], []

        dt = 1 / 60
        mu = 0.0002 if trend == "up" else -0.0002 if trend == "down" else 0

        scenarios = []
        for _ in range(num_scenarios):
            shocks = np.random.normal(loc=mu * dt, scale=volatility * np.sqrt(dt), size=steps)
            path = current_price * np.exp(np.cumsum(shocks))
            scenarios.append(path)

        scenarios = np.array(scenarios)

        # Calcolo delle probabilità con pesi normalizzati
        final_prices = scenarios[:, -1]
        deviations = np.abs(final_prices - current_price)
        inv_dev = 1 / (deviations + 1e-6)
        probs = inv_dev / np.sum(inv_dev)

        return scenarios, probs

    except Exception as e:
        log(f"Errore nella generazione degli scenari Monte Carlo: {str(e)}")
        return [], []

