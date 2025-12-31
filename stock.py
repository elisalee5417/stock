import sys
import io
import yfinance as yf
import pandas as pd
from datetime import datetime

# 解決 Windows/GitHub 環境編碼問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 核心參數輸入 (根據您的分析) ---
# 台股期指代碼通常為 WTX&F (Yahoo Finance)，或您可以改回 6148.TWO
STOCK_ID = "WTX&F" 
ZONES = {
    'sup_low': 24002,   # 大箱型多空轉折 (守不住則偏空)
    'sup_high': 24068,  # 短線多空轉折 (站穩則多頭具備進攻資格)
    'res_low': 24100,   # 短線壓回觀察點
    'res_high': 24150   # 新波段進攻點
}

def generate_html(status, detail, price, color):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>交易策略儀表板</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; background-color: #f4f4f4; padding: 50px; }}
            .card {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }}
            .status {{ font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0; }}
            .price {{ font-size: 24px; color: #555; }}
            .detail {{ color: #666; font-size: 18px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>{STOCK_ID} 策略監控</h1>
            <div class="price">目前價位: {price:.2f}</div>
            <div class="status">{status}</div>
            <div class="detail">{detail}</div>
            <hr>
            <p>最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    # 抓取 1H 資料 [cite: 6]
    df = yf.download(STOCK_ID, period="5d", interval="60m", progress=False)
    if df.empty or len(df) < 8: return

    current_p = df['Close'].iloc[-1]
    last_1h = df['Close'].iloc[-2]
    prev_1h = df['Close'].iloc[-3] # 修正之前檔案缺失的賦值 [cite: 2]

    # 1. 破位判定 (24002)
    if current_p < ZONES['sup_low']:
        generate_html("⚠️ 破位警戒", f"跌破大箱型轉折 {ZONES['sup_low']}，結構轉弱！", current_p, "red")
    
    # 2. 站穩判定 (24068) [cite: 3]
    elif prev_1h > ZONES['sup_high'] and last_1h > ZONES['sup_high']:
        if current_p < ZONES['res_high']:
            generate_html("✅ 結構站穩", f"守住短線轉折 {ZONES['sup_high']}，具備進攻 24150 資格。", current_p, "green")
        else:
            generate_html("🚀 波段突破", f"已突破 {ZONES['res_high']}，進入新波段！", current_p, "blue")
    
    # 3. 區間震盪 [cite: 4]
    else:
        generate_html("🔎 觀察中", "目前在轉折區間內震盪，等待 123 站穩訊號。", current_p, "orange")

if __name__ == "__main__":
    main()
