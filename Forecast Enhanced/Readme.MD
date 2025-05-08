# Market Forecasting con MetaTrader5

Un'applicazione Python modulare per:
- Previsione di breve termine sui mercati (1h)
- Calcolo scenari probabilistici con Monte Carlo
- Stima volatilità condizionata (GARCH)
- Validazione rolling con ARIMA
- Output in Markdown con analisi automatica

---

## ⚙️ Requisiti

- Python >= 3.8
- MetaTrader5 (`pip install MetaTrader5`)
- pandas, numpy, pytz
- statsmodels, arch

```bash
pip install pandas numpy pytz statsmodels arch MetaTrader5
```

---

## 📂 Struttura del progetto

```
market_analysis_mt5/
├── main.py
├── data/
│   └── price_fetcher.py
├── models/
│   └── forecast_combiner.py
├── scenarios/
│   └── montecarlo.py
├── utils/
│   ├── logging.py
│   └── analysis_report.py
├── validation/
│   └── backtest.py
└── output/
    └── <report generati>
```

---

## ▶️ Esecuzione

```bash
python main.py
```

Verrà richiesto un **simbolo** (es. `XGER30`, `EURUSD`, ecc). Al termine dell'elaborazione:
- Il report verrà salvato in `output/`
- Sarà eseguito un backtest storico

---

## 📊 Output Markdown

- Prezzo corrente
- Trend generale
- 3 scenari con probabilità
- Classificazione di **volatilità** e **momentum**

---

## 📚 Note

- Il forecast è ottenuto con ARIMA(3,1,0)
- La volatilità è stimata tramite GARCH(1,1)
- Gli scenari Monte Carlo usano drift + random walk
- Il sistema è estensibile a modelli machine learning o Prophet

---

## 🚀 To Do (futuro)

- Aggiunta modelli LSTM/GRU
- Integrazione con Telegram/Slack per invio automatico report
- Supporto multi-timeframe
