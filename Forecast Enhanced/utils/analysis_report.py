# File: utils/analysis_report.py

from datetime import datetime, timedelta
import pytz
import os
from utils.logging import log
import numpy as np


def describe_all_scenarios(scenarios, probs, current_price):
    all_scenarios = []
    for i, (s, prob) in enumerate(zip(scenarios, probs)):
        low, high = round(s.min(), 2), round(s.max(), 2)
        trend = "rialzista" if s[-1] > current_price else "ribassista" if s[-1] < current_price else "laterale"
        all_scenarios.append({
            "rank": i + 1,
            "probability": prob,
            "trend": trend,
            "arrival_range": (low, high)
        })
    # Ordina per probabilità decrescente
    all_scenarios.sort(key=lambda x: x['probability'], reverse=True)
    log("Descrizione di tutti gli scenari completata.")
    # Conta categorie
    category_counts = {"Dominante": 0, "Alternativo": 0, "Marginale": 0}
    for sc in all_scenarios:
        label = "Dominante" if sc['probability'] >= 0.20 else "Alternativo" if sc['probability'] >= 0.10 else "Marginale"
        category_counts[label] += 1
    for sc in all_scenarios:
        sc['category'] = "Dominante" if sc['probability'] >= 0.20 else "Alternativo" if sc['probability'] >= 0.10 else "Marginale"
    return all_scenarios, category_counts


def summarize_trend_distribution(all_scenarios):
    summary = {}
    for sc in all_scenarios:
        trend = sc['trend']
        summary[trend] = summary.get(trend, 0) + sc['probability']
    return summary


def generate_market_analysis(symbol, current_price, scenarios, probs, hist_vol, all_scenarios_tuple, df, validity_minutes=60, forecast_price=None, forecast_range=None):
    try:
        tz_local = pytz.timezone('Europe/Rome')
        now_dt = datetime.now(tz_local)
        now_str = now_dt.strftime('%d/%m/%Y %H:%M')
        expiry_dt = now_dt + timedelta(minutes=validity_minutes)
        expiry_str = expiry_dt.strftime('%d/%m/%Y %H:%M')

        # Nuova logica per trend generale basata sulla previsione
        if forecast_price and forecast_price > current_price * 1.001:
            general_trend = "Rialzista"
        elif forecast_price and forecast_price < current_price * 0.999:
            general_trend = "Ribassista"
        else:
            general_trend = "Laterale"

        all_scenarios, category_counts = all_scenarios_tuple
        trend_distribution = summarize_trend_distribution(all_scenarios)
        majority = max(trend_distribution, key=trend_distribution.get)

        md = [
            f"# 🔍 Analisi {symbol} – {now_str}",
            "---",
            "## 📊 Quadro Generale",
            f"- **Prezzo corrente:** {current_price:.2f}",
            f"- **Prezzo previsto ARIMA:** {forecast_price:.2f}" if forecast_price else "",
            f"- **Range atteso:** {forecast_range[0]:.2f} - {forecast_range[1]:.2f}" if forecast_range else "",
            f"- **Validità previsione:** fino al {expiry_str}",
            f"- **Trend generale:** {general_trend}",
            f"- **Distribuzione scenari:** " + ", ".join([
                f"{k.title()}: {v:.1%}" for k, v in trend_distribution.items()
            ]),
            "---",
            "## 🔮 Scenari Monte Carlo e Range di Arrivo",
            f"- **Totale scenari Dominanti:** {category_counts['Dominante']}",
            f"- **Totale scenari Alternativi:** {category_counts['Alternativo']}",
            f"- **Totale scenari Marginali:** {category_counts['Marginale']}"
        ]

        for sc in all_scenarios:
            r = sc["rank"]
            label = sc["category"]
            low, high = sc["arrival_range"]
            md += [
                f"### Scenario #{r} - Prob. {sc['probability']:.1%} ({label})",
                f"- **Trend:** {sc['trend'].title()}",
                f"- **Range di arrivo stimato:** tra {low:.2f} e {high:.2f}"
            ]

        md += [
            "---",
            "## ⚡ Volatilità & Momentum"
        ]
        hist_pct = hist_vol / current_price * 100
        vol_cat = "Bassa" if hist_pct < 0.2 else "Standard" if hist_pct < 0.5 else "Alta"

        most = int(np.argmax(probs))
        change_pct = (scenarios[most][-1] - current_price) / current_price * 100
        mom_cat = "Basso" if abs(change_pct) < 0.2 else "Medio" if abs(change_pct) < 0.5 else "Alto"

        md += [
            f"- **Volatilità storica:** {vol_cat}",
            f"- **Momentum:** {mom_cat}",
            "---",
            "### Cosa si intende per Volatilità",
            "La volatilità misura l'ampiezza delle variazioni di prezzo in un determinato periodo. Una volatilità alta indica oscillazioni ampie, mentre una volatilità bassa segnala movimenti più contenuti.",
            "### Legenda categorie di scenario",
"- **Dominante**: probabilità ≥ 20%",
"- **Alternativo**: probabilità tra 10% e 20%",
"- **Marginale**: probabilità < 10%",
"",
"### Cosa si intende per Momentum",
            "Il momentum rappresenta la velocità di variazione del prezzo. Un momentum elevato suggerisce un forte slancio nella direzione del trend, mentre un momentum basso indica movimenti più rallentati."
        ]

        return "\n".join([line for line in md if line])
    except Exception as e:
        log(f"Errore nella generazione dell'analisi: {str(e)}")
        return f"# Errore nell'analisi\nSi è verificato un errore durante la generazione dell'analisi: {str(e)}"


def save_analysis(content, filename):
    try:
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        log(f"Analisi testuale salvata: {filename}")
    except Exception as e:
        log(f"Errore nel salvataggio dell'analisi: {str(e)}")











