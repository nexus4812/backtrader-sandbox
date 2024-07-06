from .base_strategy import BaseStrategy
import backtrader as bt

class DonchianChannelStrategy(BaseStrategy):
    params = (
        ('upper_period', 120),
        ('lower_period', 60),
    )

    def __init__(self):
        super().__init__(self.params)
        self.dataclose = self.datas[0].close
        self.upper_band = bt.indicators.Highest(self.data.high(-1), period=self.params.upper_period)
        self.lower_band = bt.indicators.Lowest(self.data.low(-1), period=self.params.lower_period)

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.upper_band[0]:
                self.buy()
        else:
            if self.dataclose[0] < self.lower_band[0]:
                self.sell()

    @staticmethod
    def get_optimization_params():
        return {
            'upper_period': range(100, 140, 10),
            'lower_period': range(50, 70, 10)
        }
