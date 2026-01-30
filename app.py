from flask import Flask, request, render_template_string
import pandas as pd

app = Flask(__name__)

FILE = "價格整理.xlsx"
SHEET = "平均進貨成本"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>📱 金紙手機查價</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial; background:#f5f5f5; padding:15px; }
input { width:100%; padding:12px; font-size:18px; }
button { width:100%; padding:12px; font-size:18px; margin-top:8px; }
.card {
  background:white; padding:12px; margin-top:10px;
  border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);
}
.price { color:#d32f2f; font-size:20px; }
</style>
</head>
<body>

<h2>📱 金紙查價</h2>

<form method="get">
  <input name="q" placeholder="輸入品項關鍵字（例：錢、庫錢）" value="{{ q }}">
  <button type="submit">查詢</button>
</form>

{% if error %}
<p style="color:red;">❌ {{ error }}</p>
{% endif %}

{% for r in results %}
<div class="card">
  <b>{{ r["品項名稱"] }}</b><br>
  平均進貨成本：
  <span class="price">${{ r["平均進貨成本"] }}</span>
</div>
{% endfor %}

{% if q and not results %}
<p>🔍 查無資料</p>
{% endif %}

</body>
</html>
"""

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    results = []
    error = None

    try:
        df = pd.read_excel(FILE, sheet_name=SHEET)

        if q:
            mask = df["品項名稱"].astype(str).str.contains(q, case=False, na=False)
            results = df[mask].to_dict("records")

    except Exception as e:
        error = str(e)

    return render_template_string(HTML, q=q, results=results, error=error)

if __name__ == "__main__":
    print("📱 手機查價啟動中…")
    print("👉 同 Wi-Fi 手機瀏覽：http://電腦IP:5000")
    app.run(host="0.0.0.0", port=5000)
