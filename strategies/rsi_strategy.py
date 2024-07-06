from .base_strategy import BaseStrategy
import backtrader as bt

class RSIStrategy(BaseStrategy):
    params = (
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('stop_loss', 0.05),  # 5% stop loss
    )

    def __init__(self):
        super().__init__(self.params)
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

    @staticmethod
    def get_optimization_params():
        return {
            'rsi_period': range(10, 20, 2),
            'rsi_upper': range(65, 75, 5),
            'rsi_lower': range(25, 35, 5),
            'stop_loss': [0.01, 0.02, 0.03, 0.04, 0.05]
        }
