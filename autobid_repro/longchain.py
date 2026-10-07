"""The long-chain test: the fits whose results moved under a tiny input change or another sampler seed, refitted
with far longer chains at two sampler seeds.

    python -m autobid_repro.longchain --units     print the fragile fits as a comma-separated --only list
    python -m autobid_repro.longchain             write results/longchain/longchain.{md,csv} from the fits

The fragile fits, from the saved results alone (main run, second sampler seed, original fits), on the plug-in
average and marginal return that the main run and the original report:
  1. every data seed of each Table 1 cell whose median moved beyond the seed-to-seed spread (compare.table1);
  2. every fit whose convergence flag differs between this package and the original;
  3. arm 1 at roi_sensitivity 0.2 and 0.4, every data seed.
Each is refitted on this package's input with LONG sampler settings at sampler seeds 20260908 and 101, into
results/longchain/sampler_seed_<N>/; nothing else changes.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from . import compare, fit, generator, report

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(HERE, "results")
OUT = os.path.join(RESULTS, "longchain")
LONG = {"n_chains": 8, "n_adapt": 4000, "n_burnin": 2000, "n_keep": 20000}
SAMPLER_SEEDS = (fit.SAMPLER_SEED, compare.SECOND_SAMPLER_SEED)
STRENGTH_ROWS = ("performance_chasing_0p2", "performance_chasing_0p4")


def fragile(results: str = RESULTS) -> pd.DataFrame:
    """One row per fragile fit: row, seed, config and the reasons it is on the list."""
    here = compare.plug(pd.read_csv(os.path.join(results, "fits.csv")))
    two = compare.plug(pd.read_csv(os.path.join(results, f"sampler_seed_{compare.SECOND_SAMPLER_SEED}", "fits.csv")))
    ref = pd.read_csv(os.path.join(results, "reference", "fits.csv"))
    pla = lambda d: d[d["channel"] == "pla"]
    why: dict[tuple, list[str]] = {}
    for c in compare.TABLE1_CONFIGS:
        for r in report.MECHANISM_ROWS:
            h, o, t = (d[(d["row"] == r) & (d["config"] == c)] for d in
                       (pla(here), pla(ref[ref["set"] == "mechanisms"]), pla(two)))
            moved = [col for col in ("est_avg", "est_marg")
                     if abs(report.med(h, col) - report.med(o, col)) > abs(report.med(t, col) - report.med(h, col))]
            for s in generator.SEEDS if moved else ():
                why.setdefault((r, s, c), []).append("Table 1 median beyond spread (" + ", ".join(
                    m.replace("est_", "") for m in moved) + ")")
    m = pla(ref).merge(pla(here), on=compare.KEY, suffixes=("_ref", ""))
    for x in m[m["converged"] != m["converged_ref"]].itertuples():
        why.setdefault((x.row, x.seed, x.config), []).append(
            f"convergence flag differs (here {x.converged}, original {x.converged_ref})")
    for r in STRENGTH_ROWS:
        for s in generator.SEEDS:
            why.setdefault((r, s, "arm1"), []).append("arm 1 strength row")
    rows = [{"row": r, "seed": s, "config": c, "reasons": "; ".join(v)} for (r, s, c), v in why.items()]
    order = {c: i for i, c in enumerate(fit.CONFIGS)}
    return (pd.DataFrame(rows).assign(o=lambda d: d["config"].map(order))
            .sort_values(["o", "row", "seed"]).drop(columns="o").reset_index(drop=True))


# ---- the report ------------------------------------------------------------------------------------------------
# Criteria, fixed before any long-chain fit was read:
#  (a) the two sampler seeds agree on a return when |v1 - v2| <= 2 sqrt(se1^2 + se2^2), se the Monte Carlo standard
#      error (median: arviz over every kept draw; plug-in: sd of the per-chain plug-ins / sqrt(chains));
#  (b) all chains agree when the split R-hat of PLA's per-draw average and marginal return over all 16 chains (both
#      seeds, from the saved draws) is at most 1.01;
#  (c) the main run's or the original's plug-in matches the long chains' (the mean of the two seeds) when it is within
#      2 sqrt(se_short^2 + se_long^2), se_short the long-chain error scaled to the main run's 4 x 5,000 draws.
Z, RHAT_AGREE = 2.0, 1.01
SHORT_DRAWS = fit.SAMPLING["n_chains"] * fit.SAMPLING["n_keep"]


def load(seed: int) -> pd.DataFrame:
    d = report.load_fits(os.path.join(OUT, f"sampler_seed_{seed}"))
    return d[d["channel"] == "pla"].set_index(["row", "seed", "config"]) if not d.empty else d


def pooled_rhat(row: str, seed: int, config: str) -> tuple[float, float]:
    """Split R-hat of PLA's per-draw average and marginal return over the chains of both sampler seeds."""
    import arviz as az
    per = []
    for ss in SAMPLER_SEEDS:
        with np.load(os.path.join(OUT, f"sampler_seed_{ss}", "units", f"{row}__{seed}__{config}.draws.npz")) as d:
            d = dict(d)
        cap = d["population_scaled_stdev"] * np.einsum("dgm,g->dm", d["beta_gm"], d["population"])[:, 0]
        k = d["population"].sum() * d["media_median"][0] * d["ec_m"][:, 0]
        a, m = fit.returns_per_draw(cap, k, d["slope_m"][:, 0], float(d["mean_weekly_spend"][0]))
        n = int(d["chain"].max()) + 1
        per.append((a.reshape(n, -1), m.reshape(n, -1)))
    return tuple(float(az.rhat(np.concatenate([p[i] for p in per]))) for i in (0, 1))


