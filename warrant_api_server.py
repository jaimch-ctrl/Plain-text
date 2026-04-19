from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)


def format_date(date_str):
    try:
        if "/" in date_str:
            return date_str
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year = dt.year - 1911
        return f"{year}/{dt.month:02d}/{dt.day:02d}"
    except Exception:
        return date_str


def get_stock_name(stock):
    # 先用 Shioaji / fallback 可再補
    mapping = {
        "2330": "台積電",
        "2454": "聯發科",
        "2317": "鴻海",
        "2303": "聯電"
    }
    return mapping.get(str(stock), "未知股票")


def get_stock_volume_from_shioaji(stock):
    try:
        import shioaji as sj

        api_key = os.getenv("SHIOAJI_API_KEY", "").strip()
        secret_key = os.getenv("SHIOAJI_SECRET_KEY", "").strip()

        if not api_key or not secret_key:
            return 0, "", "missing_key"

        api = sj.Shioaji(simulation=False)
        api.login(api_key=api_key, secret_key=secret_key)

        contract = api.Contracts.Stocks[str(stock)]
        snapshot = api.snapshots([contract])[0]

        volume = int(getattr(snapshot, "volume", 0) or 0)

        snap_date = getattr(snapshot, "date", "")
        if snap_date:
            try:
                dt = datetime.strptime(str(snap_date), "%Y-%m-%d")
                date_str = f"{dt.year - 1911}/{dt.month:02d}/{dt.day:02d}"
            except Exception:
                date_str = str(snap_date)
        else:
            now = datetime.now()
            date_str = f"{now.year - 1911}/{now.month:02d}/{now.day:02d}"

        try:
            api.logout()
        except Exception:
            pass

        return volume, date_str, "shioaji"

    except Exception as e:
        print("shioaji error:", e)
        return 0, "", "shioaji_error"


def get_top():
    stock = request.args.get("stock", "").strip()

    if not stock:
        return jsonify({"error": "missing stock"}), 400

    stock_name = get_stock_name(stock)

    volume, date, source = get_stock_volume_from_shioaji(stock)

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
        "top": top,
        "top3": top3
    }

    return Response(
        json.dumps(result, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


app.add_url_rule("/api/warrant/top", "get_top", get_top)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
