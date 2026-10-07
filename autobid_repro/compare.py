"""python -m autobid_repro.compare [--results results]

Every PLA estimate this package produces beside the original study's, per seed, from results/fits.csv and the
original values exported to results/reference/. Writes results/comparison.md: the hand-written findings in
results/reference/notes.md, then the generated tables. Reads nothing but those files and the fits' saved draws.

The original fits report the plug-in returns only, so every comparison with them, and the second-seed spread they
are measured against, is on the plug-in (plugin_avg, plugin_marg). The estimand section sets the per-draw returns,
which the tables now report, beside the plug-in and Meridian's own ROI.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from . import fit, generator, report

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 0.015
SECOND_SAMPLER_SEED = 101
TABLE1_CONFIGS = ("arm1", "arm2a", "step1")
UNCALIBRATED = ("mechanisms", "knots", "strength")
KEY = ["row", "seed", "config"]


def rel(a, b):
    return a / b - 1


def e(v) -> str:
    return "n/a" if pd.isna(v) else f"{v:+.2e}"


def g4(v) -> str:
    return "n/a" if pd.isna(v) else f"{v:.4f}"


def md(header, rows) -> str:
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
                     + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]) + "\n"


def plug(d: pd.DataFrame) -> pd.DataFrame:
    """The plug-in returns under the names the original's columns use (est_avg, est_marg)."""
    d = d.copy()
    if "plugin_avg" in d:
        d["est_avg"], d["est_marg"] = d["plugin_avg"], d["plugin_marg"]
    return d


def merged(results: str) -> pd.DataFrame:
    here = plug(pd.read_csv(os.path.join(results, "fits.csv")))
    ref = pd.read_csv(os.path.join(results, "reference", "fits.csv"))
    m = ref[ref["channel"] == "pla"].merge(here[here["channel"] == "pla"], on=KEY, how="left", suffixes=("_ref", ""))
    m["d_avg"] = rel(m["est_avg"], m["est_avg_ref"])
    m["d_marg"] = rel(m["est_marg"], m["est_marg_ref"])
    m["d_true_avg"] = rel(m["true_avg"], m["true_avg_ref"])
    m["worst"] = m[["d_avg", "d_marg"]].abs().max(axis=1)
    return m


def summary(m: pd.DataFrame) -> str:
    rows = []
    for name, g in m.groupby("set", sort=False):
        both = g[g["converged"] & g["converged_ref"]]
        rows.append([name, len(g), int(g["est_avg"].notna().sum()), int((g["converged"] == g["converged_ref"]).sum()),
                     len(both), f"{both['d_avg'].abs().max():.2e}", f"{both['d_marg'].abs().max():.2e}",
                     int((both["worst"] > TOL).sum()), f"{g['d_true_avg'].abs().max():.1e}"])
    return md(["result", "PLA cells", "fitted here", "convergence flag agrees", "converged on both sides",
               "max abs rel diff avg", "max abs rel diff marg", f"beyond {TOL:.1%}", "max abs rel diff, true avg"], rows)


def cells(m: pd.DataFrame) -> str:
    rows = []
    for x in m.sort_values(["set", "config", "row", "seed"]).itertuples():
        flag = "" if not (x.converged and x.converged_ref) else ("**beyond**" if x.worst > TOL else "")
        rows.append([x.set, x.config, x.row, x.seed, f"{x.converged}/{x.converged_ref}",
                     f"{x.max_rhat:.3f}/{x.max_rhat_ref:.3f}", g4(x.est_avg), g4(x.est_avg_ref), e(x.d_avg),
                     g4(x.est_marg), g4(x.est_marg_ref), e(x.d_marg), flag])
    return md(["result", "config", "row", "seed", "converged here/original", "max R-hat here/original", "avg here",
               "avg original", "rel diff", "marg here", "marg original", "rel diff", ""], rows)


