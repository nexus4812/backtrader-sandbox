import backtrader as bt
import numpy as np
import yfinance as yf

import backtrader as bt

class SuperTrend(bt.Indicator):

    params = (
        ('period',10),
        ('multiplier',3)
        )
    lines = ('basic_ub','basic_lb','final_ub','final_lb')

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(period=self.p.period)
        self.l.basic_ub = ((self.data.high + self.data.low) / 2) + (self.atr * self.p.multiplier)
        self.l.basic_lb = ((self.data.high + self.data.low) / 2) - (self.atr * self.p.multiplier)

    def next(self):
        if len(self)-1 == self.p.period:
            self.l.final_ub[0] = self.l.basic_ub[0]
            self.l.final_lb[0] = self.l.basic_lb[0]
            return

        #=IF(OR(basic_ub<final_ub*,close*>final_ub*),basic_ub,final_ub*)
        if self.l.basic_ub[0] < self.l.final_ub[-1] or self.data.close[-1] > self.l.final_ub[-1]:
            self.l.final_ub[0] = self.l.basic_ub[0]
        else:
            self.l.final_ub[0] = self.l.final_ub[-1]

        #=IF(OR(baisc_lb > final_lb *, close * < final_lb *), basic_lb *, final_lb *)
        if self.l.basic_lb[0] > self.l.final_lb[-1] or self.data.close[-1] < self.l.final_lb[-1]:
            self.l.final_lb[0] = self.l.basic_lb[0]
        else:
            self.l.final_lb[0] = self.l.final_lb[-1]


class CCI_SuperTrendStrategy(bt.Strategy):
    params = (
        ('cci_period', 14),
        ('cci_threshold', 100),
        ('st_period', 10),
        ('st_multiplier', 3.0),
    )

    def __init__(self):
        self.cci = bt.indicators.CCI(self.data, period=self.params.cci_period)
        self.supertrend = SuperTrend(self.data, period=self.params.st_period, multiplier=self.params.st_multiplier)
        self.supertrend.plotinfo.subplot = False
        self.supertrend.plotinfo.plotlinelabels = True

    # def next(self):
    #     if not self.position:  # ポジションがない場合
    #         if self.supertrend.lines.direction[0] == 1 and self.cci[0] > -self.params.cci_threshold:
    #             # SuperTrendが上昇トレンドを示し、CCIが-100を上回る場合、買いエントリー
    #             self.buy()

    #     elif self.position:  # ポジションがある場合
    #         if self.supertrend.lines.direction[0] == -1 or self.cci[0] < -self.params.cci_threshold:
    #             # SuperTrendが下降トレンドを示すか、CCIが-100を下回る場合、売りエグジット
    #             self.sell()


if __name__ == '__main__':
    data = yf.download('VTI', start='2018-01-01', end='2024-03-01')
    data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

    # backtraderにデータを渡す
    data_feed = bt.feeds.PandasData(dataname=data)

    # Cerebroエンジンのセットアップ
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(CCI_SuperTrendStrategy)
    cerebro.broker.setcash(10000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # バックテストの実行
    cerebro.run()

    # グラフの表示
    fig = cerebro.plot(style='candlestick')[0][0]
    fig.savefig('backtest_result.png')

