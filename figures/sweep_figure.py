"""Figure 2: PLA estimated (posterior median of the per-draw average return) over true average return, per seed, (a) against the knot count of Meridian's baseline and
(b) against the strength of performance chasing.

    python figures/sweep_figure.py      reads results/fits.csv, writes results/figures/fig2_sweeps.{png,pdf}
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "figures")
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#ffffff"
BLUE, ORANGE, TRUTH = "#2a78d6", "#eb6834", "#8a8984"
TWO_ROWS = ("none", "performance_chasing")

f = pd.read_csv(os.path.join(ROOT, "results", "fits.csv"))
f = f[(f["channel"] == "pla") & f["converged"]].copy()
f["r"] = f["est_avg"] / f["true_avg"]
knot_x = {"arm1": 1, "knots4": 4, "knots13": 13, "knots26": 26, "knots52": 52}
k = f[f["config"].isin(knot_x) & f["row"].isin(TWO_ROWS)].assign(x=lambda d: d["config"].map(knot_x))
aks = f[(f["config"] == "arm2a") & f["row"].isin(TWO_ROWS)]
lvl = {"none": 0.0, "performance_chasing_0p2": 0.2, "performance_chasing_0p4": 0.4, "performance_chasing": 0.8}
s = f[f["config"].isin(["arm1", "arm2a"]) & f["row"].isin(lvl)].assign(x=lambda d: d["row"].map(lvl))

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "axes.titlesize": 9})
fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.3), sharey=True, facecolor=SURF)
yt = [0.25, 0.5, 1, 2, 4, 8, 16]


def style(ax):
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator(yt))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}x"))
    ax.set_ylim(0.2, 16)
    ax.axhline(1, color=TRUTH, lw=1.2, ls=(0, (3, 2)))
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


# (a) knots
xs = [1, 4, 13, 26, 52]
for row, color, label, dx in (("performance_chasing", ORANGE, "Performance chasing on PLA", 1.04), ("none", BLUE, "No mechanism", 0.96)):
    d = k[k["row"] == row]
    a.scatter(d["x"] * dx, d["r"], s=22, color=color, edgecolor=SURF, linewidth=0.8, zorder=3)
    m = d.groupby("x")["r"].median().reindex(xs)
    a.plot([x * dx for x in xs], m.values, color=color, lw=2, label=label, zorder=2)
    e = aks[aks["row"] == row]
    a.scatter([75 * dx] * len(e), e["r"], s=22, color=color, edgecolor=SURF, linewidth=0.8, marker="D", zorder=3)
auto = f"auto\n({aks['n_knots'].min()} to {aks['n_knots'].max()})"
a.set_xscale("log")
a.xaxis.set_major_locator(FixedLocator(xs + [75]))
a.xaxis.set_minor_locator(NullLocator())
a.xaxis.set_major_formatter(FuncFormatter(lambda v, _: auto if v == 75 else f"{v:g}"))
a.set_xlabel("knots in Meridian's baseline (arm 1 with knots fixed; auto is arm 2a)")
a.set_ylabel("PLA estimated / true average return\n(posterior median of the per-draw return)")
a.set_title("(a) Baseline flexibility, two rows", loc="left", fontweight="bold")
a.text(1.05, 1.08, "truth", color=INK2, fontsize=7.5)
a.legend(frameon=False, loc="upper right", fontsize=8)
style(a)

# (b) strength
levels = [0.0, 0.2, 0.4, 0.8]
for config, color, label, dx in (("arm1", ORANGE, "Arm 1, one knot", 0.012), ("arm2a", BLUE, "Arm 2a, automatic knots", -0.012)):
    d = s[s["config"] == config]
    b.scatter(d["x"] + dx, d["r"], s=22, color=color, edgecolor=SURF, linewidth=0.8, zorder=3)
    m = d.groupby("x")["r"].median().reindex(levels)
    b.plot([x + dx for x in levels], m.values, color=color, lw=2, label=label, zorder=2)
b.xaxis.set_major_locator(FixedLocator(levels))
b.set_xlabel("strength of performance chasing on PLA (roi_sensitivity; published default 0.8)")
b.set_title("(b) Auto-bidding strength, two configurations", loc="left", fontweight="bold")
b.legend(frameon=False, loc="upper left", fontsize=8)
style(b)

fig.suptitle("Meridian 2.0.0 on the Heusch generator: each dot is one data seed, lines are medians, converged fits only",
             x=0.01, ha="left", fontsize=10, color=INK, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.94))
os.makedirs(OUT, exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"fig2_sweeps.{ext}"), dpi=200, facecolor=SURF)
print(f"results/figures/fig2_sweeps.png and .pdf ({len(k)} knot, {len(aks)} automatic, {len(s)} strength points)")
