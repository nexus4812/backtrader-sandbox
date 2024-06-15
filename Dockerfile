# Dockerfile
FROM python:3.9-buster

# 作業ディレクトリを作成
WORKDIR /app

# RUN apt-get update && apt-get install tk

# 必要なパッケージをインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# スクリプトをコピー
COPY . .

CMD ["python", "backtest.py"]

