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
    'res_low': 26.5,    # 壓力區底部
    'res_high': 28.0    # 波段結構點
}

def generate_html(status, detail, price, color):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>台股個股監控</title>
        <style>
            body {{ font-family: -apple-system, "Microsoft JhengHei", sans-serif; text-align: center; background-color: #f4f7f6; padding: 20px; }}
            .card {{ background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); display: inline-block; width: 320px; border-top: 10px solid {color}; }}
            .status {{ font-size: 38px; font-weight: bold; color: {color}; margin: 15px 0; }}
            .price {{ font-size: 24px; color: #333; font-weight: 500; }}
            .detail {{ background: #fff5f5; padding: 15px; border-radius: 10px; color: #444; line-height: 1.6; border: 1px solid #eee; }}
            .footer {{ color: #999; font-size: 11px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="margin-top:0;">{STOCK_ID} 監控看板</h2>
            <div class="price">現價: <span style="font-size:32px;">{price:.2f}</span></div>
            <div class="status">{status}</div>
            <div class="detail">{detail}</div>
            <div class="footer">最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    # 抓取 1H 資料
    df = yf.download(STOCK_ID, period="5d", interval="60m", progress=False)
    
    if df.empty or len(df) < 3:
        print("資料抓取失敗或資料不足")
        return

    # --- 關鍵修正處：使用 .item() 或 float() 確保取到的是單一數值 ---
    try:
        current_p = float(df['Close'].iloc[-1])
        last_1h = float(df['Close'].iloc[-2])
        prev_1h = float(df['Close'].iloc[-3])
    except Exception as e:
        print(f"數值轉換出錯: {e}")
        return

    # --- 交易邏輯 ---
    if current_p < ZONES['sup_low']:
        generate_html("⚠️ 破位警示", f"跌破關鍵支撐 {ZONES['sup_low']}，請注意風險。", current_p, "#e74c3c")
    elif prev_1h > ZONES['sup_high'] and last_1h > ZONES['sup_high']:
        if current_p < ZONES['res_high']:
            generate_html("✅ 結構站穩", f"成功守住 {ZONES['sup_high']}，目標上看 {ZONES['res_low']}。", current_p, "#27ae60")
        else:
            generate_html("🚀 波段突破", f"已衝破壓力 {ZONES['res_high']}，開啟新上漲空間！", current_p, "#2980b9")
    else:
        generate_html("🔎 觀察中", f"目前在區間震盪，等待 123 站穩訊號。", current_p, "#f39c12")

if __name__ == "__main__":
    main()
