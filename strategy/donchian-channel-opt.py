import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
import os
import itertools
import backtrader.analyzers as btanalyzers

class DonchianChannelStrategy(bt.Strategy):
    params = (
        ('upper_period', 120),
        ('lower_period', 60),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close

        # Donchian Channelの上限と下限を計算
        self.upper_band = bt.indicators.Highest(self.data.high(-1), period=self.params.upper_period)
        self.lower_band = bt.indicators.Lowest(self.data.low(-1), period=self.params.lower_period)

    def next(self):
        if not self.position:  # 現在ポジションがない場合
            if self.dataclose[0] > self.upper_band[0]:  # 終値が上限バンドを超えた場合
                self.buy()
        else:
            if self.dataclose[0] < self.lower_band[0]:  # 終値が下限バンドを下回った場合
                self.sell()

# Yahoo Financeからデータを取得
data = yf.download('AAPL', start='2018-01-01', end='2023-01-01')

# backtraderに渡すためにDataFrameのカラムをリネーム
data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# backtraderにデータを渡す
data_feed = bt.feeds.PandasData(dataname=data)

# Cerebroエンジンのセットアップ
cerebro = bt.Cerebro(optreturn=False)
cerebro.adddata(data_feed)
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)

# 最適化のためにパラメータを範囲指定
strats = cerebro.optstrategy(
    DonchianChannelStrategy,
    upper_period=range(100, 140, 10),
    lower_period=range(50, 70, 10)
)

# 初期ポートフォリオの価値
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 結果を保存するディレクトリの作成
os.makedirs('backtest_results/strategy/donchian-channel-opt', exist_ok=True)

# 最適化を実行
optimized_runs = cerebro.run()

# 最適化結果を表示
final_results_list = []
for i, run in enumerate(optimized_runs):
    for j, strategy in enumerate(run):
        upper_period = strategy.params.upper_period
        lower_period = strategy.params.lower_period
        final_value = strategy.broker.getvalue()

        # プロットを生成して保存
        cerebro = bt.Cerebro()  # 各戦略のために新しいCerebroインスタンスを作成
        cerebro.adddata(data_feed)
        cerebro.addstrategy(DonchianChannelStrategy, upper_period=upper_period, lower_period=lower_period)
        cerebro.broker.setcash(10000.0)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
        thestrats = cerebro.run()

        thestrat = thestrats[0]

        sqn = thestrat.analyzers.sqn.get_analysis()

        fig = cerebro.plot(style='candlestick', dpi=100)[0][0]
        fig.savefig(f'backtest_results/strategy/donchian-channel-opt/result_{i}_{j}_upper{upper_period}_lower{lower_period}.png')
        plt.close(fig)

        final_results_list.append((upper_period, lower_period, final_value, sqn))

# 最適化結果をソートして表示
sorted_by_value = sorted(final_results_list, key=lambda x: x[2], reverse=True)
for upper_period, lower_period, value, sqn in sorted_by_value:
    print(f"Upper Period: {upper_period}, Lower Period: {lower_period}, Final Portfolio Value: {value:.2f}, SQN: {sqn}")
