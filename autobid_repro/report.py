"""The tables of the note, from the fits under <results>/units/.

    python -m autobid_repro.report [--results results] [--recompute]

--recompute first rewrites every fit's per-draw columns (fit.summarize) from its saved draws, <unit>.draws.npz,
without refitting.

Writes <results>/fits.csv (every fit, every channel), <results>/baseline_metrics.csv, <results>/learnings.csv and
one markdown file per result under <results>/tables/. A table whose fits are not all present is skipped and says so.

Conventions. Seeds are 20260908 to 20260912; per-seed values are listed in that order, nc where the fit did not
converge (max R-hat above 1.1 or minimum bulk ESS below 400). Each fit's estimate is the posterior median of the
per-draw return and its 90 percent interval the 5th to 95th percentile, over the fit's 1,000 saved draws (fit.py).
Beside it: the plug-in return (the curve at posterior-mean cap and posterior-median k and s, the estimand the note
first reported) and Meridian's own ROI (`Analyzer.roi()`, posterior median over the same draws). Medians of estimates
are over converged seeds; true values are medians over all seeds. Covered counts the converged seeds whose 90
percent interval contains the true value. Sign is the four-of-five rule on the
average return's signed bias: high or low when at least four of five converged seeds agree, indeterminate otherwise
or when fewer than five converged.
"""

from __future__ import annotations

import argparse
import glob
import os

import numpy as np
import pandas as pd

from . import experiment, fit, generator

SEEDS = generator.SEEDS
MECHANISM_ROWS = ("none", "budget_feedback", "anticipatory_spend", "tv_bursts", "performance_chasing", "all_four")
TWO_ROWS = ("none", "performance_chasing")
CHANNELS = ("meta", "pla", "tv")
ARM_NAMES = {"arm1": "arm 1", "arm2a": "arm 2a", "step1": "step 1"}
STRENGTH = {"none": 0.0, "performance_chasing_0p2": 0.2, "performance_chasing_0p4": 0.4, "performance_chasing": 0.8}


# ---- loading ---------------------------------------------------------------------------------------------------

def load_fits(results: str) -> pd.DataFrame:
    files = [f for f in glob.glob(os.path.join(results, "units", "*.csv")) if not f.endswith(".series.csv")]
    if not files:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in sorted(files)], ignore_index=True)


def load_series(results: str, row: str, seed: int, config: str) -> pd.DataFrame | None:
    p = os.path.join(results, "units", f"{row}__{seed}__{config}.series.csv")
    return pd.read_csv(p) if os.path.exists(p) else None


def have(fits: pd.DataFrame, units) -> list:
    """The units of a table that have no fit yet."""
    got = set() if fits.empty else set(zip(fits["row"], fits["seed"], fits["config"]))
    return [u for u in units if u not in got]


def skipped(name: str, missing: list) -> str:
    return f"Not written: {len(missing)} fit(s) missing, e.g. {' '.join(map(str, missing[0]))}. Run the full mode.\n"


# ---- formatting ------------------------------------------------------------------------------------------------

def f2(v) -> str:
    return "nc" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.2f}"


def per_seed(g: pd.DataFrame, col: str, fmt=f2) -> str:
    g = g.set_index("seed")
    return ", ".join(fmt(g.at[s, col]) if s in g.index and g.at[s, "converged"] else "nc" for s in SEEDS)


def sign(g: pd.DataFrame) -> str:
    c = g[g["converged"]]
    hi, lo, n = int((c["est_avg"] > c["true_avg"]).sum()), int((c["est_avg"] < c["true_avg"]).sum()), len(c)
    if n == len(SEEDS) and hi >= 4:
        return f"high {hi}/{n}"
    if n == len(SEEDS) and lo >= 4:
        return f"low {lo}/{n}"
    return f"indeterminate {max(hi, lo)}/{n}"


def covered(g: pd.DataFrame, what: str) -> str:
    c = g[g["converged"]]
    k = int(((c[f"{what}_lo"] <= c[f"true_{what}"]) & (c[f"true_{what}"] <= c[f"{what}_hi"])).sum())
    return f"{k}/{len(c)}"


def med(g: pd.DataFrame, col: str) -> float:
    c = g[g["converged"]]
    return float(c[col].median()) if len(c) else float("nan")