def calibrated(results: str, m: pd.DataFrame) -> str:
    L = pd.read_csv(os.path.join(results, "learnings.csv"))
    R = pd.read_csv(os.path.join(results, "reference", "learnings.csv"))
    R["lo"], R["hi"] = R[["iroas_lo", "iroas_hi"]].min(axis=1), R[["iroas_lo", "iroas_hi"]].max(axis=1)
    lr = L.merge(R, on=["row", "seed", "level"], suffixes=("", "_ref"))
    out = ["The experiments, here and original. Max abs difference over the 20: "
           + ", ".join(f"{c} {np.abs(lr[c] - lr[c + '_ref']).max():.1e}" for c in
                       ("effect", "se", "true_effect", "incremental_spend", "iroas", "prior_loc", "prior_scale"))
           + f", iROAS interval {max(np.abs(lr['iroas_lo'] - lr['lo']).max(), np.abs(lr['iroas_hi'] - lr['hi']).max()):.1e}.\n",
           md(["row", "seed", "level", "iROAS [95%] here", "iROAS [95%] original", "prior loc, scale here",
               "prior loc, scale original"],
              [[x.row, x.seed, x.level, f"{x.iroas:.4f} [{x.iroas_lo:.4f}, {x.iroas_hi:.4f}]",
                f"{x.iroas_ref:.4f} [{x.lo:.4f}, {x.hi:.4f}]", f"{x.prior_loc:.4f}, {x.prior_scale:.4f}",
                f"{x.prior_loc_ref:.4f}, {x.prior_scale_ref:.4f}"] for x in lr.itertuples()])]
    c = m[m["set"] == "calibration"].copy()
    c["level"] = c["config"].str.split("_").str[1]
    c = c.drop(columns=[x for x in c.columns if x.startswith("iroas")])
    c = c.merge(L[["row", "seed", "level", "iroas"]], on=["row", "seed", "level"], how="left")
    out.append("\nThe calibrated PLA estimates beside the experiment that set their prior.\n\n" + md(
        ["config", "row", "seed", "experiment iROAS", "avg here", "avg original", "rel diff", "marg here",
         "marg original", "rel diff", "converged here/original"],
        [[x.config, x.row, x.seed, f"{x.iroas:.4f}", g4(x.est_avg), g4(x.est_avg_ref), e(x.d_avg), g4(x.est_marg),
          g4(x.est_marg_ref), e(x.d_marg), f"{x.converged}/{x.converged_ref}"]
         for x in c.sort_values(["config", "row", "seed"]).itertuples()]))
    return "\n".join(out)


def baseline(results: str) -> str:
    here = pd.read_csv(os.path.join(results, "baseline_metrics.csv"))
    ref = pd.read_csv(os.path.join(results, "reference", "baseline.csv"))
    cols = ["corr_baseline_truth", "rmse", "corr_resid_pla_spend", "resid_share_of_pla", "pla_fit_over_true"]
    m = ref.merge(here, on=KEY + ["window"], suffixes=("_ref", ""))
    rows = []
    for (config, row), g in m.groupby(["config", "row"]):
        rows.append([config, row, len(g)] + [f"{np.abs(g[c] - g[c + '_ref']).max():.1e}" for c in cols])
    return ("Max absolute difference per configuration and row, over seeds and both windows (all weeks, training "
            "weeks; the calibrated rows are all weeks only).\n\n"
            + md(["config", "row", "seed-windows"] + cols, rows))


def seeds_section(results: str) -> str:
    """The second sampler seed changes the sampling and nothing else: the instance each fit read is the same."""
    d2 = os.path.join(results, f"sampler_seed_{SECOND_SAMPLER_SEED}")
    f2 = pd.read_csv(os.path.join(d2, "fits.csv"))
    main = pd.read_csv(os.path.join(results, "fits.csv"))
    pairs = sorted(set(zip(f2["row"], f2["seed"])) | set(zip(main["row"], main["seed"])))
    hashes = {(r, s): __import__("hashlib").sha256(generator.frame(r, int(s)).to_csv(index=False).encode()).hexdigest()
              for r, s in pairs}
    hash_ok = all(hashes[(x.row, x.seed)] == x.instance_sha256 for x in f2.itertuples())
    main_hash_ok = all(hashes[(x.row, x.seed)] == x.instance_sha256 for x in main.itertuples())
    main_seeds = sorted(main["sampler_seed"].dropna().astype(int).unique().tolist())
    cols = ["week", "revenue", "truth_nonmarketing", "truth_pla_effect", "pla_spend"]
    series_ok, n = True, 0
    for x in f2[f2["channel"] == "pla"].itertuples():
        a = report.load_series(results, x.row, x.seed, x.config)
        b = report.load_series(d2, x.row, x.seed, x.config)
        series_ok &= bool(a[cols].equals(b[cols]))
        n += 1
    m = main.merge(f2, on=["row", "seed", "config", "channel"], suffixes=("", "_2"))
    truth_ok = all((m[c] == m[c + "_2"]).all() for c in ("true_avg", "true_marg", "mean_weekly_spend"))
    return (f"The data seed is the generator's master seed: it fixes an instance (20260908 to 20260912). The sampler "
            f"seed seeds Meridian's prior and posterior sampling. The main run uses sampler seed {fit.SAMPLER_SEED} for "
            f"every fit: a fixed constant, not derived from the instance, numerically equal to the first data seed "
            f"because the original study chose it that way. The second-seed check refits the mechanisms set "
            f"({len(f2) // 3} fits) at sampler seed {SECOND_SAMPLER_SEED}, chosen so it cannot be mistaken for a "
            f"data seed (`python -m autobid_repro --sets mechanisms --sampler-seed {SECOND_SAMPLER_SEED}`, into "
            f"`results/sampler_seed_{SECOND_SAMPLER_SEED}/`).\n\n"
            f"Only the sampler seed changes:\n\n"
            f"- sampler seed recorded on every second-seed fit: {sorted(f2['sampler_seed'].unique().tolist())};\n"
            f"- sha256 of the generated instance (its full frame as CSV), recorded at fit time, equal to the instance "
            f"regenerated now for all {len(pairs)} (row, data seed) pairs: {hash_ok};\n"
            f"- weekly revenue, PLA spend, true non-marketing sales and true PLA effect, as written by each fit, "
            f"identical between the main and second-seed fits on all {n}: {series_ok};\n"
            f"- true average and marginal return and mean weekly spend identical on every channel row: {truth_ok};\n"
            f"- sampler seed recorded on every main-run fit: {main_seeds}; its instance hash equal to the instance "
            f"regenerated now on all {len(main) // 3}: {main_hash_ok}.\n")


