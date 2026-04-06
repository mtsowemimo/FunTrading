import yfinance as yf
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

ticker = "AAPL"
data = yf.download(ticker, period="2y", interval="1d")
data.columns = data.columns.droplevel(1)  # Flatten MultiIndex columns
data = data.dropna()

class SmaCross(Strategy):
    fast = 10
    slow = 20

    def init(self):
        self.ma_fast = self.I(SMA, self.data.Close, self.fast)
        self.ma_slow = self.I(SMA, self.data.Close, self.slow)

    def next(self):
        if crossover(self.ma_fast, self.ma_slow):
            self.buy()
        elif crossover(self.ma_slow, self.ma_fast):
            self.position.close()

bt = Backtest(data, SmaCross, cash=10000, commission=0.002, exclusive_orders=True)
stats = bt.run()
print(stats)
bt.plot()