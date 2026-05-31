import sys
import os
import time
import json
import csv
import warnings
import numpy as np
import globus_compute_sdk
from globus_compute_sdk.serialize import ComputeSerializer, AllCodeStrategies
from model import load_prices, estimate, var_from_hist, POSITIONS, V0
from montecarlo import simulate_batch

warnings.filterwarnings("ignore", category=UserWarning)

N_SIMS = 480_000_000
N_BATCHES = 8
N_BINS = 10000
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")


def online_endpoints():
    client = globus_compute_sdk.Client()
    nodes = [e["uuid"] for e in client.get_endpoints()
             if e["name"].startswith("mc-") and client.get_endpoint_status(e["uuid"])["status"] == "online"]
    return sorted(nodes)


def run(nodes, mu, L, positions, lo, hi):
    serializer = ComputeSerializer(strategy_code=AllCodeStrategies())
    executors = []
    for node in nodes:
        ex = globus_compute_sdk.Executor(endpoint_id=node)
        ex.serializer = serializer
        executors.append(ex)
    batch = N_SIMS // N_BATCHES
    start = time.perf_counter()
    futures = [executors[i % len(executors)].submit(simulate_batch, mu, L, positions, batch, i, lo, hi, N_BINS)
               for i in range(N_BATCHES)]
    counts = sum(f.result() for f in futures)
    elapsed = time.perf_counter() - start
    for ex in executors:
        ex.shutdown()
    return counts, elapsed


def save(timings, counts, edges, var99, var95, es99):
    os.makedirs(RESULTS, exist_ok=True)
    base = timings[0][1]
    with open(os.path.join(RESULTS, "timings.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["nodes", "time_s", "speedup", "efficiency"])
        for n, t in timings:
            writer.writerow([n, round(t, 3), round(base / t, 3), round(base / t / n, 3)])
    with open(os.path.join(RESULTS, "var_results.json"), "w") as f:
        json.dump({"portfolio_value": V0, "n_sims": N_SIMS, "VaR99": var99,
                   "VaR95": var95, "ES99": es99, "VaR99_pct": var99 / V0 * 100}, f, indent=2)
    np.savez(os.path.join(RESULTS, "histogram.npz"), counts=counts, edges=edges)


def main():
    nodes = sys.argv[1:] or online_endpoints()
    print("online endpoints:", len(nodes))
    for node in nodes:
        print("  ", node)

    mu, cov, L = estimate(load_prices())
    sigma = float(np.sqrt(POSITIONS @ cov @ POSITIONS))
    edges = np.linspace(-12 * sigma, 12 * sigma, N_BINS + 1)
    lo, hi = float(edges[0]), float(edges[-1])
    mu, L, positions = mu.tolist(), L.tolist(), POSITIONS.tolist()

    timings = []
    counts = None
    for n in range(1, len(nodes) + 1):
        counts, elapsed = run(nodes[:n], mu, L, positions, lo, hi)
        timings.append((n, elapsed))
        print(f"nodes={n}  sims={N_SIMS:,}  time={elapsed:.2f}s")

    var99, var95, es99 = var_from_hist(counts, edges)
    print(f"VaR99 ${var99:,.0f} ({var99 / V0 * 100:.2f}%)   VaR95 ${var95:,.0f}   ES99 ${es99:,.0f}")
    save(timings, counts, edges, var99, var95, es99)


if __name__ == "__main__":
    main()
