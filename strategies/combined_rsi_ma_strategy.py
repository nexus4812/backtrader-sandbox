from .base_strategy import BaseStrategy
import backtrader as bt

class CombinedRSIMAStrategy(BaseStrategy):
    params = (
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('short_ma_period', 50),
        ('long_ma_period', 200),
    )

    def __init__(self):
        super().__init__(self.params)

        # RSI インジケータ
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

        # 移動平均線 インジケータ
        self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_ma_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_ma_period)

    def next(self):
        if not self.position:  # 現在ポジションがない場合
            if self.rsi < self.params.rsi_lower and self.short_ma > self.long_ma:
                self.buy()
        else:
            if self.rsi > self.params.rsi_upper and self.short_ma < self.long_ma:
                self.sell()

    @staticmethod
    def get_optimization_params():
        return {
            'rsi_period': range(10, 20, 2),
            'rsi_upper': range(60, 80, 5),
            'rsi_lower': range(20, 40, 5),
            'short_ma_period': range(40, 60, 5),
            'long_ma_period': range(180, 220, 10),
        }
