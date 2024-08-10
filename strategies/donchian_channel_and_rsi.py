import backtrader as bt

class DonchianChannelRSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_oversold', 30),
        ('donchian_period', 20),
        ('atr_period', 14),  # ATRの期間
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

        self.donchian_low = bt.indicators.Lowest(self.data.low, period=self.params.donchian_period)
        self.donchian_low.plotinfo.subplot = False
        self.donchian_low.plotinfo.plotlinelabels = True

        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)

        self.entry_price = None  # To track the entry price

    def next(self):
        if not self.position:
            if self.rsi[0] < self.params.rsi_oversold:
                self.buy()
                self.entry_price = self.data.close[0]
        else:
            stop_price = max(self.donchian_low[0], self.entry_price - self.atr[0])
            if self.data.close[0] < stop_price:
                self.close()

    # @staticmethod
    # def get_optimization_params():
    #     return {
    #         'rsi_period': range(7, 21, 7),
    #         'rsi_oversold': range(10, 40, 10),
    #         'donchian_period': range(10, 120, 10),
    #         'atr_period': range(7, 21, 7),
    #     }

    @staticmethod
    def get_optimization_params():
        return {
            'rsi_period': [7],
            'rsi_oversold': [30],
            'donchian_period': [30],
            'atr_period': [7],
        }
