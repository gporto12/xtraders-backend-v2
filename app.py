from flask import Flask, request, jsonify, send_from_directory
import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# IMPORTAÇÕES DO BACKTEST
from backtest.controller import executar_backtest_invert50

app = Flask(__name__, static_folder=".", static_url_path="")

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# === ROTA ORIGINAL ===
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "your_key_here")

@app.route("/run-backtest", methods=["POST"])
def run_backtest():
    symbol = "X:BTC-USD"
    timeframe = "day"

    try:
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=30)
        from_str = from_date.strftime("%Y-%m-%d")
        to_str = to_date.strftime("%Y-%m-%d")

        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/{timeframe}/{from_str}/{to_str}?adjusted=true&sort=asc&limit=5000&apiKey={POLYGON_API_KEY}"
        response = requests.get(url)
        data = response.json()
        candles = data.get("results", [])

        if not candles:
            return jsonify({"error": "Nenhum dado encontrado."}), 400

        df = pd.DataFrame(candles)
        df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
        df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]

        trades = []
        for i in range(min(20, len(df))):
            row = df.iloc[i]
            trade = {
                "data": row["timestamp"].strftime("%Y-%m-%d"),
                "fechamento": row["close"],
                "setup": "INSPEÇÃO VISUAL",
                "avaliacao_ia": "Candle diário carregado com sucesso.",
                "nota": 10.0
            }
            trades.append(trade)

        return jsonify({"trades": trades})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === NOVA ROTA PARA BACKTEST COM BINANCE (INVERT 50 - VENDA) ===
@app.route("/backtest/invert50", methods=["GET"])
def backtest_invert50():
    try:
        resultado = executar_backtest_invert50()
        return jsonify(resultado.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