def table1(results: str) -> str:
    """The note's Table 1 (PLA by row and configuration, medians of converged seeds, four-of-five sign rule) here,
    original and at the second sampler seed."""
    here = plug(pd.read_csv(os.path.join(results, "fits.csv")))
    ref = pd.read_csv(os.path.join(results, "reference", "fits.csv"))
    two = plug(pd.read_csv(os.path.join(results, f"sampler_seed_{SECOND_SAMPLER_SEED}", "fits.csv")))
    ref = ref[ref["set"] == "mechanisms"]
    pick = lambda d, r, c: d[(d["row"] == r) & (d["config"] == c) & (d["channel"] == "pla")]
    rows, flags = [], {"median": 0, "sign": 0, "scored": 0, "cells": 0}
    for c in TABLE1_CONFIGS:
        for r in report.MECHANISM_ROWS:
            h, o, t = pick(here, r, c), pick(ref, r, c), pick(two, r, c)
            out = [report.ARM_NAMES[c], r]
            moved = []
            for col in ("est_avg", "est_marg"):
                mh, mo, mt = report.med(h, col), report.med(o, col), report.med(t, col)
                spread = abs(mt - mh)
                beyond = abs(mh - mo) > spread
                moved.append(beyond)
                out += [f"{mh:.2f}", f"{mo:.2f}", f"{spread:.2f}", "yes" if beyond else "no"]
            sh, so = report.sign(h), report.sign(o)
            nh, no = int(h["converged"].sum()), int(o["converged"].sum())
            out += [sh, so, report.sign(t), "yes" if sh != so else "no", f"{nh}/{no}", "yes" if nh != no else "no"]
            flags["cells"] += 1
            flags["median"] += any(moved)
            flags["sign"] += sh != so
            flags["scored"] += nh != no
            rows.append(out)
    head = ["config", "row", "avg here", "avg original", f"avg spread (seed {SECOND_SAMPLER_SEED})",
            "avg moves beyond spread", "marg here", "marg original", f"marg spread (seed {SECOND_SAMPLER_SEED})",
            "marg moves beyond spread", "sign here", "sign original", f"sign at seed {SECOND_SAMPLER_SEED}",
            "sign changes", "scored here/original", "scored count changes"]
    return (f"Medians over converged seeds of PLA's plug-in average and marginal return. Spread is |median at sampler seed "
            f"{SECOND_SAMPLER_SEED} - median at sampler seed {fit.SAMPLER_SEED}|, both on this package's input: how far "
            f"the median moves when nothing changes but the sampler's seed. A median moves beyond the spread when "
            f"|here - original| exceeds it. Sign changes when its label or count differs.\n\n"
            f"Of {flags['cells']} cells: a median (average or marginal) moves beyond the spread in {flags['median']}; "
            f"the sign label or count changes in {flags['sign']}; the scored-seed count changes in {flags['scored']}.\n\n"
            + md(head, rows))


