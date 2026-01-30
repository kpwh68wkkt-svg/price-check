from flask import Flask, render_template_string, request
import pandas as pd
import os

# ================= 設定 =================
CSV_FILE = "LINE_查價_單品快速.csv"
APP_TITLE = "📱 金紙即時查價"

# ================= Flask App =================
app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 "PingFang TC", "Microsoft JhengHei", sans-serif;
    margin: 0;
    background: #f5f5f5;
}
.header {
    background: #222;
    color: white;
    padding: 14px;
    text-align: center;
    font-size: 20px;
}
.container {
    padding: 12px;
}
input {
    width: 100%;
    padding: 14px;
    font-size: 18px;
    margin-bottom: 12px;
    border-radius: 8px;
    border: 1px solid #ccc;
}
.card {
    background: white;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.name {
    font-size: 18px;
    font-weight: bold;
}
.price {
    color: #d32f2f;
    font-size: 22px;
    margin-top: 6px;
}
.date {
    color: #666;
    font-size: 14px;
    margin-top: 4px;
}
.empty {
    text-align: center;
    color: #888;
    margin-top: 40px;
}
</style>
</head>

<body>
<div class="header">{{ title }}</div>

<div class="container">
<form method="get">
    <input type="text" name="q" placeholder="🔍 輸入品名或編號" value="{{ q }}">
</form>

{% if results %}
    {% for r in results %}
    <div class="card">
        <div class="name">{{ r["品項名稱"] }}（{{ r["品項編號"] }}）</div>
        <div class="price">{{ r["最新進價"] }}</div>
        <div class="date">📅 {{ r["最新進貨日"] }}</div>
    </div>
    {% endfor %}
{% else %}
    {% if q %}
    <div class="empty">查無資料</div>
    {% endif %}
{% endif %}
</div>

</body>
</html>
"""

# ================= 路由 =================
@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "").strip()

    if not os.path.exists(CSV_FILE):
        return f"找不到 {CSV_FILE}，請先執行『金紙進貨整理』程式"

    df = pd.read_csv(CSV_FILE, dtype=str)

    results = []
    if q:
        mask = (
            df["品項名稱"].str.contains(q, case=False, na=False) |
            df["品項編號"].str.contains(q, case=False, na=False)
        )
        results = df[mask].to_dict("records")

    return render_template_string(
        HTML,
        title=APP_TITLE,
        q=q,
        results=results
    )

# ================= 啟動 =================
if __name__ == "__main__":
    print("📱 手機查價啟動中…")
    print("👉 同一個 Wi-Fi 的手機瀏覽：")
    print("👉 http://電腦IP:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
