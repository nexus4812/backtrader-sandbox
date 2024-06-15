import backtrader as bt
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class BreakoutStrategy(bt.Strategy):
    params = (('period', 20),)

    def __init__(self):
        self.highest = bt.indicators.Highest(self.data.high, period=self.params.period)
        self.lowest = bt.indicators.Lowest(self.data.low, period=self.params.period)

    def next(self):
        if not self.position:
            if self.data.close[0] > self.highest[-1]:
                self.buy()
        else:
            if self.data.close[0] < self.lowest[-1]:
                self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BreakoutStrategy)

    data = bt.feeds.PandasData(dataname=yf.download('AAPL', '2022-01-01', '2023-01-01'))

    cerebro.adddata(data)
    cerebro.broker.setcash(10000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # グラフをファイルに保存
    fig = cerebro.plot()[0][0]
    fig.savefig('backtest_result.png')
