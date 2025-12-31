import sys
import io
import yfinance as yf
import pandas as pd
from datetime import datetime

# 解決環境編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

STOCK_ID = "6148.TWO"
ZONES = {
    'sup_low': 24.0,
    'sup_high': 24.6,
    'res_low': 26.5,
    'res_high': 28.0
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
            <div class="footer">更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    # 1. 抓取資料
    df = yf.download(STOCK_ID, period="5d", interval="60m", progress=False)
    
    if df.empty:
        print("抓不到資料")
        return

    # 2. 【暴力提取】無視所有欄位結構，直接強制轉換
    try:
        # 先把所有的資料轉成最原始的 numpy 陣列，再轉成清單
        # 我們只鎖定 'Close' 欄位，不論它在哪一層
        raw_prices = df.loc[:, df.columns.get_level_values(0) == 'Close'].values.flatten().tolist()
        
        # 移除空值並確保是純 float 數字
        clean_prices = [float(p) for p in raw_prices if str(p) != 'nan']
        
        if len(clean_prices) < 3:
            print(f"資料不足：只有 {len(clean_prices)} 筆有效價格")
            return
            
        # 到這一步，current_p 絕對、百分之百只是個「數字」，不再是 Series
        current_p = clean_prices[-1]
        last_1h = clean_prices[-2]
        prev_1h = clean_prices[-3]
        
        print(f"DEBUG - 當前價格: {current_p}, 類型: {type(current_p)}")
        
    except Exception as e:
        print(f"解析崩潰: {e}")
        return

    # 3. 判斷邏輯
    # 這次絕對不會在下面這一行報 ValueError，因為 current_p 已經是純 float
    if current_p < ZONES['sup_low']:
        generate_html("⚠️ 破位", f"跌破支撐 {ZONES['sup_low']}", current_p, "red")
    elif prev_1h > ZONES['sup_high'] and last_1h > ZONES['sup_high']:
        if current_p < ZONES['res_high']:
            generate_html("✅ 站穩", f"守住轉折 {ZONES['sup_high']}", current_p, "green")
        else:
            generate_html("🚀 突破", f"衝過壓力 {ZONES['res_high']}", current_p, "blue")
    else:
        generate_html("🔎 觀察", "區間震盪中", current_p, "orange")

if __name__ == "__main__":
    main()