def extra(g: pd.DataFrame) -> list[str]:
    """The plug-in average and marginal return and Meridian's ROI, medians over converged seeds."""
    return [f2(med(g, "plugin_avg")), f2(med(g, "plugin_marg")), f2(med(g, "meridian_roi_median"))]


EXTRA = ["median plug-in avg", "median plug-in marg", "median Meridian ROI"]


UNCALIBRATED = ("arm1", "arm2a", "step1", "knots4", "knots13", "knots26", "knots52")


def roi_prior(config: str = "arm1") -> dict:
    """PLA's ROI prior at an uncalibrated configuration, read from the model specification the fits used: Meridian
    2.0.0's default, LogNormal(0.2, 0.9) (arm 2a states the same values). Its median, mean and 5th to 95th
    percentile."""
    import warnings
    warnings.filterwarnings("ignore")
    from scipy import stats
    d = fit.model_spec(config, 156).prior.roi_m
    mu = float(np.ravel(d.parameters["loc"])[fit.CHANNELS.index("pla")] if np.ndim(d.parameters["loc"]) else d.parameters["loc"])
    sd = float(np.ravel(d.parameters["scale"])[fit.CHANNELS.index("pla")] if np.ndim(d.parameters["scale"]) else d.parameters["scale"])
    z = stats.norm.ppf(0.95)
    return {"loc": mu, "scale": sd, "median": np.exp(mu), "mean": np.exp(mu + sd ** 2 / 2),
            "lo": np.exp(mu - z * sd), "hi": np.exp(mu + z * sd)}


def prior_line(p: dict) -> str:
    return (f"PLA's ROI prior at every uncalibrated configuration (Meridian 2.0.0's default, read from the fitted model "
            f"specification): LogNormal({p['loc']:g}, {p['scale']:g}), median {p['median']:.2f}, mean {p['mean']:.2f}, "
            f"90 percent interval (5th to 95th percentile) [{p['lo']:.2f}, {p['hi']:.2f}], width {p['hi'] - p['lo']:.2f}.")


def prior_table(fits: pd.DataFrame, cells) -> str:
    """Per uncalibrated (config, row) cell: PLA's per-draw average return and Meridian's ROI beside the ROI prior.
    Median and interval bounds are medians over converged seeds; each ratio is the median over converged seeds of the
    per-fit ratio."""
    pr = {c: roi_prior(c) for c in {c for c, _ in cells if c in UNCALIBRATED}}
    if len({(v["loc"], v["scale"]) for v in pr.values()}) > 1:
        raise RuntimeError("uncalibrated configurations do not share one ROI prior")
    p = next(iter(pr.values()))
    width = p["hi"] - p["lo"]
    rows = []
    for c, r in cells:
        if c not in UNCALIBRATED:
            continue
        g = fits[(fits["config"] == c) & (fits["row"] == r) & (fits["channel"] == "pla") & fits["converged"]]
        if g.empty:
            continue
        rows.append([c, r, len(g), f"{p['median']:.2f} [{p['lo']:.2f}, {p['hi']:.2f}]",
                     f"{g['est_avg'].median():.2f} [{g['avg_lo'].median():.2f}, {g['avg_hi'].median():.2f}]",
                     f"{(g['est_avg'] / p['median']).median():.2f}", f"{((g['avg_hi'] - g['avg_lo']) / width).median():.2f}",
                     f"{g['meridian_roi_median'].median():.2f} [{g['meridian_roi_lo'].median():.2f}, "
                     f"{g['meridian_roi_hi'].median():.2f}]",
                     f"{(g['meridian_roi_median'] / p['median']).median():.2f}",
                     f"{((g['meridian_roi_hi'] - g['meridian_roi_lo']) / width).median():.2f}",
                     f2(g["true_avg"].median())])
    return (prior_line(p) + " Beside it, per uncalibrated cell: PLA's per-draw average return and Meridian's ROI "
            "(the quantity the prior is placed on), median [5th, 95th percentile] over the fit's saved draws, as medians "
            "over converged seeds; each ratio is the median over converged seeds of the per-fit ratio (median over the "
            "prior's median; interval width over the prior's interval width).\n\n" + md(
                ["config", "row", "converged", "ROI prior median [90%]", "per-draw avg [90%]", "median / prior median",
                 "width / prior width", "Meridian ROI [90%]", "ROI median / prior median", "ROI width / prior width",
                 "true avg"], rows))


