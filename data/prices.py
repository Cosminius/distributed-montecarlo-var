import yfinance as yf

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM","XOM","JNJ"]

raw_data = yf.download(TICKERS, period ="3y", interval = "1d", auto_adjust=True)
raw_data = raw_data["Close"][TICKERS]
raw_data = raw_data.dropna()
raw_data.to_csv("data.csv")

print("shape:", raw_data.shape)
print("range:", raw_data.index.min().date(), raw_data.index.max().date())
print(raw_data.tail(3))