def agree(v1, s1, v2, s2) -> bool:
    return bool(abs(v1 - v2) <= Z * np.hypot(s1, s2))


def verdicts(f: pd.DataFrame) -> pd.DataFrame:
    a, b = load(SAMPLER_SEEDS[0]), load(SAMPLER_SEEDS[1])
    main = compare.plug(pd.read_csv(os.path.join(RESULTS, "fits.csv")))
    main = main[main["channel"] == "pla"].set_index(["row", "seed", "config"])
    ref = pd.read_csv(os.path.join(RESULTS, "reference", "fits.csv"))
    ref = ref[ref["channel"] == "pla"].set_index(["row", "seed", "config"])
    scale = np.sqrt(LONG["n_chains"] * LONG["n_keep"] / SHORT_DRAWS)
    rows = []
    for x in f.itertuples():
        key = (x.row, x.seed, x.config)
        if key not in a.index or key not in b.index:
            continue
        p, q = a.loc[key], b.loc[key]
        r_avg, r_marg = pooled_rhat(*key)
        out = {"config": x.config, "row": x.row, "seed": x.seed}
        for tag, v in (("a", p), ("b", q)):
            out.update({f"conv_{tag}": bool(v["converged"]), f"rhat_{tag}": v["max_rhat"], f"ess_{tag}": v["min_ess_bulk"],
                        f"plug_avg_{tag}": v["plugin_avg"], f"plug_marg_{tag}": v["plugin_marg"],
                        f"med_avg_{tag}": v["all_avg_median"], f"med_marg_{tag}": v["all_marg_median"],
                        f"se_plug_avg_{tag}": v["mcse_avg_plugin"], f"se_plug_marg_{tag}": v["mcse_marg_plugin"],
                        f"se_med_avg_{tag}": v["mcse_avg_median"], f"se_med_marg_{tag}": v["mcse_marg_median"],
                        f"roi_{tag}": v["meridian_roi"], f"chains_{tag}": v["chain_avg_median"],
                        f"avg_lo_{tag}": v["avg_lo"], f"avg_hi_{tag}": v["avg_hi"],
                        f"marg_lo_{tag}": v["marg_lo"], f"marg_hi_{tag}": v["marg_hi"],
                        "true_avg": v["true_avg"], "true_marg": v["true_marg"],
                        f"chain_plug_{tag}": v["chain_avg_plugin"], f"rhat_pla_avg_{tag}": v["rhat_avg"]})
        seeds_agree = all(agree(out[f"{e}_{w}_a"], out[f"se_{e}_{w}_a"], out[f"{e}_{w}_b"], out[f"se_{e}_{w}_b"])
                          for e in ("plug", "med") for w in ("avg", "marg"))
        lc = {w: (out[f"plug_{w}_a"] + out[f"plug_{w}_b"]) / 2 for w in ("avg", "marg")}
        se_lc = {w: np.hypot(out[f"se_plug_{w}_a"], out[f"se_plug_{w}_b"]) / 2 for w in ("avg", "marg")}
        se_short = {w: (out[f"se_plug_{w}_a"] + out[f"se_plug_{w}_b"]) / 2 * scale for w in ("avg", "marg")}
        def matches(src):
            if key not in src.index or pd.isna(src.at[key, "est_avg"]):
                return None
            return all(abs(src.at[key, f"est_{w}"] - lc[w]) <= Z * np.hypot(se_short[w], se_lc[w]) for w in ("avg", "marg"))
        mm, mo = matches(main), matches(ref)
        match = ("both" if mm and mo else "main" if mm else "original" if mo else "neither")
        if mo is None:
            match += " (original not converged, no value)"
        out.update({"pooled_rhat_avg": r_avg, "pooled_rhat_marg": r_marg, "lc_avg": lc["avg"], "lc_marg": lc["marg"],
                    "main_avg": main.at[key, "est_avg"], "main_conv": bool(main.at[key, "converged"]),
                    "orig_avg": ref.at[key, "est_avg"] if key in ref.index else np.nan,
                    "orig_conv": bool(ref.at[key, "converged"]) if key in ref.index else None,
                    "seeds_agree": seeds_agree, "chains_agree": bool(max(r_avg, r_marg) <= RHAT_AGREE),
                    "match": match})
        rows.append(out)
    return pd.DataFrame(rows)


