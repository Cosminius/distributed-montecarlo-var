import numpy as np
import pandas as pd

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "XOM", "JNJ"]
V0 = 1_000_000.0
POSITIONS = np.full(len(TICKERS), V0 / len(TICKERS))


def load_prices(path="data/data.csv"):
    prices = pd.read_csv(path, index_col=0, parse_dates=True)
    return prices[TICKERS]


def estimate(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    mu = returns.mean().to_numpy()
    cov = returns.cov().to_numpy()
    L = np.linalg.cholesky(cov)
    return mu, cov, L


def var_from_hist(counts, edges):
    counts = np.asarray(counts, dtype=np.float64)
    centers = (edges[:-1] + edges[1:]) / 2
    cumulative = np.cumsum(counts)
    total = cumulative[-1]
    i99 = int(np.searchsorted(cumulative, 0.01 * total))
    i95 = int(np.searchsorted(cumulative, 0.05 * total))
    var99 = -float(centers[i99])
    var95 = -float(centers[i95])
    es99 = -float((centers[:i99 + 1] * counts[:i99 + 1]).sum() / cumulative[i99])
    return var99, var95, es99
