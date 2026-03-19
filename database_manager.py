import sqlite3
import logging
from datetime import datetime

# 配置 Logging：這會同時輸出到螢幕與檔案
# 設定日誌格式：時間 - 等級 - 訊息
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("market_monitor.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MarketDB:
    def __init__(self, db_path="market_data.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """初始化資料庫表結構"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_records (
                    date TEXT PRIMARY KEY,
                    vix_ratio REAL,
                    yield_spread REAL,
                    nq_rsi REAL,
                    margin_ratio REAL,
                    bias_60 REAL,
                    decision TEXT,
                    reason TEXT
                )
            ''')
            conn.commit()

    def record_exists(self, date_str):
        """檢查當天數據是否已存在，避免重複寫入"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM sentiment_records WHERE date = ?", (date_str,))
            return cursor.fetchone() is not None

    def save_analysis(self, results):
        """
        results: 傳入字典格式的數據
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                sql = '''
                    INSERT OR REPLACE INTO sentiment_records 
                    (date, vix_ratio, yield_spread, nq_rsi, margin_ratio, bias_60, decision, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(sql, (
                    date_str,
                    results['vix_ratio'],
                    results['yield_spread'],
                    results['nq_rsi'],
                    results['margin_ratio'],
                    results['bias_60'],
                    results['decision'],
                    results['reason']
                ))
                conn.commit()
            logging.info(f"📊 {date_str} 數據儲存成功")
        except Exception as e:
            logging.error(f"❌ 資料庫寫入失敗: {e}")

# --- 測試代碼 (只為了確認工具盒能不能用) ---
# if __name__ == "__main__":
#     # 1. 實例化：拿出一盒工具
#     db = MarketDB() 
    
#     # 2. 準備假數據
#     test_data = {
#         "vix_ratio": 0.95,
#         "yield_spread": 0.4,
#         "nq_rsi": 50,
#         "margin_ratio": 160,
#         "bias_60": 2.5,
#         "decision": "測試中",
#         "reason": "確認資料庫是否運作"
#     }
    
#     # 3. 按下按鈕：存檔
#     print("正在測試存檔功能...")
#     db.save_analysis(test_data)
#     print("存檔完成！請檢查 VS Code 左側清單是否出現了 market_data.db")