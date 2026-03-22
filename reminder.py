import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from database_manager import MarketDB  # 導入資料庫工具盒

# ==========================================
# 參數設定
# ==========================================
MARGIN_MAINTENANCE_RATIO = 172.02  # 融資維持率 (手動輸入)
LOOKBACK_DAYS = '6mo' 

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

import requests  # 防止被認成機器人
def get_market_data():
    print(f"🚀 正在嘗試用 curl_cffi 抓取數據...")
    tickers = ['^VIX', '^VIX3M', '^TNX', '^FVX', 'NQ=F', '^TWII']
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    try:

        # 直接下載，yfinance 會自動偵測環境中的 curl_cffi 並進行偽裝
        data = yf.download(
            tickers, 
            period=LOOKBACK_DAYS, 
            progress=False, 
            auto_adjust=True
        )
        

        data = yf.download(tickers, period=LOOKBACK_DAYS, progress=False, auto_adjust=True, session=session) #session防止被認成機器人

        if data.empty:
            print("❌ 錯誤：下載數據為空。")
            return None
            
        # 處理資料格式 (保持原本的 Close 處理邏輯)
        if isinstance(data.columns, pd.MultiIndex):
            try:
                data = data['Close']
            except KeyError:
                data = data.xs('Close', level=0, axis=1)

        data = data.ffill()
        return data
    except Exception as e:
        print(f"❌ 抓取數據發生異常: {e}")
        return None

def analyze_market(data, margin_ratio):
    if data is None or data.empty:
        print("⚠️ 無法進行分析，因為沒有數據。")
        return

    try:
        # --- 1. 計算指標 ---
        latest = data.iloc[-1]
        
        # VIX 期限結構
        vix_ratio = latest['^VIX'] / latest['^VIX3M'] if '^VIX3M' in latest and latest['^VIX3M'] != 0 else 0
        
        # 殖利率曲線
        yield_spread = latest['^TNX'] - latest['^FVX'] if '^TNX' in latest else 0
        
        # 期貨 RSI
        nq_rsi = calculate_rsi(data['NQ=F']).iloc[-1] if 'NQ=F' in data else 0

        # 台股均線與乖離率
        twii_series = data['^TWII']
        price_tw = twii_series.iloc[-1]
        ma5_series = twii_series.rolling(window=5).mean()
        ma5_today = ma5_series.iloc[-1]
        ma5_yesterday = ma5_series.iloc[-2]
        
        ma60 = twii_series.rolling(window=60).mean().iloc[-1]
        bias_60 = ((price_tw - ma60) / ma60) * 100 

        # 均線型態判斷
        is_above_ma5 = price_tw > ma5_today
        ma_slope = ma5_today - ma5_yesterday
        trend_msg = "↗️ 上揚" if ma_slope > 0 else "↘️ 下彎" if ma_slope < 0 else "➡️ 走平"
        ma_status = "🟢 站上 (多)" if is_above_ma5 else "🔴 跌破 (空)"

        # --- 2. 輸出報告 ---
        print("\n" + "="*48)
        print(f"📊 量化恐慌儀表板 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*48)
        
        vix_tag = "🔴 恐慌" if vix_ratio > 1.1 else "🟢 正常"
        print(f"1. VIX 期限結構 : {vix_ratio:.2f}  ({vix_tag})")
        print(f"2. 債券利差     : {yield_spread:.2f}% (10Y-5Y)")
        print(f"3. 期貨 RSI     : {nq_rsi:.2f}")
        print(f"4. 融資維持率   : {margin_ratio}%")
        print(f"5. 季線乖離率   : {bias_60:.2f}%")
        print(f"6. 5日均線判斷  : {price_tw:.0f} ({ma_status} | 趨勢: {trend_msg})")
        print("-" * 48)
        
        # --- 3. 判斷建議 ---
        suggestion = ""
        reason = ""
        
        if margin_ratio < 130 and bias_60 < -5:
            suggestion = "🚀 強力建議：分批進場"
            reason = "理由：散戶融資已斷頭且股價嚴重超跌。"
        elif vix_ratio > 1.1 or (130 <= margin_ratio < 140):
            suggestion = "🛡️ 建議：空手/觀望"
            reason = "理由：市場處於極度恐慌或追繳中，風險較大。"
        elif not is_above_ma5:
            suggestion = "✋ 建議：不進場"
            reason = "理由：短線趨勢偏空，等待站上5日線。"
        else:
            suggestion = "☕ 建議：按兵不動 / 續抱"
            reason = "理由：目前各項指標均在正常範圍。"

        print(suggestion)
        print(reason)
        print("="*48 + "\n")

        # --- 4. 儲存至資料庫 (核心整合) ---
        try:
            db = MarketDB()
            final_results = {
                "vix_ratio": float(vix_ratio),
                "yield_spread": float(yield_spread),
                "nq_rsi": float(nq_rsi),
                "margin_ratio": float(margin_ratio),
                "bias_60": float(bias_60),
                "decision": str(suggestion),
                "reason": str(reason)
            }
            db.save_analysis(final_results)
        except Exception as db_e:
            print(f"⚠️ 資料庫儲存失敗: {db_e}")

    except Exception as e:
        print(f"❌ 分析過程發生錯誤: {e}")

# 主程式執行入口
if __name__ == "__main__":
    df = get_market_data()
    analyze_market(df, MARGIN_MAINTENANCE_RATIO)
