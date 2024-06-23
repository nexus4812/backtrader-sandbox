import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    return stock.info

# 例: S&P 500銘柄リストを取得
sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

# スクリーニング条件
criteria = {
    'marketCap': 1e10,   # 時価総額が100億ドル以上
    'trailingPE': (0, 20),  # PERが20以下
    'returnOnEquity': 0.15  # ROEが15%以上
}

# スクリーニング実行
screened_stocks = []
for ticker in sp500_tickers:
    try:
        data = get_stock_data(ticker)
        if (data['marketCap'] > criteria['marketCap'] and
            criteria['trailingPE'][0] < data['trailingPE'] < criteria['trailingPE'][1] and
            data['returnOnEquity'] > criteria['returnOnEquity']):
            screened_stocks.append(ticker)
    except KeyError:
        pass

print(f"Screened stocks: {screened_stocks}")

# ['AFL', 'ALLE', 'AXP', 'AMP', 'APA', 'APTV', 'ACGL', 'BBY', 'BLK', 'BLDR', 'BG', 'CPB', 'CAT', 'CE', 'CF', 'CHTR', 'CB', 'CINF', 'CSCO', 'CTSH', 'CMCSA', 'COP', 'CSX', 'DRI', 'DVA', 'DE', 'DAL', 'DVN', 'FANG', 'DFS', 'DG', 'DOV', 'DHI', 'EMN', 'EBAY', 'ETR', 'EOG', 'EG', 'XOM', 'FDX', 'GIS', 'GPC', 'GDDY', 'HAL', 'HIG', 'HCA', 'HSY', 'IBM', 'INCY', 'IPG', 'JBL', 'JPM', 'KR', 'LW', 'LEN', 'LMT', 'LYB', 'MPC', 'MLM', 'MAS', 'MGM', 'MOH', 'NRG', 'NUE', 'NVR', 'OMC', 'ON', 'OKE', 'PCAR', 'PYPL', 'PSX', 'PHM', 'RL', 'RJF', 'RCL', 'SLB', 'SPG', 'SNA', 'STLD', 'SYF', 'SYY', 'TROW', 'TGT', 'TEL', 'ULTA', 'UAL', 'UPS', 'URI', 'VLO', 'WRB', 'WMB']

