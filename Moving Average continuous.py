import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. Download stock data
ticker = "AAPL"  # you can change this
data = yf.download(ticker, start="2020-01-01", end="2024-01-01")
data.columns = data.columns.droplevel(1)  # Flatten MultiIndex columns

# 2. Calculate moving averages
data['MA20'] = data['Close'].rolling(window=20).mean()
data['MA50'] = data['Close'].rolling(window=50).mean()

# 3. Create signals
data['Signal'] = 0
data['Signal'][50:] = (data['MA20'][50:] > data['MA50'][50:]).astype(int)  # Start from where MA50 is valid

# 4. Create positions (buy/sell points)
data['Position'] = data['Signal'].diff()

# 5. Calculate returns
data['Market Return'] = data['Close'].pct_change()
data['Strategy Return'] = data['Market Return'] * data['Signal'].shift(1)

# 6. Cumulative returns
data['Cumulative Market'] = (1 + data['Market Return']).cumprod()
data['Cumulative Strategy'] = (1 + data['Strategy Return']).cumprod()

# 7. Plot results
plt.figure(figsize=(12,6))
plt.plot(data['Cumulative Market'], label='Buy & Hold')
plt.plot(data['Cumulative Strategy'], label='Strategy')
plt.legend()
plt.title(f'{ticker} Strategy vs Buy & Hold')
plt.show()

# 8. Print performance
total_return_strategy = data['Cumulative Strategy'].iloc[-1] - 1
total_return_market = data['Cumulative Market'].iloc[-1] - 1

print(f"Strategy Return: {total_return_strategy:.2%}")
print(f"Market Return: {total_return_market:.2%}")