import backtrader as bt
import yfinance as yf
import os
import itertools

from strategies.rsi_strategy import RSIStrategy
from strategies.donchian_channel_strategy import DonchianChannelStrategy

def run_backtest(strategy, params, ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data_feed = bt.feeds.PandasData(dataname=data)
    
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy, **params)
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    result = cerebro.run()
    sqn = result[0].analyzers.sqn.get_analysis().sqn
    final_value = cerebro.broker.getvalue()
    
    return sqn, final_value

if __name__ == '__main__':
    strategies = [RSIStrategy, DonchianChannelStrategy]
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    start_date = '2018-01-01'
    end_date = '2023-01-01'

    for strategy in strategies:
        optimization_params = strategy.get_optimization_params()
        param_combinations = list(itertools.product(*optimization_params.values()))
        for params in param_combinations:
            param_dict = dict(zip(optimization_params.keys(), params))
            for ticker in tickers:
                sqn, final_value = run_backtest(strategy, param_dict, ticker, start_date, end_date)
                print(f'Strategy: {strategy.__name__}, Ticker: {ticker}, Params: {param_dict}, SQN: {sqn}, Final Value: {final_value:.2f}')
