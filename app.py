from flask import Flask, request, render_template_string
import yfinance as yf
from pycoingecko import CoinGeckoAPI
import plotly.graph_objs as go
import pandas as pd

app = Flask(__name__)
cg = CoinGeckoAPI()

# ---------------- HTML Chat Interface ----------------
html = """
<!doctype html>
<html>
<head>
    <title>R_AlgoBuddy 🌞</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #ffecd2, #fcb69f);
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            max-width: 750px;
            margin: 30px auto;
        }
        h2 {
            text-align: center;
            color: #ff7f50;
            margin-bottom: 20px;
        }
        .chat-box {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        .message {
            padding: 10px 15px;
            border-radius: 20px;
            margin: 8px 0;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user {
            background-color: #fff9c4;
            align-self: flex-end;
        }
        .bot {
            background-color: #ffe0b2;
            align-self: flex-start;
        }
        form {
            display: flex;
            margin-top: 10px;
        }
        input[type=text] {
            flex: 1;
            padding: 10px;
            border-radius: 20px;
            border: 1px solid #ccc;
        }
        input[type=submit] {
            margin-left: 5px;
            padding: 10px 18px;
            border-radius: 20px;
            border: none;
            background-color: #ffb347;
            color: white;
            cursor: pointer;
            transition: 0.3s;
        }
        input[type=submit]:hover {
            background-color: #ffcc33;
        }
        a {
            text-decoration: none;
            color: #007BFF;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        .dashboard-card {
            background: #fff8dc;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
<div class="container">
    <h2>R_AlgoBuddy 🌞<br>Track, Predict & Shine! ✨</h2>
    <div class="chat-box">
      <form action="/" method="post">
        <input type="text" name="user_input" placeholder="Ask something..." required>
        <input type="submit" value="Send">
      </form>
      <p><a href="/dashboard">Go to Dashboard 📊</a></p>
      <div class="chat-container">
      {% if response %}
        {% for msg in response %}
            <div class="message {{ msg.type }}">{{ msg.text|safe }}</div>
        {% endfor %}
      {% endif %}
      </div>
    </div>
</div>
</body>
</html>
"""

# ---------------- Utility Functions ----------------
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            return f"{symbol} stock is at ${price:.2f}"
        return "Stock data not available."
    except:
        return "Error fetching stock data."

def analyze_stock_trend(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="10d")
        if data.empty: return "No data to analyze."
        data['MA5'] = data['Close'].rolling(5).mean()
        data['MA10'] = data['Close'].rolling(10).mean()
        latest = data.iloc[-1]
        trend = "neutral ➖"
        if latest['MA5'] > latest['MA10']: trend = "upward 📈"
        elif latest['MA5'] < latest['MA10']: trend = "downward 📉"
        return f"{symbol}: {trend}"
    except:
        return "Error analyzing trend."

def get_crypto_price(coin):
    try:
        data = cg.get_price(ids=coin, vs_currencies='usd')
        price = data[coin]['usd']
        return f"{coin.capitalize()} is at ${price}"
    except:
        return "Error fetching crypto price."

def analyze_crypto_trend(coin):
    try:
        data = cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days=10)
        prices = [p[1] for p in data['prices']]
        ma5 = sum(prices[-5:])/5
        ma10 = sum(prices[-10:])/10
        latest = prices[-1]
        trend = "neutral ➖"
        if ma5 > ma10: trend = "upward 📈"
        elif ma5 < ma10: trend = "downward 📉"
        return f"{coin.capitalize()}: {trend}"
    except:
        return "Error analyzing crypto trend."

# ---------------- Chat Route ----------------
@app.route("/", methods=["GET","POST"])
def chat():
    messages = []
    if request.method == "POST":
        user_input = request.form["user_input"].lower()
        messages.append({"type":"user","text":user_input})

        if "price" in user_input:
            if any(x in user_input for x in ["aapl","amzn","tsla","goog"]):
                symbol = [x.upper() for x in ["aapl","amzn","tsla","goog"] if x in user_input][0]
                messages.append({"type":"bot","text":get_stock_price(symbol)})
            elif any(x in user_input for x in ["bitcoin","ethereum","dogecoin"]):
                coin = [x for x in ["bitcoin","ethereum","dogecoin"] if x in user_input][0]
                messages.append({"type":"bot","text":get_crypto_price(coin)})
        elif "trend" in user_input:
            if any(x in user_input for x in ["aapl","amzn","tsla","goog"]):
                symbol = [x.upper() for x in ["aapl","amzn","tsla","goog"] if x in user_input][0]
                messages.append({"type":"bot","text":analyze_stock_trend(symbol)})
            elif any(x in user_input for x in ["bitcoin","ethereum","dogecoin"]):
                coin = [x for x in ["bitcoin","ethereum","dogecoin"] if x in user_input][0]
                messages.append({"type":"bot","text":analyze_crypto_trend(coin)})
        else:
            messages.append({"type":"bot","text":f"Got your question: '{user_input}'. Soon more insights!"})

    return render_template_string(html,response=messages)

# ---------------- Dashboard ----------------
@app.route("/dashboard")
def dashboard():
    stocks = ["AAPL","TSLA","MSFT"]
    cryptos = ["bitcoin","ethereum","dogecoin"]
    dashboard_html = "<h2>📊 R_AlgoBuddy Dashboard 🌞</h2>"

    # Stocks
    for s in stocks:
        data = yf.Ticker(s).history(period="30d")
        if not data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=s))
            fig.update_layout(title=f"{s} 30-Day Prices", xaxis_title="Date", yaxis_title="USD")
            dashboard_html += f'<div class="dashboard-card">{fig.to_html(full_html=False)}</div>'

    # Cryptos
    for c in cryptos:
        data = cg.get_coin_market_chart_by_id(id=c, vs_currency='usd', days=30)
        prices = pd.DataFrame(data['prices'], columns=['Timestamp','Price'])
        prices['Date'] = pd.to_datetime(prices['Timestamp'], unit='ms')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices['Date'], y=prices['Price'], mode='lines', name=c.capitalize()))
        fig.update_layout(title=f"{c.capitalize()} 30-Day Prices", xaxis_title="Date", yaxis_title="USD")
        dashboard_html += f'<div class="dashboard-card">{fig.to_html(full_html=False)}</div>'

    dashboard_html += '<p><a href="/">Back to Chat 💬</a></p>'
    return dashboard_html

# ---------------- Run App ----------------
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

