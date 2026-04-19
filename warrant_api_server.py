from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ===== 工具 =====

def format_date(date_str):
    # 2026-04-19 -> 114/04/19
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year = dt.year - 1911
    return f"{year}/{dt.month:02d}/{dt.day:02d}"

def get_stock_name(stock):
    try:
        url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
        res = requests.get(url, timeout=10)
        data = res.json()

        if not isinstance(data, list):
            return "未知股票"

        for item in data:
            if item.get("公司代號") == stock:
                return item.get("公司名稱", "未知股票")

        return "未知股票"
    except Exception as e:
        print("stock name error:", e)
        return "未知股票"

def get_stock_volume(stock):
    try:
        url = f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?stockNo={stock}&response=json"
        res = requests.get(url, timeout=10)
        data = res.json()

        if "data" not in data or not data["data"]:
            return 0, ""

        latest = data["data"][-1]

        volume = int(latest[1].replace(",", ""))
        date = latest[0]

        return volume, date
    except Exception as e:
        print("volume error:", e)
        return 0, ""

# ===== API =====

@app.route("/api/warrant/top")
def get_top():
    stock = request.args.get("stock", "")

    if not stock:
        return jsonify({"error": "missing stock"}), 400

    stock_name = get_stock_name(stock)
    volume, date = get_stock_volume(stock)

    # 模擬權證（你之後可以換真資料）
    top = {
        "code": "033872",
        "volume": volume
    }

    top3 = [
        {"code": "033872", "volume": volume},
        {"code": "044111", "volume": int(volume * 0.7)},
        {"code": "055222", "volume": int(volume * 0.5)}
    ]

    return jsonify({
        "stock": stock,
        "stock_name": stock_name,
        "volume": volume,
        "date": date,
        "top": top,
        "top3": top3
    })

# ===== 啟動 =====

if __name__ == "__main__":
    app.run()
