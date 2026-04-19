from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import requests
import json

app = Flask(__name__)
CORS(app)


COMMON_STOCK_NAMES = {
    "2330": "台積電",
    "2454": "聯發科",
    "2317": "鴻海",
    "2303": "聯電",
    "2881": "富邦金",
    "2882": "國泰金",
    "1301": "台塑",
    "1303": "南亞"
}


def roc_date_from_yyyymmdd(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
        return f"{dt.year - 1911}/{dt.month:02d}/{dt.day:02d}"
    except Exception:
        return ""


def get_stock_name(stock: str) -> str:
    # 先用常用對照，避免公開 API 不穩時整個變空
    if stock in COMMON_STOCK_NAMES:
        return COMMON_STOCK_NAMES[stock]

    # 再嘗試 TWSE OpenAPI
    try:
        url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
        res = requests.get(url, timeout=10)
        data = res.json()

        if isinstance(data, list):
            for item in data:
                if str(item.get("公司代號", "")).strip() == str(stock).strip():
                    return item.get("公司名稱", "未知股票")
    except Exception as e:
        print("get_stock_name error:", e)

    return "未知股票"


def get_stock_volume(stock: str):
    """
    回傳:
    volume: 當月最後一筆日成交量（若遇休市日，通常會是最近一個交易日）
    date: 民國日期字串
    source: 資料來源
    market_status: open / closed / no_data
    """
    try:
        today = datetime.now().strftime("%Y%m01")
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        params = {
            "response": "json",
            "date": today,
            "stockNo": stock
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.twse.com.tw/"
        }

        res = requests.get(url, params=params, headers=headers, timeout=15)
        data = res.json()

        rows = data.get("data", [])
        if not rows:
            return 0, "", "twse_stock_day", "no_data"

        latest = rows[-1]
        # TWSE STOCK_DAY 格式:
        # [日期, 成交股數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌價差, 成交筆數]
        raw_date = str(latest[0]).strip()
        raw_volume = str(latest[1]).replace(",", "").strip()

        volume = int(raw_volume) if raw_volume.isdigit() else 0
        date = raw_date

        return volume, date, "twse_stock_day", "closed"

    except Exception as e:
        print("get_stock_volume error:", e)
        return 0, "", "twse_stock_day", "no_data"


@app.route("/api/warrant/top")
def get_top():
    stock = request.args.get("stock", "").strip()

    if not stock:
        return jsonify({"error": "missing stock"}), 400

    stock_name = get_stock_name(stock)
    volume, date, source, market_status = get_stock_volume(stock)

    # 先保留你目前前端需要的格式
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
        "source": source,
        "market_status": market_status,
        "top": top,
        "top3": top3
    }

    return Response(
        json.dumps(result, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
