import pandas as pd
import re
from datetime import datetime

# 讀取原始輸入
df_raw = pd.read_excel("進貨明細.xlsx", sheet_name="raw", header=None)
df_raw.columns = ["raw"]

records = []

for text in df_raw["raw"].dropna():
    parts = text.split()

    # 判斷第一欄是不是日期
    if re.match(r"\d{4}/\d{2}/\d{2}", parts[0]):
        日期 = pd.to_datetime(parts[0])
        offset = 1
    else:
        日期 = pd.NaT
        offset = 0

    品項編號 = parts[offset]

    # 單價、金額一定在最後
    單價 = float(parts[-2])
    金額 = float(parts[-1])

    middle = parts[offset + 1:-2]

    # 找「數量+單位」例如 10箱 / 4件 / 2包
    qty_idx = next(
        i for i, p in enumerate(middle)
        if re.match(r"\d+[\u4e00-\u9fff]+", p)
    )

    品項名稱 = "".join(middle[:qty_idx])
    數量 = int(re.search(r"\d+", middle[qty_idx]).group())
    單位 = re.search(r"[\u4e00-\u9fff]+", middle[qty_idx]).group()

    records.append([
        日期,
        品項編號,
        品項名稱,
        數量,
        單位,
        單價,
        金額
    ])

# 結構化資料
df = pd.DataFrame(records, columns=[
    "日期", "品項編號", "品項名稱", "數量", "單位", "單價", "金額"
])

# ===== 價格分析 =====
this_year = datetime.now().year

latest = (
    df.dropna(subset=["日期"])
      .sort_values("日期")
      .groupby("品項編號")
      .last()
      .reset_index()
)[["品項編號", "品項名稱", "單價", "日期"]]

latest.columns = ["品項編號", "品項名稱", "最新進價", "最新進貨日"]

avg = (
    df[df["日期"].dt.year == this_year]
      .groupby(["品項編號", "品項名稱"])["單價"]
      .mean()
      .reset_index()
)

avg.columns = ["品項編號", "品項名稱", "今年平均進價"]

# 輸出
with pd.ExcelWriter("價格整理.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="整理後明細", index=False)
    latest.to_excel(writer, sheet_name="最新進價", index=False)
    avg.to_excel(writer, sheet_name="今年平均", index=False)

print("✅ 金紙進貨資料整理完成（支援箱/件/包）")
