from flask import Flask, request, render_template_string
import pandas as pd
import os

EXCEL_FILE = "價格整理.xlsx"

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>金紙手機查價</title>
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI";
    background: #f5f5f5;
    padding: 15px;
}
h2 { text-align:center; }
input, button {
    width:100%;
    padding:12px;
    font-size:18px;
    margin-top:10px;
}
.card {
    background:white;
    border-radius:10px;
    padding:15px;
    margin-top:15px;
    box-shadow:0 2px 6px rgba(0,0,0,.1);
}
.label { color:#666; font-size:14px; }
.value { font-size:22px; font-weight:bold; }
.up { color:#d32f2f; }
.ok { color:#2e7d32; }
</style>
</head>
<body>

<h2>📱 金紙手機查價</h2>

<form method="get">
    <input name="q" placeholder="輸入品項編號或名稱" value="{{q}}">
    <button type="submit">查詢</button>
</form>

{% if result %}
<div class="card">
    <div class="label">品項編號</div>
    <div class="value">{{result.code}}</div>

    <div class="label">品項名稱</div>
    <div class="value">{{result.name}}</div>

    <div class="label">最新進價</div>
    <div class="value">${{result.latest}}</div>

    <div class="label">平均進貨成本</div>
    <div class="value">${{result.avg}}</div>

    <div class="label">漲價狀態</div>
    <div class="value {{result.cls}}">{{result.notice}}</div>
</div>
{% elif q %}
<div class="card">❌ 查無資料</div>
{% endif %}

</body>
</html>
"""

def load_data():
    if not os.path.exists(EXCEL_FILE):
        return None

    latest = pd.read_excel(EXCEL_FILE, sheet_name="最新進價")
    avg = pd.read_excel(EXCEL_FILE, sheet_name="平均進貨成本")
    up = pd.read_excel(EXCEL_FILE, sheet_name="漲價提醒")
    seq = pd.read_excel(EXCEL_FILE, sheet_name="連續漲價提醒")

    return latest, avg, up, seq

@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "").strip()
    result = None

    data = load_data()
    if not data:
        return "❌ 找不到 價格整理.xlsx"

    latest, avg, up, seq = data

    if q:
        row = latest[
            latest["品項編號"].astype(str).str.contains(q) |
            latest["品項名稱"].astype(str).str.contains(q)
        ]

        if not row.empty:
            r = row.iloc[0]

            avg_row = avg[avg["品項編號"] == r["品項編號"]]
            avg_price = int(avg_row["平均進貨成本"].iloc[0]) if not avg_row.empty else 0

            notice = "正常"
            cls = "ok"

            if r["品項編號"] in seq["品項編號"].values:
                notice = "⚠ 連續漲價"
                cls = "up"
            elif r["品項編號"] in up["品項編號"].values:
                notice = "📈 有漲價"
                cls = "up"

            result = {
                "code": r["品項編號"],
                "name": r["品項名稱"],
                "latest": int(r["最新進價"]),
                "avg": avg_price,
                "notice": notice,
                "cls": cls
            }

    return render_template_string(HTML, q=q, result=result)

if __name__ == "__main__":
    print("📱 手機查價啟動中…")
    print("👉 同 Wi-Fi 手機瀏覽：http://電腦IP:5000")
    app.run(host="0.0.0.0", port=5000)
