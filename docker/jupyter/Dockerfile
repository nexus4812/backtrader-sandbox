FROM python:3.9-buster

WORKDIR /app

# Node.jsのバージョンを指定
ARG NODE_VERSION=22

# 必要なパッケージをインストールし、Node.jsをインストール
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_$NODE_VERSION.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \    
    backtrader \
    matplotlib \
    pandas \
    yfinance

# 検証後マージする
RUN pip install --no-cache-dir \    
    jupyterlab \
    ipywidgets \
    ipympl

COPY . .

CMD ["jupyter-lab", "--ip", "0.0.0.0", "--allow-root", "-b", "localhost", "--NotebookApp.token=''"]