def convergence(m: pd.DataFrame) -> str:
    x = m[m["converged"] != m["converged_ref"]].sort_values(["set", "config", "row", "seed"])
    return (f"{len(x)} fits whose convergence flag differs ({', '.join(f'{k} {v}' for k, v in x.groupby('set', sort=False).size().items())}). "
            f"A fit converges when max R-hat is at most {fit.RHAT_MAX} and min bulk ESS at least {fit.ESS_MIN}.\n\n"
            + md(["result", "config", "row", "seed", "converged here", "max R-hat here", "min bulk ESS here",
                  "converged original", "max R-hat original", "min bulk ESS original"],
                 [[r.set, r.config, r.row, r.seed, r.converged, f"{r.max_rhat:.3f}", f"{r.min_ess_bulk:.0f}",
                   r.converged_ref, f"{r.max_rhat_ref:.3f}", f"{r.min_ess_bulk_ref:.0f}"] for r in x.itertuples()]))


# ---- the cells of the note's tables ----------------------------------------------------------------------------
# Table 1 mechanisms, 2 baseline decomposition, 3 knot sweep, 4 strength, 5 calibration: (table, config, row) cells.
STRICT_RHAT = 1.01
TABLES = {
    "1 mechanisms": [(c, r) for c in TABLE1_CONFIGS for r in report.MECHANISM_ROWS],
    "2 baseline": [(c, r) for c in TABLE1_CONFIGS for r in report.TWO_ROWS],
    "3 knots": [(c, r) for c in ("arm1", "knots4", "knots13", "knots26", "knots52", "arm2a") for r in report.TWO_ROWS],
    "4 strength": [(c, r) for c in ("arm1", "arm2a") for r in report.STRENGTH],
    "5 calibration": [(a + lv, r) for a in ("arm1", "arm2a") for lv in ("", "_weak", "_strong") for r in report.TWO_ROWS],
}


def path_per_draw(results: str, x) -> float:
    """Median over the saved draws of PLA's Hill curve averaged over the realized weekly spend path,
    sum_t f_d(x_t) / sum_t x_t: Meridian's ROI without adstock carryover or the lag window."""
    spend = report.load_series(results, x.row, x.seed, x.config)["pla_spend"].to_numpy(float)
    with np.load(os.path.join(results, "units", f"{x.row}__{x.seed}__{x.config}.draws.npz")) as d:
        d = dict(d)
    j = list(d["channels"]).index("pla")
    cap = d["population_scaled_stdev"] * np.einsum("dgm,g->dm", d["beta_gm"], d["population"])[:, j]
    k = d["population"].sum() * d["media_median"][j] * d["ec_m"][:, j]
    f = fit.hill(spend[None, :], cap[:, None], k[:, None], d["slope_m"][:, j][:, None])
    return float(np.median(f.sum(axis=1) / spend.sum()))


AGREE = 0.10


