from flask import Flask, request, render_template_string
import pandas as pd

FILE = "價格整理.xlsx"

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>手機查價</title>
<style>
body { font-family: Arial; padding:15px; background:#f6f6f6; }
input, select { width:100%; padding:12px; font-size:18px; margin:6px 0; }
button { width:100%; padding:14px; font-size:18px; background:#2c7be5; color:white; border:none; }
.card { background:white; padding:12px; margin-top:10px; border-radius:8px; }
.price { font-size:22px; color:#d6336c; }
</style>
</head>
<body>

<h2>📱 手機查價</h2>

<form method="get">
<input name="q" placeholder="品項編號或名稱" value="{{q}}">
<select name="year">
<option value="">全部年度</option>
{% for y in years %}
<option value="{{y}}" {% if y==year %}selected{% endif %}>{{y}}</option>
{% endfor %}
</select>

<input type="date" name="start" value="{{start}}">
<input type="date" name="end" value="{{end}}">

<button type="submit">查詢</button>
</form>

{% for r in rows %}
<div class="card">
<b>{{r['品項編號']}} {{r['品項名稱']}}</b><br>
最新進價：<span class="price">${{r['最新進價']}}</span><br>
平均成本：${{r['平均進貨成本']}}<br>
最新進貨日：{{r['最新進貨日']}}
</div>
{% endfor %}

</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q","").strip()
    year = request.args.get("year","")
    start = request.args.get("start","")
    end = request.args.get("end","")

    df = pd.read_excel(FILE, sheet_name="整理後明細")
    latest = pd.read_excel(FILE, sheet_name="最新進價")
    avg = pd.read_excel(FILE, sheet_name="平均進貨成本")

    df["日期"] = pd.to_datetime(df["日期"])

    if year:
        df = df[df["年度"] == int(year)]
    if start:
        df = df[df["日期"] >= start]
    if end:
        df = df[df["日期"] <= end]

    if q:
        df = df[
            df["品項編號"].astype(str).str.contains(q, case=False) |
            df["品項名稱"].astype(str).str.contains(q, case=False)
        ]

    items = df["品項編號"].unique()

    rows = []
    for code in items:
        r1 = latest[latest["品項編號"] == code]
        r2 = avg[avg["品項編號"] == code]
        if r1.empty:
            continue
        rows.append({
            "品項編號": code,
            "品項名稱": r1.iloc[0]["品項名稱"],
            "最新進價": int(r1.iloc[0]["最新進價"]),
            "最新進貨日": r1.iloc[0]["最新進貨日"],
            "平均進貨成本": int(r2.iloc[0]["平均進貨成本"]) if not r2.empty else ""
        })

    years = sorted(df["年度"].dropna().unique())

    return render_template_string(
        HTML,
        rows=rows,
        q=q,
        year=year,
        years=years,
        start=start,
        end=end
    )

if __name__ == "__main__":
    print("📱 手機查價啟動中…")
    print("👉 同一個 Wi-Fi 手機瀏覽：")
    print("👉 http://你的電腦IP:5000")
    app.run(host="0.0.0.0", port=5000)
