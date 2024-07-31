from .base_strategy import BaseStrategy
import backtrader as bt
import numpy as np

class RSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_low', 30),
        ('take_profit', 0.05),  # 利益確定条件（5％上昇）
        ('stop_loss', 0.05),    # 損切り条件（5％下落）
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)
        self.dataclose = self.datas[0].close
        self.buy_price = None

    def next(self):
        if not self.position:  # 現在ポジションがない場合
            if self.rsi < self.params.rsi_low:  # RSIが低レベルを下回った場合
                self.buy()
                self.buy_price = self.dataclose[0]
        else:
            if self.dataclose[0] >= self.buy_price * (1 + self.params.take_profit):  # 利益確定条件
                self.sell()
            elif self.dataclose[0] <= self.buy_price * (1 - self.params.stop_loss):  # 損切り条件
                self.sell()


    @staticmethod
    def get_optimization_params():
        return {
            'rsi_period': range(7, 49, 7),
            'rsi_low': range(10, 50, 5),
            'take_profit': np.arange(0.03, 0.10, 0.01),
            'stop_loss': np.arange(0.03, 0.10, 0.01),
        }