def estimand(results: str) -> str:
    f = pd.read_csv(os.path.join(results, "fits.csv"))
    f = f[f["channel"] == "pla"].copy()
    f["path_avg"] = [path_per_draw(results, x) for x in f.itertuples()]
    f["avg_over_plugin"] = f["est_avg"] / f["plugin_avg"]
    f["marg_over_plugin"] = f["est_marg"] / f["plugin_marg"]
    f["roi_over_avg"] = f["meridian_roi_median"] / f["est_avg"]
    f["roi_over_plugin"] = f["meridian_roi_median"] / f["plugin_avg"]
    f["path_factor"] = f["path_avg"] / f["est_avg"]
    f["rest_factor"] = f["meridian_roi_median"] / f["path_avg"]
    f[["row", "seed", "config", "converged", "plugin_avg", "est_avg", "all_avg_median", "avg_lo", "avg_hi",
       "plugin_marg", "est_marg", "all_marg_median",
       "meridian_roi_median", "meridian_roi_lo", "meridian_roi_hi", "meridian_roi", "path_avg", "avg_over_plugin",
       "marg_over_plugin", "roi_over_avg", "roi_over_plugin", "path_factor", "rest_factor"]].sort_values(
        ["config", "row", "seed"]).to_csv(os.path.join(results, "estimand_check.csv"), index=False)
    rows, off, off_plug, seen = [], [], [], set()
    for table, cellset in TABLES.items():
        for c, r in cellset:
            g = f[(f["config"] == c) & (f["row"] == r) & f["converged"]]
            if g.empty:
                continue
            pa, da, pm, dm, ro = (g[col].median() for col in
                                  ("plugin_avg", "est_avg", "plugin_marg", "est_marg", "meridian_roi_median"))
            ok, ok_plug = abs(ro / da - 1) <= AGREE, abs(ro / pa - 1) <= AGREE
            if (c, r) not in seen:
                seen.add((c, r))
                off += [] if ok else [f"{c} {r}"]
                off_plug += [] if ok_plug else [f"{c} {r}"]
            rows.append([table, c, r, len(g), f"{pa:.2f}", f"{da:.2f}", f"{da / pa:.3f}",
                         f"{g['avg_over_plugin'].min():.3f} to {g['avg_over_plugin'].max():.3f}", f"{pm:.2f}",
                         f"{dm:.2f}", f"{dm / pm:.3f}", f"{ro:.2f}", f"{ro / da:.3f}",
                         f"{g['roi_over_avg'].min():.3f} to {g['roi_over_avg'].max():.3f}", f"{ro / pa:.3f}",
                         f"{g['path_factor'].median():.3f}", f"{g['rest_factor'].median():.3f}",
                         "yes" if ok else "**no**", f"{g['meridian_roi'].median():.2f}",
                         f"{g['meridian_roi'].median() / pa:.3f}", f"{g['all_avg_median'].median():.2f}",
                         f"{g['all_avg_median'].median() / da:.3f}"])
    allc = f[f["converged"]]
    return ("Each fit's average and marginal return is now the posterior median of the per-draw return over its 1,000 "
            "saved draws; the plug-in, the curve at posterior-mean cap and posterior-median k and s (the earlier "
            "estimand and the original's), is kept beside it. Meridian's ROI is `Analyzer.roi()` per draw: the "
            "channel's incremental outcome over all 156 weeks of the actual spend path, with adstock carryover, on the "
            "revenue scale, over its total spend; its posterior median over the same saved draws. *Path* is the "
            "per-draw Hill curve averaged over the realized weekly spend instead of evaluated at the mean spend "
            "(posterior median), and splits Meridian's ROI over the per-draw average into path / per-draw average "
            "(window and curvature) and ROI / path (adstock, the lag window). Medians over converged seeds; ratios of "
            f"those medians, per-seed ranges of the per-fit ratio. The per-draw average agrees with Meridian's ROI "
            f"when the ratio of medians is within {AGREE:.0%} of 1. The last two columns give the same per-draw median over "
            "every kept draw (20,000 per fit) instead of the 1,000 saved: the saved draws carry more Monte Carlo error "
            "in the median (a few percent on the wide cells), which the long-chain test sizes. Per-fit values: "
            "`results/estimand_check.csv`.\n\n"
            f"Over all {len(allc)} converged fits: per-draw over plug-in average {allc['avg_over_plugin'].min():.3f} to "
            f"{allc['avg_over_plugin'].max():.3f} (median {allc['avg_over_plugin'].median():.3f}), marginal "
            f"{allc['marg_over_plugin'].min():.3f} to {allc['marg_over_plugin'].max():.3f} (median "
            f"{allc['marg_over_plugin'].median():.3f}); Meridian's ROI over the per-draw average "
            f"{allc['roi_over_avg'].min():.3f} to {allc['roi_over_avg'].max():.3f} (median "
            f"{allc['roi_over_avg'].median():.3f}), over the plug-in {allc['roi_over_plugin'].min():.3f} to "
            f"{allc['roi_over_plugin'].max():.3f}. Meridian's posterior-mean ROI over the plug-in "
            f"{(allc['meridian_roi'] / allc['plugin_avg']).min():.3f} to {(allc['meridian_roi'] / allc['plugin_avg']).max():.3f} "
            f"(median {(allc['meridian_roi'] / allc['plugin_avg']).median():.3f}): the per-draw distribution is right-skewed, "
            "so its median sits below its mean, and the plug-in, built on the posterior-mean cap, tracks the mean.\n\n"
            f"Configuration and row cells where Meridian's ROI is more than {AGREE:.0%} from the per-draw average: "
            f"{len(off)} of {len(seen)}{': ' + '; '.join(off) if off else ''}. From the plug-in: {len(off_plug)} of "
            f"{len(seen)}{': ' + '; '.join(off_plug) if off_plug else ''}.\n\n"
            + md(["table", "config", "row", "converged seeds", "plug-in avg", "per-draw avg", "per-draw / plug-in",
                  "per-seed", "plug-in marg", "per-draw marg", "per-draw / plug-in, marg", "Meridian ROI",
                  "ROI / per-draw avg", "per-seed", "ROI / plug-in avg", "path factor", "rest factor",
                  "ROI agrees with per-draw avg", "Meridian ROI, posterior mean", "ROI mean / plug-in avg",
                  "per-draw avg, every kept draw", "every kept draw / saved draws"], rows)
            + "\n### Per-draw 90 percent intervals of PLA's returns, every fit\n\n"
            "5th to 95th percentile of the per-draw return over the fit's saved draws, and whether it contains the "
            "generator's true value. Every fit, converged or not (the tables count converged fits only).\n\n"
            + intervals(f))


