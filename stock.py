import sys
import io
import yfinance as yf
from datetime import datetime

# 解決編碼問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_html(status, detail, price, color):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head><meta charset="UTF-8"><title>監控看板</title></head>
    <body style="text-align:center; padding:50px; background:#f4f4f4; font-family:sans-serif;">
        <div style="background:white; display:inline-block; padding:30px; border-radius:20px; border-top:10px solid {color}; shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h1>6148.TWO 監控</h1>
            <p style="font-size:24px;">現價: {price:.2f}</p>
            <h2 style="color:{color};">{status}</h2>
            <p>{detail}</p>
            <hr><p style="font-size:12px; color:gray;">更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    # 1. 抓取資料，強制關閉 auto_adjust 減少干擾
    df = yf.download("6148.TWO", period="5d", interval="60m", progress=False, auto_adjust=True)
    
    if df.empty: return

    # 2. 【核心改動】直接從數值矩陣抓取最後三筆收盤價，完全不使用欄位名稱比較
    # 這樣可以徹底避開 Pandas 的 Series 比較錯誤
    try:
        # 抓取 Close 欄位的最後三個數字
        close_list = df['Close'].values.flatten().tolist()
        # 過濾掉空值
        clean_prices = [float(p) for p in close_list if str(p) != 'nan']
        
        c_p = clean_prices[-1]
        l_p = clean_prices[-2]
        p_p = clean_prices[-3]
    except:
        return

    # 3. 定義位階 (手動定義數字，避免從字典讀取可能發生的型別錯誤)
    S_LOW = 24.0
    S_HIGH = 24.6
    R_HIGH = 28.0

    # 4. 【暴力比較】強制將變數轉為 float 後再比較
    cur = float(c_p)
    last = float(l_p)
    prev = float(p_p)

    if cur < S_LOW:
        generate_html("⚠️ 破位", f"跌破 {S_LOW}", cur, "red")
    elif prev > S_HIGH and last > S_HIGH:
        if cur < R_HIGH:
            generate_html("✅ 站穩", f"守住 {S_HIGH}", cur, "green")
        else:
            generate_html("🚀 突破", f"衝過 {R_HIGH}", cur, "blue")
    else:
        generate_html("🔎 觀察", "區間震盪", cur, "orange")

if __name__ == "__main__":
    main()
