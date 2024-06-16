import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class DonchianChannelStrategy(bt.Strategy):
    params = (
        ('upper_period', 120),
        ('lower_period', 60),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close

        # Donchian Channelの上限と下限を計算
        self.upper_band = bt.indicators.Highest(self.data.high(-1), period=self.params.upper_period)
        self.lower_band = bt.indicators.Lowest(self.data.low(-1), period=self.params.lower_period)

    def next(self):
        if not self.position:  # 現在ポジションがない場合
            if self.dataclose[0] > self.upper_band[0]:  # 終値が上限バンドを超えた場合
                self.buy()
        else:
            if self.dataclose[0] < self.lower_band[0]:  # 終値が下限バンドを下回った場合
                self.sell()

# Yahoo Financeからデータを取得
data = yf.download('AAPL', start='2020-01-01', end='2023-01-01')

# backtraderに渡すためにDataFrameのカラムをリネーム
data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# backtraderにデータを渡す
data_feed = bt.feeds.PandasData(dataname=data)


# Cerebroエンジンのセットアップ
cerebro = bt.Cerebro()
cerebro.addstrategy(DonchianChannelStrategy)
cerebro.adddata(data_feed)
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)

# 初期ポートフォリオの価値
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 戦略の実行
cerebro.run()

# 最終ポートフォリオの価値
print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 結果のプロット
plt.figure(figsize=(1000, 1000), dpi=1000)
cerebro.plot()

fig = cerebro.plot(width=600, height=1200)[0][0]
fig.savefig('backtest_result.png')