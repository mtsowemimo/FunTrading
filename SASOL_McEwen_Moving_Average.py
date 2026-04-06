import datetime
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Separate analysis for SASOL and McEwen Mining
# Verified Yahoo Finance symbols: SASOL = SSL, McEwen Mining = MUX
tickers = ["SSL", "MUX"]
start_date = "2021-01-01"
end_date = datetime.date.today().strftime("%Y-%m-%d")

results = {}
fig, axes = plt.subplots(nrows=len(tickers), ncols=1, figsize=(14, 4 * len(tickers)), sharex=True)

for ax, ticker in zip(axes, tickers):
    data = yf.download(ticker, start=start_date, end=end_date)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    data = data.dropna(subset=["Close"])

    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    data['Signal'] = 0
    data.loc[data.index[50:], 'Signal'] = (data['MA20'].iloc[50:] > data['MA50'].iloc[50:]).astype(int)

    data['Market Return'] = data['Close'].pct_change()
    data['Strategy Return'] = data['Market Return'] * data['Signal'].shift(1)

    data['Cumulative Market'] = (1 + data['Market Return']).cumprod()
    data['Cumulative Strategy'] = (1 + data['Strategy Return']).cumprod()

    ax.plot(data.index, data['Cumulative Market'], label='Buy & Hold')
    ax.plot(data.index, data['Cumulative Strategy'], label='Strategy')
    ax.set_title(f'{ticker}: Strategy vs Buy & Hold')
    ax.set_ylabel('Cumulative Return')
    ax.legend()
    ax.grid(True)

    results[ticker] = {
        'strategy_return': data['Cumulative Strategy'].iloc[-1] - 1,
        'market_return': data['Cumulative Market'].iloc[-1] - 1,
    }

axes[-1].set_xlabel('Date')
plt.suptitle('SASOL and McEwen Mining Moving Average Strategy Performance', y=1.02, fontsize=16)
plt.tight_layout()
output_file = "SASOL_McEwen_strategy.png"
fig.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"Saved chart to {output_file}")

summary = pd.DataFrame(
    [{
        'Ticker': ticker,
        'Strategy Return': results[ticker]['strategy_return'],
        'Market Return': results[ticker]['market_return'],
    } for ticker in tickers]
)
summary_file = "SASOL_McEwen_results.csv"
summary.to_csv(summary_file, index=False)
print(f"Saved summary to {summary_file}\n")

for ticker in tickers:
    print(f"{ticker} Strategy Return: {results[ticker]['strategy_return']:.2%}")
    print(f"{ticker} Market Return:   {results[ticker]['market_return']:.2%}\n")
