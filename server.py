from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

# ─── CONFIGURAÇÕES ───────────────────────────────────────────
API_KEY    = os.environ.get("BINANCE_API_KEY", "SUA_API_KEY_AQUI")
API_SECRET = os.environ.get("BINANCE_API_SECRET", "SUA_API_SECRET_AQUI")
SYMBOL     = "RAYUSDT"
LEVERAGE   = 15
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN", "meu_token_secreto")
# ─────────────────────────────────────────────────────────────

client = Client(API_KEY, API_SECRET)

def set_leverage():
    try:
        client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)
    except Exception as e:
        print(f"Alavancagem já configurada ou erro: {e}")

def get_balance_usdt():
    account = client.futures_account()
    for asset in account["assets"]:
        if asset["asset"] == "USDT":
            return float(asset["availableBalance"])
    return 0.0

def get_symbol_price():
    ticker = client.futures_symbol_ticker(symbol=SYMBOL)
    return float(ticker["price"])

def get_step_size():
    info = client.futures_exchange_info()
    for s in info["symbols"]:
        if s["symbol"] == SYMBOL:
            for f in s["filters"]:
                if f["filterType"] == "LOT_SIZE":
                    return float(f["stepSize"])
    return 1.0

def round_qty(qty, step):
    import math
    precision = len(str(step).rstrip("0").split(".")[-1]) if "." in str(step) else 0
    return round(math.floor(qty / step) * step, precision)

def close_all_positions():
    positions = client.futures_position_information(symbol=SYMBOL)
    for pos in positions:
        amt = float(pos["positionAmt"])
        if amt == 0:
            continue
        side = SIDE_SELL if amt > 0 else SIDE_BUY
        client.futures_create_order(
            symbol=SYMBOL,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=abs(amt),
            reduceOnly=True
        )
        print(f"Posição fechada: {amt} {SYMBOL}")

def open_position(side: str):
    """side: 'long' ou 'short'"""
    set_leverage()
    balance = get_balance_usdt()
    price   = get_symbol_price()
    step    = get_step_size()

    raw_qty = (balance * LEVERAGE) / price
    qty     = round_qty(raw_qty, step)

    if qty <= 0:
        print("Saldo insuficiente para abrir posição.")
        return

    order_side = SIDE_BUY if side == "long" else SIDE_SELL

    order = client.futures_create_order(
        symbol=SYMBOL,
        side=order_side,
        type=ORDER_TYPE_MARKET,
        quantity=qty
    )
    print(f"Ordem {side.upper()} aberta: {qty} {SYMBOL} | Preço: {price}")
    return order

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    # Verificação de segurança com token
    token = data.get("token") or request.args.get("token")
    if token != WEBHOOK_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    sinal = str(data.get("sinal", "")).lower()
    print(f"Sinal recebido: {sinal}")

    if sinal not in ("long", "short"):
        return jsonify({"error": "Sinal inválido. Use 'long' ou 'short'"}), 400

    try:
        close_all_positions()
        open_position(sinal)
        return jsonify({"status": "ok", "sinal": sinal}), 200
    except Exception as e:
        print(f"Erro ao executar ordem: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Bot OTT rodando!"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
