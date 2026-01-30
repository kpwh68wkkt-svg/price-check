from flask import Flask, request
import pandas as pd
import os
import traceback

app = Flask(__name__)

# ========= 設定 =========
EXCEL_FILE = "價格整理.xlsx"
SHEET_NAME = "最新進價"   # 只查這個，不動你其他 Sheet

# ========= HTML =========
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>手機查價</title>
<style>
body { font-family: Arial; background:#f6f6f6; padding:20px; }
input, button { width:100%; padding:10px; font-size:16px; margin-top:10px; }
.card { background:white; padding:15px; border-radius:10px; margin-top:15px; }
.err { color:red; white-space:pre-wrap; }
</style>
</head>
<body>

<h2>📱 金紙手機查價</h2>

<form method="get">
  <input name="q" placeholder="輸入品項編號或名稱" value="{{q}}">
  <button type="submit">查詢</button>
</form>

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

</body>
</html>
"""

# ========= 主頁 =========
@app.route("/")
def index():
    q = request.args.get("q", "").strip()

    try:
        # 1️⃣ 檢查檔案
        if not os.path.exists(EXCEL_FILE):
            raise FileNotFoundError(f"找不到檔案：{EXCEL_FILE}")

        # 2️⃣ 讀 Excel
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

        # 3️⃣ 必要欄位檢查
        need_cols = {"品項編號", "品項名稱", "最新進價"}
        if not need_cols.issubset(df.columns):
            raise ValueError(f"缺少欄位，目前欄位：{list(df.columns)}")

        # 4️⃣ 查詢
        if q:
            df = df[
                df["品項編號"].astype(str).str.contains(q, na=False) |
                df["品項名稱"].astype(str).str.contains(q, na=False)
            ]

        rows = df.fillna("").to_dict("records")

        return app.jinja_env.from_string(HTML).render(
            q=q, rows=rows, error=""
        )

    except Exception as e:
        # ❗關鍵：錯誤直接顯示在手機
        return app.jinja_env.from_string(HTML).render(
            q=q,
            rows=[],
            error=str(e) + "\n\n" + traceback.format_exc()
        )

# ========= 啟動 =========
if __name__ == "__main__":
    print("📱 手機查價啟動中…")
    print("👉 同 Wi-Fi 手機瀏覽：http://電腦IP:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
