from flask import Flask, request
import pandas as pd
import os
import traceback

app = Flask(__name__)

EXCEL_FILE = "價格整理.xlsx"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>手機查價</title>
<style>
body { font-family: Arial; background:#f6f6f6; padding:20px; }
input, button { width:100%; padding:12px; font-size:18px; margin-top:10px; }
.card { background:white; padding:15px; border-radius:10px; margin-top:15px; }
.err { color:red; white-space:pre-wrap; }
small { color:#666; }
</style>
</head>
<body>

<h2>📱 金紙手機查價</h2>

<form method="get">
  <input name="q" placeholder="輸入關鍵字（例如：庫錢 / 壽 / 50）" value="{{q}}">
  <button type="submit">查詢</button>
</form>

{% if sheet %}
<small>📄 資料來源：{{ sheet }}</small>
{% endif %}

{% if error %}
<div class="card err">
❌ 發生錯誤：
{{ error }}
</div>
{% endif %}

{% for r in rows %}
<div class="card">
<b>{{ r["品項編號"] }}｜{{ r["品項名稱"] }}</b><br>
最新進價：<b style="color:green">${{ r["最新進價"] }}</b>
</div>
{% endfor %}

{% if q and not rows %}
<div class="card">
查無資料
</div>
{% endif %}

</body>
</html>
"""

@app.route("/")
def index():
    q = request.args.get("q", "").strip()

    try:
        if not os.path.exists(EXCEL_FILE):
            raise FileNotFoundError(f"找不到檔案：{EXCEL_FILE}")

        xls = pd.ExcelFile(EXCEL_FILE)

        df = None
        sheet_used = None

        # 🔍 自動找正確的 Sheet
        for s in xls.sheet_names:
            tmp = pd.read_excel(xls, sheet_name=s)
            if {"品項編號", "品項名稱", "最新進價"}.issubset(tmp.columns):
                df = tmp.copy()
                sheet_used = s
                break

        if df is None:
            raise ValueError("找不到包含『品項編號 / 品項名稱 / 最新進價』的工作表")

        # 🔧 強制轉型 + 清洗
        df["品項編號"] = df["品項編號"].astype(str).str.strip()
        df["品項名稱"] = df["品項名稱"].astype(str).str.strip()
        df["最新進價"] = df["最新進價"].astype(str).str.strip()

        # 🔍 模糊搜尋（最穩）
        if q:
            key = q.lower()
            df = df[
                df["品項編號"].str.lower().str.contains(key, regex=False) |
                df["品項名稱"].str.lower().str.contains(key, regex=False)
            ]

        rows = df.to_dict("records")

        return app.jinja_env.from_string(HTML).render(
            q=q,
            rows=rows,
            sheet=sheet_used,
            error=""
        )

    except Exception as e:
        return app.jinja_env.from_string(HTML).render(
            q=q,
            rows=[],
            sheet="",
            error=str(e) + "\n\n" + traceback.format_exc()
        )

if __name__ == "__main__":
    print("📱 手機查價啟動中…")
    print("👉 同 Wi-Fi 手機瀏覽：http://電腦IP:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