def md(header: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


# ---- result a: the six mechanism rows --------------------------------------------------------------------------

def mechanisms(fits: pd.DataFrame) -> str:
    units = [(r, s, c) for c in ARM_NAMES for r in MECHANISM_ROWS for s in SEEDS]
    if (missing := have(fits, units)):
        return skipped("mechanisms", missing)
    f = fits[fits["config"].isin(ARM_NAMES) & fits["row"].isin(MECHANISM_ROWS)]
    out = []
    head = ["row", "channel", "true avg", "true marg", "median est avg", "median est marg", "per-seed est avg",
            "per-seed est marg", "sign (4 of 5)", "covered avg", "covered marg", "converged", "median wall s"] + EXTRA
    for config, name in ARM_NAMES.items():
        rows = []
        for r in MECHANISM_ROWS:
            for ch in CHANNELS:
                g = f[(f["config"] == config) & (f["row"] == r) & (f["channel"] == ch)]
                rows.append([r, ch, f2(g["true_avg"].median()), f2(g["true_marg"].median()), f2(med(g, "est_avg")),
                             f2(med(g, "est_marg")), per_seed(g, "est_avg"), per_seed(g, "est_marg"), sign(g),
                             covered(g, "avg"), covered(g, "marg"), f"{int(g['converged'].sum())}/{len(g)}",
                             f"{g['wall_seconds'].median():.1f}"] + extra(g))
        out.append(f"### {name.capitalize()}\n\n" + md(head, rows))
    rows = []
    for r in MECHANISM_ROWS:
        row = [r]
        for config in ARM_NAMES:
            g = f[(f["config"] == config) & (f["row"] == r) & (f["channel"] == "pla")]
            if config == "arm1":
                row = [r, f2(g["true_avg"].median()), f2(g["true_marg"].median())]
            row += [f2(med(g, "est_avg")), f2(med(g, "est_marg")), per_seed(g, "est_avg"), sign(g), covered(g, "avg"),
                    f"{int(g['converged'].sum())}/{len(g)}", f2(med(g, "plugin_avg")), f2(med(g, "meridian_roi_median")),
                    per_seed(g, "meridian_roi_median")]
        rows.append(row)
    head = ["row", "true avg", "true marg"] + [f"{n} {x}" for n in ARM_NAMES.values() for x in
                                               ("median avg", "median marg", "per-seed avg", "sign", "covered", "converged",
                                                "median plug-in avg", "median Meridian ROI", "per-seed Meridian ROI")]
    out.append("### PLA, the three configurations side by side\n\n" + md(head, rows))
    out.append("### PLA against the default ROI prior\n\n" + prior_table(f, [(c, r) for c in ARM_NAMES
                                                                           for r in MECHANISM_ROWS]))
    nc = f[(~f["converged"]) & (f["channel"] == "pla")].sort_values(["config", "row", "seed"])
    out.append("### Fits that did not converge\n\n" + md(
        ["configuration", "row", "seed", "max R-hat", "min bulk ESS"],
        [[ARM_NAMES[x.config], x.row, x.seed, f"{x.max_rhat:.3f}", f"{x.min_ess_bulk:.0f}"] for x in nc.itertuples()]))
    k = f[(f["config"] == "arm2a") & (f["channel"] == "pla")].pivot(index="row", columns="seed", values="n_knots")
    out.append("### Knots chosen by automatic selection at arm 2a\n\n" + md(
        ["row"] + [str(s) for s in SEEDS], [[r] + [int(k.at[r, s]) for s in SEEDS] for r in MECHANISM_ROWS]))
    return "\n".join(out)


# ---- result b: the weekly baseline decomposition ---------------------------------------------------------------

def metrics(s: pd.DataFrame) -> dict:
    resid = s["truth_nonmarketing"] - s["baseline"]
    return {"corr_baseline_truth": float(np.corrcoef(s["baseline"], s["truth_nonmarketing"])[0, 1]),
            "rmse": float(np.sqrt(np.mean(resid ** 2))),
            "corr_resid_pla_spend": float(np.corrcoef(resid, s["pla_spend"])[0, 1]),
            "resid_share_of_pla": float(resid.sum() / s["fit_pla"].sum()),
            "pla_fit_over_true": float(s["fit_pla"].sum() / s["truth_pla_effect"].sum()),
            "corr_pla_spend_truth_nonmarketing": float(np.corrcoef(s["pla_spend"], s["truth_nonmarketing"])[0, 1]),
            "baseline_mean": float(s["baseline"].mean()), "truth_mean": float(s["truth_nonmarketing"].mean()),
            "fit_pla_mean": float(s["fit_pla"].mean()), "truth_pla_mean": float(s["truth_pla_effect"].mean())}


def baseline_metrics(results: str, fits: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for x in fits[(fits["channel"] == "pla") & fits["row"].isin(TWO_ROWS)].itertuples():
        s = load_series(results, x.row, x.seed, x.config)
        if s is None:
            continue
        key = {"row": x.row, "seed": x.seed, "config": x.config, "converged": x.converged, "n_knots": x.n_knots}
        rows.append({**key, "window": "all", **metrics(s)})
        rows.append({**key, "window": "train", **metrics(s[s["train"]])})
    return pd.DataFrame(rows)


def cell(g: pd.DataFrame, col: str, fmt="{:.2f}") -> str:
    g = g.sort_values("seed")
    return f"{fmt.format(g[col].median())} ({', '.join(fmt.format(v) for v in g[col])})"


def baseline(fits: pd.DataFrame, bm: pd.DataFrame) -> str:
    units = [(r, s, c) for c in ARM_NAMES for r in TWO_ROWS for s in SEEDS]
    if (missing := have(fits, units)):
        return skipped("baseline", missing)
    rows = []
    for config in ARM_NAMES:
        for r in TWO_ROWS:
            for w in ("all", "train"):
                g = bm[(bm["config"] == config) & (bm["row"] == r) & (bm["window"] == w)]
                rows.append([ARM_NAMES[config], r, w, len(g), cell(g, "corr_baseline_truth"), cell(g, "rmse", "{:.0f}"),
                             cell(g, "corr_resid_pla_spend"), cell(g, "resid_share_of_pla"), cell(g, "pla_fit_over_true")])
    out = ["Each cell: median over seeds (per-seed values in seed order), every seed whether or not it converged. "
           "Baseline: Meridian's posterior-mean expected outcome with media at zero. Truth: base_sales plus "
           "promotional_sales_uplift. Residual: truth less baseline. Share: summed residual over PLA's summed fitted "
           "contribution. Window all is the 156 weeks, train the 143 before the holdout.\n",
           md(["config", "row", "window", "seeds", "corr(baseline, truth)", "RMSE", "corr(residual, PLA spend)",
               "residual share of PLA contribution", "PLA fitted / true"], rows)]
    g = bm[(bm["window"] == "all") & (bm["config"] == "arm1")]
    out.append("corr(PLA spend, true non-marketing sales), all weeks: " + "; ".join(
        f"{r} {cell(g[g['row'] == r], 'corr_pla_spend_truth_nonmarketing')}" for r in TWO_ROWS) + "\n")
    f = fits[(fits["channel"] == "pla") & fits["config"].isin(["arm1", "step1"]) & fits["row"].isin(TWO_ROWS)]
    rows = []
    for x in f.sort_values(["row", "config", "seed"]).itertuples():
        frac = x.mean_weekly_spend ** x.s / (x.mean_weekly_spend ** x.s + x.k ** x.s)
        rows.append([x.row, ARM_NAMES[x.config], x.seed, f"{x.mean_weekly_spend:.1f}", f"{x.k:.1f}",
                     f"{x.mean_weekly_spend / x.k:.3f}", f"{x.s:.2f}", f"{x.cap:.0f}", f"{frac:.3f}", f2(x.plugin_avg),
                     f2(x.plugin_marg), f2(x.plugin_marg / x.plugin_avg), f2(x.est_avg), f2(x.meridian_roi_median)])
    out.append("### PLA's fitted Hill curve at the mean weekly spend, arm 1 and step 1\n\n"
               "Point curve: cap posterior mean, k and s posterior medians, so avg and marg here are the plug-in "
               "returns, for which marg/avg = s(1 - f/cap). Beside them the per-draw median average return and "
               "Meridian's ROI.\n\n" + md(
                   ["row", "config", "seed", "mean weekly spend x", "k", "x/k", "slope s", "cap", "f(x)/cap",
                    "plug-in avg", "plug-in marg", "marg/avg", "per-draw avg", "Meridian ROI"], rows))
    return "\n".join(out)


# ---- result c: the knot sweep ----------------------------------------------------------------------------------

KNOT_CONFIGS = (("arm1", "1 (arm 1)"), ("knots4", "4"), ("knots13", "13"), ("knots26", "26"), ("knots52", "52"),
                ("arm2a", "automatic (arm 2a)"))


def knots(fits: pd.DataFrame, bm: pd.DataFrame) -> str:
    units = [(r, s, c) for c, _ in KNOT_CONFIGS for r in TWO_ROWS for s in SEEDS]
    if (missing := have(fits, units)):
        return skipped("knots", missing)
    f = fits[fits["channel"] == "pla"]
    b = bm[bm["window"] == "all"]
    rows, pc_medians = [], []
    for config, label in KNOT_CONFIGS:
        for r in TWO_ROWS:
            g = f[(f["config"] == config) & (f["row"] == r)]
            h = b[(b["config"] == config) & (b["row"] == r) & b["converged"]]
            n = g["n_knots"]
            if r == "performance_chasing" and config != "arm2a":
                pc_medians.append(med(g, "est_avg"))
            rows.append([label, r, f"{n.min()}" if n.min() == n.max() else f"{n.min()} to {n.max()}",
                         f"{int(g['converged'].sum())}/{len(g)}", f2(g["true_avg"].median()), f2(med(g, "est_avg")),
                         per_seed(g, "est_avg"), f2(g["true_marg"].median()), f2(med(g, "est_marg")),
                         per_seed(g, "est_marg"), covered(g, "avg"), covered(g, "marg"),
                         f2(h["corr_baseline_truth"].median()),
                         f"{h['baseline_mean'].median():,.0f} ({h['truth_mean'].median():,.0f})",
                         f"{h['fit_pla_mean'].median():,.0f} ({h['truth_pla_mean'].median():,.0f})",
                         f2(h["corr_resid_pla_spend"].median())] + extra(g))
    falling = all(a > b for a, b in zip(pc_medians, pc_medians[1:]))
    return ("Arm 1 with the number of time knots fixed; arm 1 itself has one knot and arm 2a selects them "
            "automatically. Each cell: median over converged seeds. Baseline figures are weekly means over all 156 "
            "weeks, truth in parentheses.\n\n" + md(
                ["knots", "row", "n knots fitted", "converged", "true avg", "median est avg", "per-seed est avg",
                 "true marg", "median est marg", "per-seed est marg", "covered avg", "covered marg",
                 "corr(baseline, truth)", "baseline mean (truth)", "PLA contribution mean (truth)",
                 "corr(residual, PLA spend)"] + EXTRA, rows) +
            f"\nPLA median average return on performance_chasing at 1, 4, 13, 26, 52 knots: "
            f"{', '.join(f2(v) for v in pc_medians)}; strictly falling: {falling}.\n"
            "\n### PLA against the default ROI prior\n\n" + prior_table(fits, [(c, r) for c, _ in KNOT_CONFIGS
                                                                              for r in TWO_ROWS]))


# ---- result d: auto-bidding strength ---------------------------------------------------------------------------

def strength(fits: pd.DataFrame, notebook_path: str | None) -> str:
    units = [(r, s, c) for c in ("arm1", "arm2a") for r in STRENGTH for s in SEEDS]
    if (missing := have(fits, units)):
        return skipped("strength", missing)
    f = fits[fits["channel"] == "pla"]
    corr = {}
    for r in STRENGTH:
        v = []
        for s in SEEDS:
            fr = generator.frame(r, s, notebook_path)
            v.append(np.corrcoef(fr["pla_spend"], fr["base_sales"] + fr["promotional_sales_uplift"])[0, 1])
        corr[r] = f"{np.median(v):.2f} ({', '.join(f'{x:.2f}' for x in v)})"
    rows, ratio = [], []
    for r, lvl in STRENGTH.items():
        for config in ("arm1", "arm2a"):
            g = f[(f["config"] == config) & (f["row"] == r)]
            if config == "arm1":
                ratio.append(med(g, "est_avg") / g["true_avg"].median())
            rows.append([f"{lvl:.1f}", r, corr[r], f2(g["true_avg"].median()), f2(g["true_marg"].median()),
                         ARM_NAMES[config], f"{int(g['converged'].sum())}/{len(g)}", f2(med(g, "est_avg")),
                         per_seed(g, "est_avg"), f2(med(g, "est_marg")), per_seed(g, "est_marg"), covered(g, "avg"),
                         covered(g, "marg")] + extra(g))
    return ("Performance chasing alone at roi_sensitivity 0 (the none row), 0.2, 0.4 and 0.8 (the published value). "
            "The correlation is over all 156 weeks of the generator's frame, per seed in parentheses.\n\n" + md(
                ["roi_sensitivity", "row", "corr(PLA spend, true non-marketing)", "true avg", "true marg", "config",
                 "converged", "median est avg", "per-seed est avg", "median est marg", "per-seed est marg",
                 "covered avg", "covered marg"] + EXTRA, rows) +
            f"\nArm 1 median PLA average return over truth at 0, 0.2, 0.4, 0.8: {', '.join(f2(v) for v in ratio)}.\n"
            "\n### PLA against the default ROI prior\n\n" + prior_table(fits, [(c, r) for c in ("arm1", "arm2a")
                                                                              for r in STRENGTH]))


# ---- result e: calibration -------------------------------------------------------------------------------------

def learnings(notebook_path: str | None) -> pd.DataFrame:
    return pd.DataFrame([experiment.run(r, s, lv, notebook_path) for lv in experiment.LEVELS for r in TWO_ROWS
                         for s in SEEDS])


def calibration(fits: pd.DataFrame, bm: pd.DataFrame, L: pd.DataFrame) -> str:
    configs = [f"{a}{lv}" for a in ("arm1", "arm2a") for lv in ("", "_weak", "_strong")]
    units = [(r, s, c) for c in configs for r in TWO_ROWS for s in SEEDS]
    if (missing := have(fits, units)):
        return skipped("calibration", missing)
    out = ["PLA's ROI prior set from the go-dark experiment on the same instance (experiment.py); Meta and TV at "
           "Meridian's default. Uncalibrated rows are the arm 1 and arm 2a fits of the mechanisms set.\n"]
    rows = []
    for x in L.itertuples():
        rows.append([x.row, x.seed, x.level, f"{x.effect:,.0f} ({x.se:,.0f})", f"{x.true_effect:,.0f}",
                     f"{x.iroas:.2f} [{x.iroas_lo:.2f}, {x.iroas_hi:.2f}]", f"{x.prior_mean:.2f} (sd {x.prior_sd:.2f})",
                     f"{x.prior_loc:.3f}, {x.prior_scale:.3f}", f"{x.true_iroas:.2f}"])
    out.append("### The experiments and the priors they set\n\n" + md(
        ["row", "seed", "level", "effect (SE)", "true effect", "iROAS [95%]", "prior mean (sd)", "prior loc, scale",
         "experiment's true iROAS"], rows))
    rows, rows_mt = [], []
    for r in TWO_ROWS:
        for a in ("arm1", "arm2a"):
            for lv in ("", "_weak", "_strong"):
                g = fits[(fits["config"] == a + lv) & (fits["row"] == r)]
                p = g[g["channel"] == "pla"]
                level = lv.strip("_") or "uncalibrated"
                rows.append([r, ARM_NAMES[a], level,
                             f"{f2(med(p, 'est_avg'))} ({per_seed(p, 'est_avg')})", f2(p["true_avg"].median()),
                             f"{f2(med(p, 'est_marg'))} ({per_seed(p, 'est_marg')})", f2(p["true_marg"].median()),
                             covered(p, "avg"), covered(p, "marg"), f"{int(p['converged'].sum())}/{len(p)}"] + extra(p))
                rows_mt.append([r, ARM_NAMES[a], level] + [
                    f"{f2(med(g[g['channel'] == c], 'est_avg'))} ({f2(g[g['channel'] == c]['true_avg'].median())})"
                    for c in ("meta", "tv")])
    out.append("### PLA\n\n" + md(["row", "config", "level", "PLA avg median (per seed)", "true avg",
                                   "PLA marg median (per seed)", "true marg", "covered avg", "covered marg",
                                   "converged"] + EXTRA, rows))
    out.append("### Uncalibrated PLA against the default ROI prior\n\n" + prior_table(
        fits, [(a, r) for r in TWO_ROWS for a in ("arm1", "arm2a")]))
    out.append("### Meta and TV average return, median (true)\n\n" + md(["row", "config", "level", "Meta", "TV"], rows_mt))
    rows = []
    for lv in ("", "_weak", "_strong"):
        g = bm[(bm["config"] == "arm1" + lv) & (bm["row"] == "performance_chasing") & (bm["window"] == "all")]
        rows.append([lv.strip("_") or "uncalibrated", cell(g, "baseline_mean", "{:,.0f}"),
                     f"{g['truth_mean'].median():,.0f}", cell(g, "corr_resid_pla_spend"),
                     cell(g, "resid_share_of_pla"), cell(g, "pla_fit_over_true"), f"{int(g['converged'].sum())}/{len(g)}"])
    out.append("### Arm 1 baseline on performance_chasing, all weeks\n\n" + md(
        ["level", "baseline mean, median (per seed)", "truth mean", "corr(residual, PLA spend)",
         "residual share of PLA contribution", "PLA fitted / true", "converged"], rows))
    return "\n".join(out)


# ---- quick mode ------------------------------------------------------------------------------------------------

def quick(fits: pd.DataFrame) -> str:
    f = fits[(fits["channel"] == "pla") & (fits["row"] == "performance_chasing") & (fits["seed"] == SEEDS[0])
             & fits["config"].isin(["arm1", "arm2a"])].sort_values("config")
    return ("PLA on performance_chasing, seed 20260908.\n\n" + md(
        ["config", "converged", "knots", "est avg [90%]", "est marg [90%]", "true avg", "true marg", "plug-in avg",
         "plug-in marg", "Meridian ROI median [90%]", "wall s"],
        [[x.config, x.converged, x.n_knots, f"{x.est_avg:.2f} [{x.avg_lo:.2f}, {x.avg_hi:.2f}]",
          f"{x.est_marg:.2f} [{x.marg_lo:.2f}, {x.marg_hi:.2f}]", f2(x.true_avg), f2(x.true_marg), f2(x.plugin_avg),
          f2(x.plugin_marg), f"{x.meridian_roi_median:.2f} [{x.meridian_roi_lo:.2f}, {x.meridian_roi_hi:.2f}]",
          f"{x.wall_seconds:.0f}"] for x in f.itertuples()]))


def recompute(results: str) -> int:
    """Rewrite the per-draw columns of every unit under <results>/units/ from its saved draws."""
    n = 0
    for path in sorted(glob.glob(os.path.join(results, "units", "*.draws.npz"))):
        table = path[:-len(".draws.npz")] + ".csv"
        df = pd.read_csv(table)
        with np.load(path) as d:
            per = fit.summarize(d)
        for col in next(iter(per.values())):
            df[col] = [per[c][col] for c in df["channel"]]
        df.to_csv(table + ".tmp", index=False)
        os.replace(table + ".tmp", table)
        n += 1
    return n


def write_all(results: str, notebook_path: str | None = None) -> None:
    fits = load_fits(results)
    if fits.empty:
        print("no fits")
        return
    fits = fits.sort_values(["config", "row", "seed", "channel"]).reset_index(drop=True)
    fits.to_csv(os.path.join(results, "fits.csv"), index=False)
    bm = baseline_metrics(results, fits)
    bm.to_csv(os.path.join(results, "baseline_metrics.csv"), index=False)
    L = learnings(notebook_path)
    L.to_csv(os.path.join(results, "learnings.csv"), index=False)
    tables = {"quick": quick(fits), "mechanisms": mechanisms(fits), "baseline": baseline(fits, bm),
              "knots": knots(fits, bm), "strength": strength(fits, notebook_path),
              "calibration": calibration(fits, bm, L)}
    os.makedirs(os.path.join(results, "tables"), exist_ok=True)
    for name, text in tables.items():
        with open(os.path.join(results, "tables", f"{name}.md"), "w") as fh:
            fh.write(f"# {name.capitalize()}\n\n{text}")
        print(f"tables/{name}.md: {'skipped' if text.startswith('Not written') else 'written'}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="write the tables from the fits under <results>/units/")
    p.add_argument("--results", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results"))
    p.add_argument("--notebook", default=None)
    p.add_argument("--recompute", action="store_true", help="recompute the per-draw columns from the saved draws first")
    a = p.parse_args(argv)
    if a.recompute:
        print(f"recomputed {recompute(a.results)} fits from their saved draws")
    write_all(a.results, a.notebook)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
