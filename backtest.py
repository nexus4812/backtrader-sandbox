import backtrader as bt
import yfinance as yf
import os
import itertools
import matplotlib.pyplot as plt

from strategies.rsi_strategy import RSIStrategy
from strategies.donchian_channel_strategy import DonchianChannelStrategy
from strategies.combined_rsi_ma_strategy import CombinedRSIMAStrategy

def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data_feed = bt.feeds.PandasData(dataname=data)
    return data_feed

def run_backtest(strategy, params, data_feed, ticker):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy, **params)
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    result = cerebro.run()
    sqn = result[0].analyzers.sqn.get_analysis().sqn
    final_value = cerebro.broker.getvalue()
    trade_analysis = result[0].analyzers.trades.get_analysis()
    num_trades = trade_analysis.total.closed if 'total' in trade_analysis and 'closed' in trade_analysis.total else 0

    if sqn > 1.5:
        path = f'backtest_results/{strategy.__name__}/{ticker}'
        os.makedirs(path, exist_ok=True)
        fig = cerebro.plot()[0][0]
        fig.savefig(f'{path}/sqn_{sqn}.png')

    return sqn, final_value, num_trades

if __name__ == '__main__':
    strategies = [CombinedRSIMAStrategy]
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    start_date = '2018-01-01'
    end_date = '2023-01-01'
    results = []

    for ticker in tickers:
        data_feed = fetch_data(ticker, start_date, end_date)
        for strategy in strategies:
            optimization_params = strategy.get_optimization_params()
            param_combinations = list(itertools.product(*optimization_params.values()))
            for params in param_combinations:
                param_dict = dict(zip(optimization_params.keys(), params))
                sqn, final_value, num_trades = run_backtest(strategy, param_dict, data_feed, ticker)
                results.append((strategy.__name__, ticker, param_dict, sqn, final_value, num_trades))

    # 結果をSQNの降順でソートして表示
    sorted_results = sorted(results, key=lambda x: x[3], reverse=True)
    for strategy_name, ticker, params, sqn, final_value, num_trades in sorted_results:
        print(f'Strategy: {strategy_name}, Ticker: {ticker}, Params: {params}, SQN: {sqn:.2f}, Final Value: {final_value:.2f}, Trades: {num_trades}')
