from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# ===== 工具 =====
def format_date(date_str):
    # 2026-04-19 -> 114/04/19 (民國)
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year = dt.year - 1911
    return f"{year}/{dt.month:02d}/{dt.day:02d}"

def get_stock_name(stock):
    """
    取得股票名稱（TWSE）
    """
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        for item in data:
            if item.get("公司代號") == stock:
                return item.get("公司名稱", "未知股票")
    except:
        pass
    return "未知股票"


def get_warrants_by_date(date_str):
    """
    取得某一天的權證資料（TWSE）
    """
    roc_date = format_date(date_str)

    url = f"https://www.twse.com.tw/rwd/zh/warrant/stock?response=json&date={roc_date}"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        if "data" not in data:
            return []

        fields = data.get("fields", [])
        rows = data.get("data", [])

        results = []
        for row in rows:
            item = dict(zip(fields, row))
            results.append(item)

        return results

    except Exception as e:
        print("error:", e)
        return []


def filter_by_stock(warrants, stock):
    """
    篩出該股票相關權證
    """
    result = []
    for w in warrants:
        # 標的代號欄位名稱可能不同
        target = w.get("標的證券代號") or w.get("標的代號")

        if target == stock:
            try:
                volume = int(w.get("成交量", "0").replace(",", ""))
            except:
                volume = 0

            result.append({
                "code": w.get("權證代號"),
                "name": w.get("權證名稱"),
                "volume": volume
            })

    return result


# ===== API =====
@app.route("/api/warrant/top")
def warrant_top():
    stock = request.args.get("stock")
    date = request.args.get("date")

    if not stock:
        return jsonify({"error": "missing stock"}), 400

    # 預設今天
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    # 1. 股票名稱
    stock_name = get_stock_name(stock)

    # 2. 抓權證資料
    warrants = get_warrants_by_date(date)

    # 3. 篩選該股票
    filtered = filter_by_stock(warrants, stock)

    if not filtered:
        return jsonify({
            "stock": stock,
            "stock_name": stock_name,
            "query_date": date,
            "top": None,
            "top3": [],
            "note": "no_data"
        })

    # 4. 排序
    sorted_list = sorted(filtered, key=lambda x: x["volume"], reverse=True)

    top = sorted_list[0]
    top3 = sorted_list[:3]

    return jsonify({
        "stock": stock,
        "stock_name": stock_name,
        "query_date": date,
        "top": top,
        "top3": top3,
        "note": "official_daily_data"
    })


# ===== 啟動 =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