def contains(lo, hi, v) -> str:
    return "yes" if lo <= v <= hi else "**no**"


def intervals(f: pd.DataFrame) -> str:
    rows = []
    for x in f.sort_values(["config", "row", "seed"]).itertuples():
        rows.append([x.config, x.row, x.seed, "yes" if x.converged else "no", f"{x.true_avg:.2f}",
                     f"{x.est_avg:.2f} [{x.avg_lo:.2f}, {x.avg_hi:.2f}]", contains(x.avg_lo, x.avg_hi, x.true_avg),
                     f"{x.true_marg:.2f}", f"{x.est_marg:.2f} [{x.marg_lo:.2f}, {x.marg_hi:.2f}]",
                     contains(x.marg_lo, x.marg_hi, x.true_marg)])
    return md(["config", "row", "data seed", "converged", "true avg", "per-draw avg [90%]", "contains true avg",
               "true marg", "per-draw marg [90%]", "contains true marg"], rows)


def prior_section(results: str) -> str:
    """Every uncalibrated cell against the default ROI prior, and PLA's half-saturation k against its prior."""
    f = pd.read_csv(os.path.join(results, "fits.csv"))
    seen = list(dict.fromkeys((c, r) for cs in TABLES.values() for c, r in cs))
    return ("### PLA's return against the default ROI prior\n\n" + report.prior_table(f, seen)
            + "\n### PLA's half-saturation k against its prior\n\n" + half_saturation(results, f))


K_CELLS = [("arm2a", r) for r in report.MECHANISM_ROWS + ("performance_chasing_0p2", "performance_chasing_0p4")] + [
    ("arm1", "none")] + [(a + lv, r) for a in ("arm1", "arm2a") for lv in ("_weak", "_strong") for r in report.TWO_ROWS]


