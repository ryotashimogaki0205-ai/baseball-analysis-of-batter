FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# システム依存ライブラリのインストール（必要に応じて調整）
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && pip install --upgrade pip setuptools wheel \
    && rm -rf /var/lib/apt/lists/*

# 依存関係を先にコピーしてキャッシュを活かす
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# アプリケーションをコピー
COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
