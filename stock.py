import sys
import io
import yfinance as yf
import pandas as pd
from datetime import datetime

# 解決環境編碼問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 核心參數輸入 (根據您的分析) ---
STOCK_ID = "6148.TWO"  # 建議改回 6148.TWO 以確保資料穩定
ZONES = {
    'sup_low': 24002,   # 大箱型多空轉折
    'sup_high': 24068,  # 短線多空轉折 [cite: 3]
    'res_low': 24100,   # 短線觀察點 [cite: 4]
    'res_high': 24150   # 新波段進攻點
}

def generate_html(status, detail, price, color):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>6148 策略儀表板</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; text-align: center; background-color: #f0f2f5; padding: 30px; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: inline-block; max-width: 90%; }}
            .status {{ font-size: 40px; font-weight: bold; color: {color}; margin: 15px 0; }}
            .price {{ font-size: 20px; color: #444; }}
            .detail {{ color: #666; font-size: 16px; background: #f9f9f9; padding: 10px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>{STOCK_ID} 監控看板</h1>
            <div class="price">最新價格: {price:.2f}</div>
            <div class="status">{status}</div>
            <div class="detail">{detail}</div>
            <hr style="border: 0.5px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #999;">最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
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
        print("資料不足")
        return

    current_p = df['Close'].iloc[-1]
    last_1h = df['Close'].iloc[-2]
    prev_1h = df['Close'].iloc[-3] # 補齊語法錯誤 

    # 1. 破位判定 [cite: 1]
    if current_p < ZONES['sup_low']:
        generate_html("⚠️ 破位警戒", f"價格 {current_p:.2f} 跌破轉折 {ZONES['sup_low']}", current_p, "#d93025")
    
    # 2. 站穩判定 [cite: 3]
    elif prev_1h > ZONES['sup_high'] and last_1h > ZONES['sup_high']:
        if current_p < ZONES['res_high']:
            generate_html("✅ 結構站穩", f"守住 {ZONES['sup_high']}，目標看 {ZONES['res_high']}", current_p, "#1e8e3e")
        else:
            generate_html("🚀 波段突破", f"已衝破 {ZONES['res_high']}", current_p, "#1a73e8")
    
    # 3. 區間震盪 [cite: 4]
    else:
        generate_html("🔎 監控中", "等待 123 訊號或方向選擇中", current_p, "#f9ab00")

if __name__ == "__main__":
    main()
