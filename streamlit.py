import streamlit as st
import backtrader as bt
import yfinance as yf
import pandas as pd
import inspect
import strategies
import matplotlib.pyplot as plt
import os

PLOT_DIR = 'backtest_results'

def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data_feed = bt.feeds.PandasData(dataname=data)
    return data_feed

def run_backtest(strategy_class, data_feed):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy_class)
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    result = cerebro.run()
    sqn = result[0].analyzers.sqn.get_analysis().sqn
    final_value = cerebro.broker.getvalue()
    trade_analysis = result[0].analyzers.trades.get_analysis()
    num_trades = trade_analysis.total.closed if 'total' in trade_analysis and 'closed' in trade_analysis.total else 0

    st.write(f"SQN: {sqn:.2f}")
    st.write(f"Final Portfolio Value: ${final_value:.2f}")
    st.write(f"Number of Trades: {num_trades}")

    # グラフの表示
    # プロットを保存
    cerebro.plot(figsize=(12, 8))
    plot_path = os.path.join(PLOT_DIR, 'backtest_plot.png')
    plt.savefig(plot_path)
    
    # 画像を表示
    st.image(plot_path, caption='Backtest Results', use_column_width=True)

# BaseStrategyを継承しているクラスを動的に取得する
def get_strategy_classes(module):
    strategy_classes = {}
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, strategies.BaseStrategy) and obj is not strategies.BaseStrategy:
            strategy_classes[name] = obj
    return strategy_classes

st.title('Backtrader Strategy Backtest')

# strategiesモジュール内の戦略クラスを取得
strategy_classes = get_strategy_classes(strategies)

# 戦略を選択するセレクトボックス
strategy_name = st.selectbox('Select Strategy', list(strategy_classes.keys()))

ticker = st.text_input('Ticker', 'VTI')
start_date = st.date_input('Start Date', value=pd.to_datetime('2018-01-01'))
end_date = st.date_input('End Date', value=pd.to_datetime('2023-01-01'))

if st.button('Run Backtest'):
    data_feed = fetch_data(ticker, start_date, end_date)
    selected_strategy = strategy_classes[strategy_name]
    run_backtest(selected_strategy, data_feed)
