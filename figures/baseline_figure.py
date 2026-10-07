"""Figure 1: weekly true non-marketing sales against Meridian's fitted baseline, and true against fitted PLA
contribution, for arm 1 (one knot) and arm 2a (automatic knots), on the no-mechanism and performance-chasing rows of
the Heusch generator, one seed.

    python figures/baseline_figure.py [seed]     reads results/units/, writes results/figures/fig1_baseline_seed<seed>.{png,pdf}
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNITS = os.path.join(ROOT, "results", "units")
OUT = os.path.join(ROOT, "results", "figures")
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20260908

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#ffffff"
BLUE, ORANGE, TRUTH = "#2a78d6", "#eb6834", "#8a8984"

ROWS = [("none", "No mechanism"), ("performance_chasing", "Performance chasing on PLA")]
ARMS = [("arm1", "Arm 1, one knot"), ("arm2a", "Arm 2a, automatic knots")]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.titlecolor": INK, "axes.titlesize": 9})
fig, axes = plt.subplots(2, 2, figsize=(10, 6.6), sharex=True, sharey=True, facecolor=SURF)
for i, (config, arm_label) in enumerate(ARMS):
    for j, (row, row_label) in enumerate(ROWS):
        ax = axes[i, j]
        d = pd.read_csv(os.path.join(UNITS, f"{row}__{SEED}__{config}.series.csv")).sort_values("week")
        w = d["week"]
        ho = d.loc[~d["train"], "week"]
        if len(ho):
            ax.axvspan(ho.min() - 0.5, ho.max() + 0.5, color=GRID, alpha=0.6, lw=0)
        ax.plot(w, d["truth_nonmarketing"], color=TRUTH, lw=1.4, label="True non-marketing sales")
        ax.plot(w, d["baseline"], color=BLUE, lw=2, label="Fitted baseline")
        ax.plot(w, d["truth_pla_effect"], color=TRUTH, lw=1.4, ls=(0, (3, 2)), label="True PLA contribution")
        ax.plot(w, d["fit_pla"], color=ORANGE, lw=2, label="Fitted PLA contribution")
        tr = d[d["train"]]
        r = tr["baseline"].corr(tr["truth_nonmarketing"])
        stats = (f"baseline {tr['baseline'].mean():,.0f} vs true {tr['truth_nonmarketing'].mean():,.0f}   "
                 f"PLA {tr['fit_pla'].mean():,.0f} vs true {tr['truth_pla_effect'].mean():,.0f}   "
                 f"baseline-truth r {r:.2f}")
        ax.set_title(f"{row_label}\n" if i == 0 else "", loc="left", fontweight="bold")
        ax.text(0.0, 1.015, stats, transform=ax.transAxes, va="bottom", ha="left", fontsize=7.5, color=INK2)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        if j == 0:
            ax.set_ylabel(f"{arm_label}: weekly sales")
        if i == 1:
            ax.set_xlabel("week")
h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=8, labelcolor=INK)
fig.suptitle(f"Meridian 2.0.0 on the Heusch generator, data seed {SEED}: where the fixed baseline's demand goes",
             x=0.01, ha="left", fontsize=10, color=INK, fontweight="bold")
fig.text(0.01, 0.925, "Shaded weeks are the 13-week holdout. Summary figures are training-week means.",
         fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.05, 1, 0.92))
os.makedirs(OUT, exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"fig1_baseline_seed{SEED}.{ext}"), dpi=200, facecolor=SURF)
print(f"results/figures/fig1_baseline_seed{SEED}.png and .pdf")
