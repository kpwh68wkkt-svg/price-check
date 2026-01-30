from flask import Flask, request, render_template_string
import pandas as pd

# =============================
# 基本設定
# =============================
EXCEL_FILE = "進貨明細.xlsx"

app = Flask(__name__)

# =============================
# 讀取並整理資料（一次）
# =============================
df = pd.read_excel(EXCEL_FILE)

df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
df["年度"] = df["年度"].astype(str)
df["數量"] = pd.to_numeric(df["數量"], errors="coerce").fillna(0)
df["單價"] = pd.to_numeric(df["單價"], errors="coerce").fillna(0)

df = df[df["數量"] > 0]

# =============================
# HTML（手機友善）
# =============================
HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>📱 金紙手機查價</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial; background:#f5f5f5; padding:10px; }
.card { background:#fff; padding:12px; border-radius:10px; margin-bottom:12px; }
input, select, button {
  width:100%; padding:10px; margin-top:6px;
  border-radius:6px; border:1px solid #ccc;
}
button { background:#007aff; color:#fff; font-size:16px; }
table { width:100%; border-collapse:collapse; margin-top:10px; }
th, td { padding:6px; border-bottom:1px solid #ddd; font-size:14px; }
th { background:#eee; }
</style>
</head>
<body>

<div class="card">
<form method="get">
<label>年度</label>
<select name="year">
<option value="">全部</option>
{% for y in years %}
<option value="{{y}}" {% if y==year %}selected{% endif %}>{{y}}</option>
{% endfor %}
</select>

<label>起始日期</label>
<input type="date" name="start" value="{{start}}">

<label>結束日期</label>
<input type="date" name="end" value="{{end}}">

<button type="submit">🔍 查詢</button>
</form>
</div>

{% if data %}
<div class="card">
<table>
<tr>
<th>品項編號</th>
<th>品項名稱</th>
<th>平均進貨成本</th>
</tr>
{% for r in data %}
<tr>
<td>{{r["品項編號"]}}</td>
<td>{{r["品項名稱"]}}</td>
<td>${{r["平均進貨成本"]}}</td>
</tr>
{% endfor %}
</table>
</div>
{% endif %}

</body>
</html>
"""

# =============================
# 查詢頁
# =============================
@app.route("/", methods=["GET"])
def index():
    year = request.args.get("year", "")
    start = request.args.get("start", "")
    end = request.args.get("end", "")

    temp = df.copy()

    if year:
        temp = temp[temp["年度"] == year]

    if start:
        temp = temp[temp["日期"] >= pd.to_datetime(start)]

    if end:
        temp = temp[temp["日期"] <= pd.to_datetime(end)]

    result = []

    if not temp.empty:
        g = temp.groupby(["品項編號", "品項名稱"])
        out = g.apply(
            lambda x: (x["單價"] * x["數量"]).sum() / x["數量"].sum()
            if x["數量"].sum() > 0 else 0
        ).reset_index(name="平均進貨成本")

        out["平均進貨成本"] = (
            pd.to_numeric(out["平均進貨成本"], errors="coerce")
            .fillna(0)
            .round(0)
            .astype(int)
        )

        result = out.to_dict("records")

    years = sorted(df["年度"].dropna().unique())

    return render_template_string(
        HTML,
        data=result,
        years=years,
        year=year,
        start=start,
        end=end
    )

# =============================
# 啟動
# =============================
if __name__ == "__main__":
    print("📱 手機查價啟動中…")
    print("👉 同一個 Wi-Fi 手機瀏覽：")
    print("👉 http://你的電腦IP:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
