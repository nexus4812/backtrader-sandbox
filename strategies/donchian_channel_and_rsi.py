from .base_strategy import BaseStrategy
import backtrader as bt

class DonchianChannelRSIStrategy(BaseStrategy):
    params = (
        ('profit_period', 180),
        ('upper_period', 120),
        ('lower_period', 60),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
    )

    def __init__(self):
        super().__init__(self.params)
        self.dataclose = self.datas[0].close
        self.profit_band = bt.indicators.Highest(self.data.high(-1), period=self.params.profit_period)
        self.upper_band = bt.indicators.Highest(self.data.high(-1), period=self.params.upper_period)
        self.lower_band = bt.indicators.Lowest(self.data.low(-1), period=self.params.lower_period)
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.upper_band[0] and self.rsi[0] < self.params.rsi_overbought:
                self.buy()
        else:
            if self.dataclose[0] < self.lower_band[0] or self.rsi[0] > self.params.rsi_overbought:
                self.sell()

    @staticmethod
    def get_optimization_params():
        return {
            'upper_period': range(100, 140, 10),
            'lower_period': range(50, 70, 10),
            'rsi_period': range(7, 14, 7),
            'rsi_overbought': range(65, 75, 5),
        }
