import os
import json
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
FIG = os.path.join(RESULTS, "figures")


def load_timings():
    with open(os.path.join(RESULTS, "timings.csv")) as f:
        return [(int(r["nodes"]), float(r["time_s"]), float(r["speedup"]), float(r["efficiency"]))
                for r in csv.DictReader(f)]


def pnl_histogram():
    d = np.load(os.path.join(RESULTS, "histogram.npz"))
    counts, edges = d["counts"], d["edges"]
    centers = (edges[:-1] + edges[1:]) / 2 / 1000.0
    with open(os.path.join(RESULTS, "var_results.json")) as f:
        res = json.load(f)
    var99 = res["VaR99"] / 1000.0
    es99 = res["ES99"] / 1000.0
    plt.figure(figsize=(9, 5))
    plt.fill_between(centers, counts, step="mid", alpha=0.4, color="steelblue")
    plt.plot(centers, counts, drawstyle="steps-mid", color="steelblue", lw=0.8)
    plt.axvline(-var99, color="red", lw=2, label=f"99% VaR = ${res['VaR99']:,.0f}")
    plt.axvline(-es99, color="darkred", lw=2, ls="--", label=f"99% ES = ${res['ES99']:,.0f}")
    plt.xlabel("1-day portfolio P&L  ($ thousands)")
    plt.ylabel("number of scenarios")
    plt.title(f"Distribution of {res['n_sims']:,} simulated 1-day P&L outcomes")
    plt.xlim(-90, 90)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "pnl_histogram.png"), dpi=130)
    plt.close()


def speedup_chart():
    rows = load_timings()
    nodes = [r[0] for r in rows]
    speedup = [r[2] for r in rows]
    plt.figure(figsize=(7, 5))
    plt.plot(nodes, nodes, "--", color="gray", label="ideal (linear)")
    plt.plot(nodes, speedup, "o-", color="darkgreen", lw=2, label="measured")
    plt.xlabel("number of funcX nodes (containers)")
    plt.ylabel("speedup  (T1 / Tn)")
    plt.title("Speedup vs number of nodes")
    plt.xticks(nodes)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "speedup.png"), dpi=130)
    plt.close()


def efficiency_chart():
    rows = load_timings()
    nodes = [r[0] for r in rows]
    eff = [r[3] * 100 for r in rows]
    plt.figure(figsize=(7, 5))
    plt.axhline(100, ls="--", color="gray", label="ideal (100%)")
    plt.plot(nodes, eff, "o-", color="purple", lw=2, label="measured")
    plt.xlabel("number of funcX nodes (containers)")
    plt.ylabel("parallel efficiency (%)")
    plt.title("Parallel efficiency vs number of nodes")
    plt.xticks(nodes)
    plt.ylim(0, 110)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "efficiency.png"), dpi=130)
    plt.close()


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    pnl_histogram()
    speedup_chart()
    efficiency_chart()
    print("saved figures to", FIG)
