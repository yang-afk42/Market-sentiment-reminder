# 1. 使用輕量級 Python 基礎鏡像
FROM python:3.10-slim

# 2. 設定工作目錄
WORKDIR /app

# 3. 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 複製專案所有內容到容器
COPY reminder.py database_manager.py ./

# 5. 設定啟動指令
CMD ["python", "reminder.py"]