def half_saturation(results: str, f: pd.DataFrame) -> str:
    """k = sum(population) x media median x ec_m, so its prior is ec_m's, rescaled per instance with the fit's own
    saved constants."""
    import warnings
    warnings.filterwarnings("ignore")
    from scipy import stats
    j = fit.CHANNELS.index("pla")
    L = pd.read_csv(os.path.join(results, "learnings.csv"))
    rows, per_fit, ec_params = [], [], set()
    for c, r in K_CELLS:
        g = f[(f["config"] == c) & (f["row"] == r) & (f["channel"] == "pla")].sort_values("seed")
        vals = []
        for x in g.itertuples():
            # the specification this fit used; a calibrated one carries its own experiment's ROI prior on PLA
            _, level = fit.split(c)
            learning = (L[(L["row"] == r) & (L["seed"] == x.seed) & (L["level"] == level)].iloc[0].to_dict()
                        if level else None)
            ec = fit.model_spec(c, 156, learning).prior.ec_m
            loc, scale, lo, hi = (float(np.ravel(ec.parameters[k])[0]) for k in ("loc", "scale", "low", "high"))
            ec_params.add((loc, scale, lo, hi))
            tn = stats.truncnorm((lo - loc) / scale, (hi - loc) / scale, loc=loc, scale=scale)
            with np.load(os.path.join(results, "units", f"{x.row}__{x.seed}__{x.config}.draws.npz")) as d:
                d = dict(d)
            scale_k = float(d["population"].sum() * d["media_median"][j])
            kd = scale_k * d["ec_m"][:, j]
            prior_q = scale_k * tn.ppf([0.05, 0.5, 0.95])
            post = np.percentile(kd, [5, 50, 95])
            v = {"converged": x.converged, "x": x.mean_weekly_spend, "prior": prior_q, "post": post, "k_all": x.k,
                 "ratio": post[1] / prior_q[1], "width": (post[2] - post[0]) / (prior_q[2] - prior_q[0])}
            vals.append(v)
            per_fit.append([c, r, x.seed, "yes" if x.converged else "no", f"{x.mean_weekly_spend:.1f}",
                            f"{prior_q[1]:.1f} [{prior_q[0]:.1f}, {prior_q[2]:.1f}]",
                            f"{post[1]:.1f} [{post[0]:.1f}, {post[2]:.1f}]", f"{x.k:.1f}", f"{v['ratio']:.2f}",
                            f"{v['width']:.2f}", f"{x.mean_weekly_spend / post[1]:.2f}"])
        conv = [v for v in vals if v["converged"]]
        med = lambda key, i=None: np.median([v[key] if i is None else v[key][i] for v in conv])
        rows.append([c, r, f"{len(conv)}/{len(vals)}", f"{med('x'):.1f}",
                     f"{med('prior', 1):.1f} [{med('prior', 0):.1f}, {med('prior', 2):.1f}]",
                     f"{med('post', 1):.1f} [{med('post', 0):.1f}, {med('post', 2):.1f}]", f"{med('ratio'):.2f}",
                     f"{med('width'):.2f}", f"{np.median([v['x'] / v['post'][1] for v in conv]):.2f}"])
    if len(ec_params) != 1:
        raise RuntimeError(f"the fits do not share one ec_m prior: {sorted(ec_params)}")
    return (f"Meridian's half-saturation for PLA is k = sum(population) x PLA's media median x ec_m, with ec_m ~ "
            f"TruncatedNormal({loc:g}, {scale:g}) on [{lo:g}, {hi:g}] (Meridian 2.0.0's default, read from the fitted "
            "model specification of every fit listed, the calibrated ones included: calibration replaces only PLA's ROI "
            "prior), so k's prior is ec_m's prior rescaled by each instance's own constants. Prior: median "
            "[5th, 95th percentile]. Posterior: the same over the fit's saved draws; `k` in `fits.csv`, the posterior "
            "median over every kept draw, beside it. x is PLA's mean weekly spend, the point the returns are read at. "
            "Per cell, medians over converged seeds.\n\n"
            + md(["config", "row", "converged", "mean weekly spend x", "prior k [90%]", "posterior k [90%]",
                  "posterior / prior median", "width / prior width", "x / posterior k"], rows)
            + "\nPer fit, converged or not:\n\n"
            + md(["config", "row", "data seed", "converged", "x", "prior k [90%]", "posterior k [90%]",
                  "posterior k, every kept draw", "posterior / prior median", "width / prior width", "x / posterior k"],
                 per_fit))


def strict_gate(fits: pd.DataFrame) -> pd.DataFrame:
    f = fits.copy()
    f["converged"] = (f["max_rhat"] <= STRICT_RHAT) & (f["min_ess_bulk"] >= fit.ESS_MIN)
    return f


def strict_tables(results: str, notebook_path=None) -> None:
    """The five tables rewritten under the strict gate, to results/tables/strict/."""
    fits = strict_gate(pd.read_csv(os.path.join(results, "fits.csv")))
    bm = pd.read_csv(os.path.join(results, "baseline_metrics.csv"))
    ok = set(zip(*fits[fits["converged"]][["row", "seed", "config"]].T.values))
    bm = bm[[k in ok for k in zip(bm["row"], bm["seed"], bm["config"])]].copy()
    bm["converged"] = True
    L = pd.read_csv(os.path.join(results, "learnings.csv"))
    out = os.path.join(results, "tables", "strict")
    os.makedirs(out, exist_ok=True)
    note = (f"Strict gate: only fits with max R-hat at most {STRICT_RHAT} and min bulk ESS at least {fit.ESS_MIN}; a "
            f"fit that fails it is nc and, in the baseline tables, left out.\n\n")
    for name, text in {"mechanisms": report.mechanisms(fits), "baseline": report.baseline(fits, bm),
                       "knots": report.knots(fits, bm), "strength": report.strength(fits, notebook_path),
                       "calibration": report.calibration(fits, bm, L)}.items():
        with open(os.path.join(out, f"{name}.md"), "w") as fh:
            fh.write(f"# {name.capitalize()}, strict gate\n\n{note}{text}")


