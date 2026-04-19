from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)


def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year = dt.year - 1911
    return f"{year}/{dt.month:02d}/{dt.day:02d}"


def get_stock_name(stock):
    try:
        url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
        params = {
            "ex_ch": f"tse_{stock}.tw|otc_{stock}.tw",
            "json": "1",
            "delay": "0"
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://mis.twse.com.tw/stock/fibest.jsp"
        }

        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()
        arr = data.get("msgArray", [])

        if arr and arr[0].get("n"):
            return arr[0].get("n")

    except Exception as e:
        print("MIS name error:", e)

    try:
        url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
        res = requests.get(url, timeout=10)
        data = res.json()

        if isinstance(data, list):
            for item in data:
                if str(item.get("公司代號")) == str(stock):
                    return item.get("公司名稱", "未知股票")
    except Exception as e:
        print("OpenAPI name error:", e)

    return "未知股票"


def get_stock_volume(stock):
    try:
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        params = {
            "response": "json",
            "date": datetime.now().strftime("%Y%m01"),
            "stockNo": stock
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.twse.com.tw/"
        }

        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()

        if "data" in data and data["data"]:
            latest = data["data"][-1]
            volume = int(str(latest[1]).replace(",", ""))
            date = latest[0]
            return volume, date

    except Exception as e:
        print("TWSE volume error:", e)

    return 0, ""

@app.route("/api/warrant/top")
def get_top():
    stock = request.args.get("stock", "")

    if not stock:
        return jsonify({"error": "missing stock"}), 400

    stock_name = get_stock_name(stock)
    volume, date = get_stock_volume(stock)

    top = {
        "code": "033872",
        "volume": volume
    }

    top3 = [
        {"code": "033872", "volume": volume},
        {"code": "044111", "volume": int(volume * 0.7)},
        {"code": "055222", "volume": int(volume * 0.5)}
    ]

    result = {
        "stock": stock,
        "stock_name": stock_name,
        "volume": volume,
        "date": date,
        "top": top,
        "top3": top3
    }

    return Response(
        json.dumps(result, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
