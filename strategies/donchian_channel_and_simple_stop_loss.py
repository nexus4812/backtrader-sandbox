from .base_strategy import BaseStrategy
import backtrader as bt
import numpy as np

class DonchianChannelStrategyAndSimpleStopLoss(bt.Strategy):
    params = (
        ('upper_period', 120),
        ('lower_period', 60),
        ('stop_loss', 0.20),    # 固定パーセンテージの損切り幅（例：20%）
    )

    def __init__(self):
        self.dataclose = self.datas[0].close

        # Donchian Channelの上限と下限を計算
        self.upper_band = bt.indicators.Highest(self.data.high(-1), period=self.params.upper_period)
        self.upper_band.plotinfo.subplot = False
        self.upper_band.plotinfo.plotlinelabels = True

        self.lower_band = bt.indicators.Lowest(self.data.low(-1), period=self.params.lower_period)
        self.lower_band.plotinfo.subplot = False
        self.lower_band.plotinfo.plotlinelabels = True

        self.stop_price = None

    def next(self):
        if not self.position:  # 現在ポジションがない場合
            if self.dataclose[0] > self.upper_band[0]:  # 終値が上限バンドを超えた場合
                self.buy()
                # 損切り価格を設定（エントリー価格から固定パーセンテージ下）
                self.stop_price = self.dataclose[0] * (1 - self.params.stop_loss)
        else:
            if self.dataclose[0] < self.stop_price:  # 終値が損切り価格を下回った場合
                self.sell()  # 損切り
            
            if self.dataclose[0] < self.lower_band[0]:  # 終値が下限バンドを下回った場合
                self.sell()  # 利確  

    @staticmethod
    def get_optimization_params():
        return {
            'upper_period': range(100, 140, 10),
            'lower_period': range(50, 70, 10),
            'stop_loss': np.arange(0.01, 0.50, 0.01),
        }