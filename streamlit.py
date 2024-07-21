import streamlit as st
import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd

class DonchianChannelStrategy(bt.Strategy):
    params = (
        ('profit_period', 180),
        ('upper_period', 120),
        ('lower_period', 60),
    )

    def __init__(self):
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

def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data_feed = bt.feeds.PandasData(dataname=data)
    return data_feed

def run_backtest(data_feed):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(DonchianChannelStrategy)
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    result = cerebro.run()
    sqn = result[0].analyzers.sqn.get_analysis().sqn
    final_value = cerebro.broker.getvalue()

    st.write(f"SQN: {sqn:.2f}")
    st.write(f"Final Portfolio Value: ${final_value:.2f}")

    # グラフのプロット
    fig = cerebro.plot()[0][0]
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    st.image(buf, use_column_width=True)  # 画像のサイズを列の幅に合わせて調整

st.title('Backtrader Donchian Channel Strategy Backtest')

ticker = st.text_input('Ticker', 'AAPL')
start_date = st.date_input('Start Date', value=pd.to_datetime('2018-01-01'))
end_date = st.date_input('End Date', value=pd.to_datetime('2023-01-01'))

if st.button('Run Backtest'):
    data_feed = fetch_data(ticker, start_date, end_date)
    run_backtest(data_feed)
