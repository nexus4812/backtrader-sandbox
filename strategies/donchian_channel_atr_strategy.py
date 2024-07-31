from .base_strategy import BaseStrategy
import backtrader as bt

class DonchianChannelATRStrategy(BaseStrategy):
    params = (
        ('upper_period', 120),
        ('lower_period', 60),
        ('atr_period', 16),
        ('atr_multiplier', 2.5),
    )

    def __init__(self):
        super().__init__(self.params)
        self.dataclose = self.datas[0].close
        self.upper_band = bt.indicators.Highest(self.data.high(-1), period=self.params.upper_period)
        self.lower_band = bt.indicators.Lowest(self.data.low(-1), period=self.params.lower_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.atr_stop = None

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.upper_band[0]:
                self.buy()
                self.atr_stop = self.dataclose[0] - self.atr[0] * self.params.atr_multiplier
        else:
            if self.dataclose[0] < self.lower_band[0]:
                self.sell()
                return

            self.atr_stop = max(self.atr_stop, self.dataclose[0] - self.atr[0] * self.params.atr_multiplier)
            if self.dataclose[0] < self.atr_stop:
                self.sell()

    @staticmethod
    def get_optimization_params():
        return {
            'upper_period': range(100, 140, 10),
            'lower_period': range(50, 70, 10),
            'atr_period': range(10, 20, 2),
            'atr_multiplier': [1.5, 2.0, 2.5, 3.0, 3.5],
        }
