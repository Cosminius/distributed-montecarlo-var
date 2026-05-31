import numpy as np


def simulate_batch(mu, L, positions, n_sims, seed, lo, hi, n_bins):
    import numpy as np
    rng = np.random.default_rng(seed)
    mu = np.asarray(mu)
    L = np.asarray(L)
    positions = np.asarray(positions)
    counts = np.zeros(n_bins, dtype=np.int64)
    done = 0
    while done < n_sims:
        m = min(1_000_000, n_sims - done)
        z = rng.standard_normal((m, len(mu)))
        returns = mu + z @ L.T
        pnl = np.expm1(returns) @ positions
        counts += np.histogram(pnl, bins=n_bins, range=(lo, hi))[0]
        done += m
    return counts
