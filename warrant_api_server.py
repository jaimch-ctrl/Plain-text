from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import requests
import json

app = Flask(__name__)
CORS(app)

COMMON = {
    "2330": "台積電",
    "2454": "聯發科",
    "2317": "鴻海",
    "2303": "聯電"
}

def get_name(stock):
    if stock in COMMON:
        return COMMON[stock]
    try:
        url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
        data = requests.get(url, timeout=10).json()
        for x in data:
            if str(x.get("公司代號")) == stock:
                return x.get("公司名稱", "未知股票")
    except:
        pass
    return "未知股票"

def get_volume(stock):
    try:
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        params = {
            "response": "json",
            "date": datetime.now().strftime("%Y%m01"),
            "stockNo": stock
        }
        data = requests.get(url, params=params, timeout=10).json()
        rows = data.get("data", [])
        if rows:
            last = rows[-1]
            vol = int(last[1].replace(",", ""))
            date = last[0]
            return vol, date
    except:
        pass
    return 0, ""

@app.route("/api/warrant/top")
def api():
    stock = request.args.get("stock", "")
    if not stock:
        return jsonify({"error": "missing stock"}), 400

    name = get_name(stock)
    volume, date = get_volume(stock)

    result = {
        "stock": stock,
        "stock_name": name,
        "volume": volume,
        "date": date,
        "top": {
            "code": stock,  # 🔥 先用股票代號，不亂給
            "volume": volume
        },
        "top3": []
    }

    return Response(
        json.dumps(result, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )

if __name__ == "__main__":
    app.run()
