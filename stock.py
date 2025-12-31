import sys
import io
import yfinance as yf
import pandas as pd
import json
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 請替換您的 ID ---
SHEET_ID = "您的_GOOGLE_SHEET_ID"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def main():
    # 1. 讀取 Google Sheets 策略
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        strategies = []
        for _, row in df_sheet.iterrows():
            ticker = str(row.iloc[0]).strip()
            # 抓取 Yahoo 報價
            stock = yf.download(ticker, period="1d", interval="1m", progress=False)
            curr_p = float(stock['Close'].iloc[-1]) if not stock.empty else 0
            
            # 判定狀態
            s_low, s_high, r_high = float(row.iloc[2]), float(row.iloc[3]), float(row.iloc[4])
            status = "🔎 觀察"
            if curr_p < s_low: status = "⚠️ 破位"
            elif curr_p > r_high: status = "🚀 突破"
            elif curr_p > s_high: status = "✅ 站穩"

            strategies.append({
                "ticker": ticker,
                "name": row.iloc[1],
                "price": round(curr_p, 2),
                "status": status,
                "note": str(row.iloc[5]),
                "s_low": s_low, "s_high": s_high, "r_high": r_high
            })
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. 產生含搜尋功能的 HTML
    json_data = json.dumps(strategies, ensure_ascii=False)
    
    html_template = f"""
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>個股策略搜尋</title>
    <style>
        body {{ font-family: sans-serif; background: #f4f7f6; padding: 20px; text-align: center; }}
        .search-box {{ padding: 15px; width: 80%; max-width: 400px; border-radius: 25px; border: 1px solid #ddd; font-size: 18px; margin-bottom: 20px; }}
        .result-card {{ background: white; padding: 25px; border-radius: 15px; display: none; margin: 0 auto; max-width: 400px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .status-tag {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
    </style></head>
    <body>
        <h2>🔍 智慧策略查詢</h2>
        <input type="text" id="searchInput" class="search-box" placeholder="輸入股票代號 (如 5498.TWO)..." oninput="searchStock()">
        
        <div id="resultCard" class="result-card">
            <h3 id="resName"></h3>
            <p id="resPrice" style="font-size: 20px;"></p>
            <div id="resStatus" class="status-tag"></div>
            <p id="resNote" style="background:#eee; padding:10px;"></p>
            <div style="text-align:left; font-size:14px; color:#666;">
                長線支撐: <span id="resSLow"></span><br>
                短線轉折: <span id="resSHigh"></span><br>
                壓力頂部: <span id="resRHigh"></span>
            </div>
        </div>

        <script>
            const data = {json_data};
            function searchStock() {{
                const input = document.getElementById('searchInput').value.toUpperCase();
                const card = document.getElementById('resultCard');
                const stock = data.find(s => s.ticker.includes(input));
                
                if (stock && input.length >= 2) {{
                    card.style.display = 'block';
                    document.getElementById('resName').innerText = stock.name + " (" + stock.ticker + ")";
                    document.getElementById('resPrice').innerText = "現價: " + stock.price;
                    document.getElementById('resStatus').innerText = stock.status;
                    document.getElementById('resStatus').style.color = stock.status === '🚀 突破' ? 'blue' : (stock.status === '✅ 站穩' ? 'green' : 'orange');
                    document.getElementById('resNote').innerText = "分析: " + stock.note;
                    document.getElementById('resSLow').innerText = stock.s_low;
                    document.getElementById('resSHigh').innerText = stock.s_high;
                    document.getElementById('resRHigh').innerText = stock.r_high;
                }} else {{
                    card.style.display = 'none';
                }}
            }}
        </script>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    main()
