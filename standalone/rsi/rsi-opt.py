import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import os

class RSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('stop_loss', 0.05),  # 5% stop loss
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.buy_price = None
        self.trade_count = 0

    def next(self):
        if not self.position:
            if self.rsi < self.params.rsi_lower:
                self.buy_price = self.data.close[0]
                self.buy()
                self.trade_count += 1
        else:
            if self.rsi > self.params.rsi_upper:
                self.sell()
            elif self.data.close[0] < self.buy_price * (1 - self.params.stop_loss):
                self.sell()

def optimize_strategy(data, cash=10000.0, commission=0.001):
    cerebro = bt.Cerebro(optreturn=False)
    cerebro.adddata(data)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)

    cerebro.optstrategy(
        RSIStrategy,
        rsi_period=range(10, 20, 2),
        rsi_upper=range(65, 75, 5),
        rsi_lower=range(25, 35, 5),
        stop_loss=np.arange(0.01, 0.1, 0.01)
    )

    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    optimized_runs = cerebro.run()

    return optimized_runs

def extract_best_strategy(optimized_runs, min_trades=10):
    best_sqn = -float('inf')
    best_strategy = None

    for run in optimized_runs:
        for strategy in run:
            sqn = strategy.analyzers.sqn.get_analysis().sqn
            trade_count = strategy.trade_count
            if trade_count >= min_trades:
                print(f"RSI Period: {strategy.params.rsi_period}, RSI Upper: {strategy.params.rsi_upper}, RSI Lower: {strategy.params.rsi_lower}, Stop Loss: {strategy.params.stop_loss}, SQN: {sqn}, Trade Count: {trade_count}")
                if sqn > best_sqn:
                    best_sqn = sqn
                    best_strategy = strategy

    return best_strategy, best_sqn

# Yahoo Financeからデータを取得
data = yf.download('AAPL', start='2018-01-01', end='2023-01-01')
data_feed = bt.feeds.PandasData(dataname=data)

# 最適化の実行
optimized_runs = optimize_strategy(data_feed)

# 最適化結果から最高のSQNを持つ戦略を抽出
best_strategy, best_sqn = extract_best_strategy(optimized_runs)

# 結果の表示
print(f"Best SQN: {best_sqn}")
print(f"Best Strategy Parameters: RSI Period: {best_strategy.params.rsi_period}, RSI Upper: {best_strategy.params.rsi_upper}, RSI Lower: {best_strategy.params.rsi_lower}, Stop Loss: {best_strategy.params.stop_loss}")

# 結果を保存するディレクトリの作成
os.makedirs('backtest_results/strategy/rsi_opt', exist_ok=True)

# 最適化結果をプロット
cerebro = bt.Cerebro()
cerebro.adddata(data_feed)
cerebro.addstrategy(RSIStrategy, 
                    rsi_period=best_strategy.params.rsi_period, 
                    rsi_upper=best_strategy.params.rsi_upper, 
                    rsi_lower=best_strategy.params.rsi_lower, 
                    stop_loss=best_strategy.params.stop_loss)
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)

cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
cerebro.run()

fig = cerebro.plot(style='candlestick', dpi=100)[0][0]
fig.savefig('backtest_results/strategy/rsi_opt/best_strategy.png')
plt.close(fig)