def write(f: pd.DataFrame) -> None:
    v = verdicts(f)
    v.to_csv(os.path.join(OUT, "longchain.csv"), index=False)
    yn = lambda b: "yes" if b else "**no**"
    fits = []
    for x in v.itertuples():
        for tag, ss in (("a", SAMPLER_SEEDS[0]), ("b", SAMPLER_SEEDS[1])):
            g = lambda c: getattr(x, f"{c}_{tag}")
            fits.append([x.config, x.row, x.seed, ss, "yes" if g("conv") else "no", f"{g('rhat'):.3f}", f"{g('ess'):.0f}",
                         f"{g('plug_avg'):.3f} ± {g('se_plug_avg'):.3f}", f"{g('plug_marg'):.3f} ± {g('se_plug_marg'):.3f}",
                         f"{g('med_avg'):.3f} ± {g('se_med_avg'):.3f}", f"{g('med_marg'):.3f} ± {g('se_med_marg'):.3f}",
                         f"{g('roi'):.3f}", f"{g('rhat_pla_avg'):.3f}", g("chains").replace(";", ", "),
                         f"[{g('avg_lo'):.2f}, {g('avg_hi'):.2f}]",
                         "yes" if g("avg_lo") <= x.true_avg <= g("avg_hi") else "**no**",
                         f"[{g('marg_lo'):.2f}, {g('marg_hi'):.2f}]",
                         "yes" if g("marg_lo") <= x.true_marg <= g("marg_hi") else "**no**"])
    cells = [[x.config, x.row, x.seed, yn(x.seeds_agree), f"{max(x.pooled_rhat_avg, x.pooled_rhat_marg):.3f}",
              yn(x.chains_agree), f"{x.lc_avg:.3f}", f"{x.main_avg:.3f}" + ("" if x.main_conv else " (nc)"),
              "nc" if pd.isna(x.orig_avg) else f"{x.orig_avg:.3f}" + ("" if x.orig_conv else " (nc)"), x.match]
             for x in v.itertuples()]
    # Table 1 cells: medians over converged seeds, long chains (seed 20260908) beside the main run and the original
    t1 = []
    for (c, r), g in v.groupby(["config", "row"], sort=False):
        if len(g) < len(generator.SEEDS) or r.startswith("performance_chasing_"):
            continue
        med = lambda col, ok: f"{g.loc[g[ok].astype(bool), col].median():.2f} ({int(g[ok].astype(bool).sum())}/5)"
        t1.append([c, r, med("plug_avg_a", "conv_a"), med("plug_avg_b", "conv_b"), med("main_avg", "main_conv"),
                   med("orig_avg", "orig_conv")])
    text = (f"# Long-chain test\n\nEach fragile fit refitted on this package's input with {LONG['n_chains']} chains, "
            f"{LONG['n_adapt']:,} adaptation steps, {LONG['n_burnin']:,} burn-in and {LONG['n_keep']:,} kept draws per "
            f"chain, at sampler seeds {SAMPLER_SEEDS[0]} and {SAMPLER_SEEDS[1]}; nothing else changes and nothing was "
            f"tuned. Generated by `python -m autobid_repro.longchain`.\n\n"
            "Criteria, fixed before any fit was read: (a) the seeds agree when every return (plug-in and per-draw "
            f"median, average and marginal) differs by at most {Z:g} combined Monte Carlo standard errors; (b) the chains "
            f"agree when the split R-hat of PLA's per-draw average and marginal return over all 16 chains of both seeds "
            f"is at most {RHAT_AGREE}; (c) the main run's or the original's plug-in matches when within {Z:g} combined "
            "standard errors of the long chains' (the mean of both seeds), the main run's error taken as the long "
            f"chains' scaled by sqrt({LONG['n_chains'] * LONG['n_keep'] // SHORT_DRAWS}) for its 4 x 5,000 draws.\n\n"
            "## Per fit\n\nValues ± Monte Carlo standard error. Plug-in: the curve at posterior-mean cap, posterior-median "
            "k and s (the estimand of the main run and the original). Per-draw median: over every kept draw. Chain "
            "medians: each chain's median of PLA's per-draw average return. 90%: the 5th to 95th percentile of the "
            "per-draw return over the fit's saved draws, and whether it contains the generator's true value.\n\n"
            + compare.md(["config", "row", "data seed", "sampler seed", "converged", "max R-hat", "min bulk ESS",
                          "PLA avg, plug-in", "PLA marg, plug-in", "PLA avg, per-draw median",
                          "PLA marg, per-draw median", "Meridian ROI (mean)", "R-hat, PLA avg", "chain medians, PLA avg",
                          "PLA avg 90%", "contains true avg", "PLA marg 90%",
                          "contains true marg"],
                         fits)
            + "\n## Per fit, verdicts\n\n"
            + compare.md(["config", "row", "data seed", "(a) seeds agree", "pooled R-hat, PLA returns",
                          "(b) chains agree", "long-chain plug-in avg", "main run", "original", "(c) matches"], cells)
            + "\n## Table 1 cells, PLA average return (plug-in), median over converged seeds\n\n"
            + compare.md(["config", "row", f"long chains, seed {SAMPLER_SEEDS[0]}", f"long chains, seed {SAMPLER_SEEDS[1]}",
                          "main run", "original"], t1))
    with open(os.path.join(OUT, "longchain.md"), "w") as fh:
        fh.write(text)
    print(f"results/longchain/longchain.md: {len(v)} of {len(f)} fragile fits at both seeds")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="the long-chain test of the fragile fits")
    p.add_argument("--units", action="store_true", help="print the fragile fits as an --only list and stop")
    p.add_argument("--list", action="store_true", help="print the fragile fits with their reasons and stop")
    a = p.parse_args(argv)
    f = fragile()
    if a.units:
        print(",".join(f"{x.row}__{x.seed}__{x.config}" for x in f.itertuples()))
        return 0
    if a.list:
        print(compare.md(["config", "row", "data seed", "reasons"],
                         [[x.config, x.row, x.seed, x.reasons] for x in f.itertuples()]))
        return 0
    write(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
