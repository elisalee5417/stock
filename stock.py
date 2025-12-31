import sys
import io
import yfinance as yf
import pandas as pd
from datetime import datetime

# 解決 GitHub 環境編碼問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 核心參數輸入 ---
STOCK_ID = "6148.TWO"  # 驊宏資
ZONES = {
    'sup_low': 24.0,    # 大箱型底
    'sup_high': 24.6,   # 短線轉折
    'res_low': 26.5,    # 壓力觀察
    'res_high': 28.0    # 波段進攻
}

def generate_html(status, detail, price, color):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>交易監控看板</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; background-color: #f4f7f6; padding: 20px; }}
            .card {{ background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); display: inline-block; width: 320px; border-top: 10px solid {color}; }}
            .status {{ font-size: 38px; font-weight: bold; color: {color}; margin: 15px 0; }}
            .price {{ font-size: 24px; color: #333; }}
            .footer {{ color: #999; font-size: 11px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>{STOCK_ID} 監控</h2>
            <div class="price">現價: {price:.2f}</div>
            <div class="status">{status}</div>
            <div style="background:#eee; padding:10px; border-radius:10px;">{detail}</div>
            <div class="footer">更新於: {datetime.now().strftime('%H:%M:%S')}</div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    # 抓取資料
    df = yf.download(STOCK_ID, period="5d", interval="60m", progress=False)
    
    if df.empty or len(df) < 3:
        print("資料抓取失敗")
        return

    # --- 關鍵修正：確保提取為純數字 (Scalar) ---
    try:
        # 使用 iloc 取值後再轉成 float，避免 Series 比較錯誤
        current_p = float(df['Close'].iloc[-1].item()) if hasattr(df['Close'].iloc[-1], 'item') else float(df['Close'].iloc[-1])
        last_1h = float(df['Close'].iloc[-2].item()) if hasattr(df['Close'].iloc[-2], 'item') else float(df['Close'].iloc[-2])
        prev_1h = float(df['Close'].iloc[-3].item()) if hasattr(df['Close'].iloc[-3], 'item') else float(df['Close'].iloc[-3])
    except Exception as e:
        print(f"解析數值錯誤: {e}")
        return

    # 判斷邏輯
    if current_p < ZONES['sup_low']:
        generate_html("⚠️ 破位", f"跌破 {ZONES['sup_low']}", current_p, "red")
    elif prev_1h > ZONES['sup_high'] and last_1h > ZONES['sup_high']:
        if current_p < ZONES['res_high']:
            generate_html("✅ 站穩", f"守住 {ZONES['sup_high']}", current_p, "green")
        else:
            generate_html("🚀 突破", f"衝過 {ZONES['res_high']}", current_p, "blue")
    else:
        generate_html("🔎 觀察", "區間盤整中", current_p, "orange")

if __name__ == "__main__":
    main()