def gates(results: str) -> str:
    loose = pd.read_csv(os.path.join(results, "fits.csv"))
    loose = loose[loose["channel"] == "pla"]
    tight = strict_gate(loose)
    bm = pd.read_csv(os.path.join(results, "baseline_metrics.csv"))
    bm = bm[bm["window"] == "all"]
    rows, changed = [], []
    for table, cellset in TABLES.items():
        for c, r in cellset:
            a = loose[(loose["config"] == c) & (loose["row"] == r)]
            b = tight[(tight["config"] == c) & (tight["row"] == r)]
            na, nb = int(a["converged"].sum()), int(b["converged"].sum())
            if table == "2 baseline":
                keep = lambda g: bm[(bm["config"] == c) & (bm["row"] == r)
                                    & bm["seed"].isin(g[g["converged"]]["seed"])]
                ka, kb = keep(a), keep(b)
                va = [ka[m].median() for m in ("corr_baseline_truth", "corr_resid_pla_spend", "resid_share_of_pla")]
                vb = [kb[m].median() for m in ("corr_baseline_truth", "corr_resid_pla_spend", "resid_share_of_pla")]
                cells = [f"{x:.2f} / {y:.2f}" for x, y in zip(va, vb)] + [""]
                diff = [f"{x:.2f}" != f"{y:.2f}" for x, y in zip(va, vb)]
            else:
                va = [report.med(a, "est_avg"), report.med(a, "est_marg")]
                vb = [report.med(b, "est_avg"), report.med(b, "est_marg")]
                sa, sb = report.sign(a), report.sign(b)
                cells = [f"{report.f2(va[0])} / {report.f2(vb[0])}", f"{report.f2(va[1])} / {report.f2(vb[1])}", "",
                         f"{sa} / {sb}"]
                diff = [report.f2(x) != report.f2(y) for x, y in zip(va, vb)] + [sa != sb]
            ch = na != nb or any(diff)
            if ch:
                changed.append(f"{table} {c} {r}")
            rows.append([table, c, r, na, nb] + cells + ["**yes**" if ch else "no"])
    dist = []
    for c in sorted(loose["config"].unique()):
        for r in sorted(loose["row"].unique()):
            g = loose[(loose["config"] == c) & (loose["row"] == r) & loose["converged"]]
            if g.empty:
                continue
            q = g["max_rhat"]
            dist.append([c, r, len(g), f"{q.min():.4f}", f"{q.median():.4f}", f"{q.max():.4f}",
                         int((q <= STRICT_RHAT).sum()), int((g["min_ess_bulk"] < fit.ESS_MIN).sum())])
    return (f"Every table recomputed with only the fits whose max R-hat is at most {STRICT_RHAT} (and min bulk ESS at "
            f"least {fit.ESS_MIN}), beside the note's gate of {fit.RHAT_MAX}. The strict tables are in "
            f"`results/tables/strict/`. Each pair is the note's gate / strict; a cell changes when the count kept, a median "
            f"at two decimals, or the sign label or count differs. Changed cells: {len(changed)} of "
            f"{sum(len(v) for v in TABLES.values())}.\n\n"
            + md(["table", "config", "row", "kept at 1.1", f"kept at {STRICT_RHAT}",
                  "avg median (table 2: corr(baseline, truth))", "marg median (table 2: corr(residual, PLA spend))",
                  "table 2: residual share", "sign", "changes"], rows)
            + f"\nMax R-hat of the fits that pass the note's gate, per configuration and row:\n\n"
            + md(["config", "row", "fits passing 1.1", "min", "median", "max", f"at or below {STRICT_RHAT}",
                  "ESS below 400"], dist))


def write(results: str) -> str:
    m = merged(results)
    strict_tables(results)
    notes_path = os.path.join(results, "reference", "notes.md")
    notes = open(notes_path).read() if os.path.exists(notes_path) else ""
    text = ("# Agreement with the original fits\n\n" + notes +
            "\n## Data seed and sampler seed\n\n" + seeds_section(results) +
            "\n## Summary, PLA\n\nRelative differences are this package's estimate over the original's, less one, on "
            "fits that converged on both sides.\n\n" + summary(m) +
            "\n## Table 1 of the note, recomputed\n\n" + table1(results) +
            "\n## Fits whose convergence flag differs\n\n" + convergence(m) +
            "\n## Estimand: per-draw returns, plug-in returns and Meridian's ROI\n\n" + estimand(results) +
            "\n## Uncalibrated cells against their priors\n\n" + prior_section(results) +
            "\n## Strict convergence gate\n\n" + gates(results) +
            "\n## Calibration\n\n" + calibrated(results, m) +
            "\n## Weekly baseline decomposition\n\n" + baseline(results) +
            "\n## Every PLA cell\n\n" + cells(m))
    with open(os.path.join(results, "comparison.md"), "w") as f:
        f.write(text)
    return text


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="this package's PLA estimates beside the original study's")
    p.add_argument("--results", default=os.path.join(HERE, "results"))
    a = p.parse_args(argv)
    m = merged(a.results)
    write(a.results)
    print(summary(m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
