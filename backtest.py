import backtrader as bt
import yfinance as yf
import os
import itertools
import multiprocessing
import matplotlib.pyplot as plt

from strategies.rsi_strategy import RSIStrategy
from strategies.donchian_channel_strategy import DonchianChannelStrategy
from strategies.donchian_channel_atr_strategy import DonchianChannelATRStrategy
from strategies.donchian_channel_and_simple_stop_loss import DonchianChannelStrategyAndSimpleStopLoss

def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data_feed = bt.feeds.PandasData(dataname=data)
    return data_feed

def run_backtest(args):
    strategy, params, data_feed, ticker = args
    cerebro = bt.Cerebro(maxcpus=1)  # 各プロセスに1コアを割り当て
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
        fig.suptitle(f'SQN: {sqn:.2f}', fontsize=16)
        fig.savefig(f'{path}/sqn_{sqn}.png')

    return strategy.__name__, ticker, params, sqn, final_value, num_trades

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    strategies = [DonchianChannelStrategyAndSimpleStopLoss]
    tickers = ['VTI']
    start_date = '2018-01-01'
    end_date = '2024-07-01'
    results = []

    # バックテストの引数リストを作成
    args_list = []
    for ticker in tickers:
        data_feed = fetch_data(ticker, start_date, end_date)
        for strategy in strategies:
            optimization_params = strategy.get_optimization_params()
            param_combinations = list(itertools.product(*optimization_params.values()))
            for params in param_combinations:
                param_dict = dict(zip(optimization_params.keys(), params))
                args_list.append((strategy, param_dict, data_feed, ticker))

    # マルチプロセッシングプールを使用して並列実行
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(run_backtest, args_list)

    # 結果をSQNの降順でソートして表示
    sorted_results = sorted(results, key=lambda x: x[3], reverse=True)
    for strategy_name, ticker, params, sqn, final_value, num_trades in sorted_results:
        print(f'Strategy: {strategy_name}, Ticker: {ticker}, Params: {params}, SQN: {sqn:.2f}, Final Value: {final_value:.2f}, Trades: {num_trades}')
