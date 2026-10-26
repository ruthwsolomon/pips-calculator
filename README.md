# Lot Size Calculator

A small Flask web app that calculates lot size from stop loss (pips),
the amount risked, and the pip value per lot.

lot size = risk / (pips x pip value)

## Run it locally

1. python -m venv venv
2. .\venv\Scripts\activate
3. pip install -r requirements.txt
4. python app.py
5. Open http://127.0.0.1:5000