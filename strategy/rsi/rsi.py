import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
import backtrader.analyzers as btanalyzers
import os

class RSIStrategy(bt.Strategy):
    params = (
        ('period', 14),
        ('rsi_lower', 30),
        ('rsi_upper', 70),
        ('stop_loss_pct', 0.02),  # 損切りを2%に設定
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.period)
        self.dataclose = self.datas[0].close
        self.order = None  # 現在のオーダーを記録
        self.buy_price = None  # エントリー価格

    def next(self):
        if self.order:  # 現在のオーダーがある場合は何もしない
            return

        if not self.position:  # ポジションがない場合
            if self.rsi < self.params.rsi_lower:
                self.order = self.buy()
                self.buy_price = self.dataclose[0]
        else:  # ポジションがある場合
            if self.rsi > self.params.rsi_upper:
                self.order = self.sell()
            elif self.dataclose[0] < self.buy_price * (1 - self.params.stop_loss_pct):  # 損切り条件
                self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.order = None

# Yahoo Financeからデータを取得
data = yf.download('AAPL', start='2018-01-01', end='2023-01-01')
data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# backtraderにデータを渡す
data_feed = bt.feeds.PandasData(dataname=data)

# Cerebroエンジンのセットアップ
cerebro = bt.Cerebro()
cerebro.adddata(data_feed)
cerebro.addstrategy(RSIStrategy)
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)
cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')

# 初期ポートフォリオの価値
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# バックテストを実行
thestrats = cerebro.run()
thestrat = thestrats[0]

print('SQN:', thestrat.analyzers.sqn.get_analysis())


# 最終ポートフォリオの価値
print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 結果をプロット
fig = cerebro.plot(style='candlestick')[0][0]
fig.savefig('backtest_result.png')
