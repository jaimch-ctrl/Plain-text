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
    return "台積電"
    
def get_stock_volume(stock):
    return 12345678, "114/04/19"

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
