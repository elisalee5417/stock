import sys
import io
import yfinance as yf
from datetime import datetime

# 強制設定編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_html(status, detail, price, color):
    html = f"""
    <html><body style="text-align:center;padding:50px;">
        <h1 style="color:{color};">{status}</h1>
        <p>目前價位: {price:.2f}</p>
        <p>{detail}</p>
        <small>更新於: {datetime.now().strftime('%H:%M:%S')}</small>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    # 抓取資料
    df = yf.download("6148.TWO", period="5d", interval="60m", progress=False)
    
    if df.empty:
        print("抓不到資料")
        return

    # 【核心修正】拋棄所有 Pandas 結構，只取最後一個收盤價轉為純數字
    try:
        # 直接轉換成 Python 的原生浮點數清單
        prices = df['Close'].values.flatten().tolist()
        # 移除 nan
        prices = [float(p) for p in prices if str(p) != 'nan']
        
        # 取得最後三個數字
        curr = prices[-1]
        last = prices[-2]
        prev = prices[-3]
        
        print(f"DEBUG: 抓到數值 {curr}, {last}, {prev}")
    except Exception as e:
        print(f"資料解析失敗: {e}")
        return

    # 設定位階數字
    S_LOW = 24.0
    S_HIGH = 24.6
    R_HIGH = 28.0

    # 執行比較
    if curr < S_LOW:
        generate_html("⚠️ 破位", f"跌破 {S_LOW}", curr, "red")
    elif prev > S_HIGH and last > S_HIGH:
        if curr < R_HIGH:
            generate_html("✅ 站穩", f"守住 {S_HIGH}", curr, "green")
        else:
            generate_html("🚀 突破", f"衝破 {R_HIGH}", curr, "blue")
    else:
        generate_html("🔎 觀察", "區間震盪中", curr, "orange")

if __name__ == "__main__":
    main()
