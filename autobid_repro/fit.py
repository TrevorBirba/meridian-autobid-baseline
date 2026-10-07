"""Meridian on one instance's observed set, and the two returns the note reports for each channel.

The model is a single national market: weekly revenue (the generator's total_sales) as the KPI, the three channels'
weekly spend as both media and media spend, and three controls, a linear trend in years since the first week and
one annual sine and cosine on that trend. Population is the mean weekly revenue. The last thirteen weeks are held
out of the likelihood. Sampling is 4 chains, 2,000 adaptation steps, 1,000 burn-in and 5,000 kept draws, after 500
prior draws. The sampler seed seeds Meridian's prior and posterior sampling and is separate from the data seed (the
generator's master seed, which fixes the instance). The main run uses sampler seed 20260908 for every fit: a fixed
constant, not derived from the instance, numerically equal to the first data seed because the original study chose
it that way. `fit(..., sampler_seed=N)` changes it and nothing else.

Configurations, each differing from arm 1 in one place:
  arm1     every optional value at Meridian 2.0.0's default; one time knot on a national panel, Hill slope fixed at 1
  arm2a    the getting-started notebook's example: roi_m LogNormal(0.2, 0.9) stated, automatic knot selection on
  step1    arm 1 with the Hill slope freed under LogNormal(0.7, 0.4)
  knots4, knots13, knots26, knots52   arm 1 with that many time knots
  arm1_weak, arm1_strong, arm2a_weak, arm2a_strong   arm 1 or arm 2a with PLA's ROI prior set from the weak or strong
           go-dark experiment on the same instance (experiment.py); Meta and TV keep LogNormal(0.2, 0.9)

Every fit also writes its weekly decomposition (`series`): Meridian's baseline, the posterior-mean expected outcome
with every media channel at zero and the controls as observed; the expected outcome; each channel's incremental
outcome; beside the generator's true non-marketing sales (base_sales plus promotional_sales_uplift), its true PLA
effect and PLA spend.

Returns. Meridian's media response at a sustained national weekly spend x is
the Hill cap * x^s / (x^s + k^s), with cap = population_scaled_stdev * sum_g beta_gm * P_g,
k = sum(P) * media_median * ec_m and s the slope. Average return is f(x) / x and marginal return f'(x), both at
the channel's observed mean weekly spend over all 156 weeks; f' is a central difference with a step of 1e-4 of x.
Both are computed per posterior draw of (cap, k, s) and reported as the median (est_avg, est_marg) and the 5th to
95th percentile (avg_lo, avg_hi, marg_lo, marg_hi). The draws are a thinned set saved with every fit,
<unit>.draws.npz: THIN_DRAWS draws spread evenly over the chains (the same number from each, evenly spaced within
it) of beta_gm, ec_m and slope_m, with the constants that turn them into cap and k and Meridian's per-draw ROI per
channel. `summarize` computes every per-draw column from that file alone, so a change to the formula is a
recompute (`python -m autobid_repro.report --recompute`), not a refit. Meridian's own ROI, `Analyzer.roi()`: the
posterior mean over every kept draw (meridian_roi), and the median and 5th to 95th percentile over the saved draws.
The earlier plug-in, the curve at posterior-mean cap and posterior-median k and s over every kept draw, is kept as
plugin_avg and plugin_marg.

Monte Carlo diagnostics, over every kept draw, per channel row: the median of the per-draw returns (all_avg_median,
all_marg_median); each chain's median and its plug-in value (chain_*, semicolon-separated in chain order); the split
R-hat of the per-draw returns; the Monte Carlo standard error of their median (arviz, method "median") and of the
plug-in (the standard deviation of the per-chain plug-ins over the square root of the number of chains).

`fit(..., sampling={...})` overrides any of n_chains, n_adapt, n_burnin, n_keep; the defaults are unchanged.
"""

from __future__ import annotations

import hashlib
import time
import warnings

import numpy as np
import pandas as pd

from . import experiment, generator

CHANNELS = ("pla", "meta", "tv")
CONFIGS = ("arm1", "arm2a", "step1", "knots4", "knots13", "knots26", "knots52",
           "arm1_weak", "arm1_strong", "arm2a_weak", "arm2a_strong")
SAMPLING = {"n_chains": 4, "n_adapt": 2000, "n_burnin": 1000, "n_keep": 5000}
PRIOR_DRAWS = 500
SAMPLER_SEED = 20260908
HOLDOUT_WEEKS = 13
MAX_LAG = 8
RHAT_MAX, ESS_MIN = 1.1, 400
THIN_DRAWS = 1000
STEP = 1e-4


def observed(frame: pd.DataFrame) -> pd.DataFrame:
    """The observed columns the model reads, weekly, with Meridian's column conventions and the controls."""
    weeks = pd.Timestamp(generator.START) + pd.to_timedelta(7 * (frame["week"].to_numpy() - 1), unit="D")
    t = ((weeks - weeks.min()).days / 365.25).to_numpy(float)
    df = pd.DataFrame({"geo": "national", "time": weeks.strftime("%Y-%m-%d"),
                       "revenue": frame["total_sales"].to_numpy(float)})
    for c in CHANNELS:
        df[f"spend_{c}"] = frame[f"{c}_spend"].to_numpy(float)
    df["trend"], df["sin_annual"], df["cos_annual"] = t, np.sin(2 * np.pi * t), np.cos(2 * np.pi * t)
    df["population"] = float(df["revenue"].mean())
    return df


def input_data(df: pd.DataFrame):
    from meridian.data import data_frame_input_data_builder as dfb
    cols = [f"spend_{c}" for c in CHANNELS]
    b = dfb.DataFrameInputDataBuilder(kpi_type="revenue", default_geo_column="geo", default_time_column="time",
                                      default_media_time_column="time", default_population_column="population",
                                      default_kpi_column="revenue")
    return (b.with_kpi(df).with_population(df).with_controls(df, control_cols=["trend", "sin_annual", "cos_annual"])
            .with_media(df, media_cols=cols, media_spend_cols=cols, media_channels=list(CHANNELS)).build())


def split(config: str) -> tuple[str, str | None]:
    """'arm1_weak' -> ('arm1', 'weak'); an uncalibrated configuration has no level."""
    base, _, level = config.partition("_")
    return base, (level or None)


def model_spec(config: str, n_times: int, learning: dict | None = None):
    from meridian import backend
    from meridian.model import prior_distribution, spec
    if config not in CONFIGS:
        raise ValueError(f"unknown configuration {config}")
    config, level = split(config)
    hold = np.zeros(n_times, bool)
    hold[-HOLDOUT_WEEKS:] = True
    kw = {"holdout_id": hold, "max_lag": MAX_LAG, "knots": None, "enable_aks": False}
    prior = {}
    f = backend.np_float_dtype
    if config == "arm2a":
        kw["enable_aks"] = True
        prior["roi_m"] = backend.tfd.LogNormal(np.full(len(CHANNELS), 0.2).astype(f), np.full(len(CHANNELS), 0.9).astype(f), name="roi_m")
    if level:
        # The learning replaces arm 2a's stated LogNormal(0.2, 0.9) on PLA alone; at arm 1 it is the only change.
        loc, scale = experiment.roi_prior(learning, CHANNELS)
        prior["roi_m"] = backend.tfd.LogNormal(loc.astype(f), scale.astype(f), name="roi_m")
    if config == "step1":
        prior["slope_m"] = backend.tfd.LogNormal(backend.np_float_dtype(0.7), backend.np_float_dtype(0.4), name="slope_m")
    elif config.startswith("knots"):
        kw["knots"] = int(config[len("knots"):])
    if prior:
        kw["prior"] = prior_distribution.PriorDistribution(**prior)
    return spec.ModelSpec(**kw)


def hill(x, cap, k, s):
    x = np.maximum(np.asarray(x, float), 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return cap * np.where(x > 0, x ** s / (x ** s + k ** s), 0.0)


def returns(cap, k, s, x) -> tuple[float, float]:
    h = x * STEP
    return float(hill(x, cap, k, s) / x), float((hill(x + h, cap, k, s) - hill(x - h, cap, k, s)) / (2 * h))


def returns_per_draw(cap, k, s, x) -> tuple[np.ndarray, np.ndarray]:
    """Average and marginal return at spend x for every draw of (cap, k, s), arrays of the same shape."""
    h = x * STEP
    return hill(x, cap, k, s) / x, (hill(x + h, cap, k, s) - hill(x - h, cap, k, s)) / (2 * h)


def plugin(cap, k, s, x) -> tuple[float, float]:
    """The plug-in returns: the curve at posterior-mean cap and posterior-median k and s."""
    return returns(float(np.mean(cap)), float(np.median(k)), float(np.median(s)), x)


def thin_index(n_chain: int, n_draw: int, n: int = THIN_DRAWS) -> np.ndarray:
    """Flat (chain-major) indices of n draws, n / n_chain from each chain, evenly spaced within it."""
    per = n // n_chain
    within = np.round(np.linspace(0, n_draw - 1, per)).astype(int)
    return (np.arange(n_chain)[:, None] * n_draw + within[None, :]).ravel()


def summarize(d) -> dict[str, dict]:
    """Every per-draw column of one fit, per channel, from its saved draws (a dict or an open .draws.npz)."""
    cap = d["population_scaled_stdev"] * np.einsum("dgm,g->dm", d["beta_gm"], d["population"])
    k = d["population"].sum() * d["media_median"][None, :] * d["ec_m"]
    q = lambda v, p: float(np.percentile(v, p))
    out = {}
    for j, c in enumerate(d["channels"]):
        avg, marg = returns_per_draw(cap[:, j], k[:, j], d["slope_m"][:, j], float(d["mean_weekly_spend"][j]))
        roi = d["roi"][:, j]
        out[str(c)] = {"est_avg": q(avg, 50), "est_marg": q(marg, 50), "avg_lo": q(avg, 5), "avg_hi": q(avg, 95),
                       "marg_lo": q(marg, 5), "marg_hi": q(marg, 95), "meridian_roi_median": q(roi, 50),
                       "meridian_roi_lo": q(roi, 5), "meridian_roi_hi": q(roi, 95), "n_saved_draws": len(roi)}
    return out


def chain_diagnostics(name: str, draws: np.ndarray, plug: np.ndarray) -> dict:
    """draws: one return per (chain, draw); plug: each chain's plug-in value of it."""
    import arviz as az
    return {f"chain_{name}_median": ";".join(f"{v:.6g}" for v in np.median(draws, axis=1)),
            f"chain_{name}_plugin": ";".join(f"{v:.6g}" for v in plug),
            f"rhat_{name}": float(az.rhat(draws)), f"mcse_{name}_median": float(az.mcse(draws, method="median")),
            f"mcse_{name}_plugin": float(np.std(plug, ddof=1) / np.sqrt(len(plug))) if len(plug) > 1 else float("nan")}


def true_returns(frame: pd.DataFrame, channel: str, cfg: dict) -> tuple[float, float]:
    """Average: the generator's realized effect over its spend, all weeks. Marginal: the derivative of its logistic
    response at the mean weekly spend; its adstock weights sum to one, so a constant spend adstocks to itself."""
    avg = float(frame[f"{channel}_effect"].sum() / frame[f"{channel}_spend"].sum())
    x = float(frame[f"{channel}_spend"].mean())
    lam, coef = cfg["saturation_lambda"], cfg["coefficient"]
    g = lambda s: coef * (1 - np.exp(-lam * s)) / (1 + np.exp(-lam * s))
    h = x * STEP
    return avg, float((g(x + h) - g(x - h)) / (2 * h))


def series(an, frame: pd.DataFrame) -> pd.DataFrame:
    """The weekly decomposition of one fit, posterior means, beside the generator's truth."""
    def mean(x, trailing):  # posterior mean over every leading (chain, draw) axis
        x = np.asarray(x, float)
        return x.reshape(-1, *x.shape[-trailing:]).mean(axis=0)
    base = mean(an._calculate_baseline_expected_outcome(aggregate_geos=True, aggregate_times=False), 1)
    expected = mean(an.expected_outcome(aggregate_geos=True, aggregate_times=False), 1)
    inc = mean(an.incremental_outcome(aggregate_times=False), 2)  # (weeks, channels)
    out = pd.DataFrame({"week": frame["week"].to_numpy(int),
                        "train": np.r_[np.ones(len(frame) - HOLDOUT_WEEKS, bool), np.zeros(HOLDOUT_WEEKS, bool)],
                        "revenue": frame["total_sales"].to_numpy(float), "expected": expected, "baseline": base})
    for j, c in enumerate(CHANNELS):
        out[f"fit_{c}"] = inc[:, j]
    out["truth_nonmarketing"] = (frame["base_sales"] + frame["promotional_sales_uplift"]).to_numpy(float)
    out["truth_pla_effect"] = frame["pla_effect"].to_numpy(float)
    out["pla_spend"] = frame["pla_spend"].to_numpy(float)
    return out


def fit(row: str, seed: int, config: str, notebook_path: str | None = None,
        sampler_seed: int = SAMPLER_SEED, sampling: dict | None = None) -> tuple[list[dict], pd.DataFrame, dict]:
    """One fit of instance (row, data seed `seed`) at `sampler_seed`: one result row per channel, and the fit's
    weekly decomposition and its saved draws. `sampling` overrides entries of SAMPLING."""
    sampling = {**SAMPLING, **(sampling or {})}
    warnings.filterwarnings("ignore")
    import arviz as az
    from meridian.analysis import analyzer
    from meridian.model import model
    frame = generator.frame(row, seed, notebook_path)
    instance_sha256 = hashlib.sha256(frame.to_csv(index=False).encode()).hexdigest()
    df = observed(frame)
    idata = input_data(df)
    n_times = len(idata.time.values)
    _, level = split(config)
    learning = experiment.run(row, seed, level, notebook_path, frame) if level else None
    t0 = time.time()
    mmm = model.Meridian(input_data=idata, model_spec=model_spec(config, n_times, learning))
    mmm.sample_prior(PRIOR_DRAWS, seed=sampler_seed)
    mmm.sample_posterior(seed=sampler_seed, **sampling)
    wall = time.time() - t0
    an = analyzer.Analyzer(mmm)
    post = mmm.inference_data.posterior
    total = int(post.sizes["chain"]) * int(post.sizes["draw"])
    rhat = [np.asarray(v, float) for v in an.get_rhat().values()]
    rhat = [r for r in rhat if not np.isnan(r).all()]
    max_rhat = max(float(np.nanmax(r)) for r in rhat)
    ess = az.ess(post, method="bulk")
    names = [k for k, v in an.get_rhat().items() if not np.isnan(np.asarray(v, float)).all()]
    min_ess = min(float(np.nanmin(ess[k].values)) for k in names if k in ess)
    converged = bool(max_rhat <= RHAT_MAX and min_ess >= ESS_MIN and all(np.isfinite(r[~np.isnan(r)]).all() for r in rhat))
    std = float(mmm.model_context.kpi_transformer.population_scaled_stdev)
    P = np.asarray(mmm.population, float)
    med = np.asarray(mmm.media_tensors.media_transformer.population_scaled_median_m, float)
    beta = post["beta_gm"].values.reshape(total, len(P), len(CHANNELS))
    ec = post["ec_m"].values.reshape(total, len(CHANNELS))
    slope = post["slope_m"].values.reshape(total, len(CHANNELS))
    cap = std * np.einsum("dgm,g->dm", beta, P)
    k = P.sum() * med[None, :] * ec
    n_chain, n_draw = int(post.sizes["chain"]), int(post.sizes["draw"])
    inc = np.asarray(an.incremental_outcome(), float).reshape(total, len(CHANNELS)).mean(axis=0)
    roi = np.asarray(an.roi(), float).reshape(total, len(CHANNELS))
    cfgs = generator.channel_configs(notebook_path)
    keep = thin_index(n_chain, n_draw)
    saved = {"beta_gm": beta[keep], "ec_m": ec[keep], "slope_m": slope[keep], "roi": roi[keep],
             "chain": keep // n_draw, "draw": keep % n_draw, "population_scaled_stdev": np.float64(std),
             "population": P, "media_median": med, "channels": np.array(CHANNELS),
             "mean_weekly_spend": np.array([float(frame[f"{c}_spend"].mean()) for c in CHANNELS])}
    per_draw = summarize(saved)
    out = []
    for j, c in enumerate(CHANNELS):
        x = float(frame[f"{c}_spend"].mean())
        point = (float(cap[:, j].mean()), float(np.median(k[:, j])), float(np.median(slope[:, j])))
        p_avg, p_marg = returns(*point, x)
        d_avg, d_marg = returns_per_draw(cap[:, j], k[:, j], slope[:, j], x)
        t_avg, t_marg = true_returns(frame, c, cfgs[c])
        by_chain = [plugin(cap[i * n_draw:(i + 1) * n_draw, j], k[i * n_draw:(i + 1) * n_draw, j],
                           slope[i * n_draw:(i + 1) * n_draw, j], x) for i in range(n_chain)]
        q = lambda v, p: float(np.percentile(v, p))
        out.append({"row": row, "seed": int(seed), "config": config, "channel": c, "converged": converged,
                    "max_rhat": max_rhat, "min_ess_bulk": min_ess, "n_knots": int(mmm.model_context.knot_info.n_knots),
                    **per_draw[c], "true_avg": t_avg, "true_marg": t_marg, "cap": point[0], "k": point[1], "s": point[2],
                    "mean_weekly_spend": x, "meridian_incremental_over_spend": float(inc[j] / frame[f"{c}_spend"].sum()),
                    "wall_seconds": wall, "sampler_seed": int(sampler_seed), "instance_sha256": instance_sha256,
                    "plugin_avg": p_avg, "plugin_marg": p_marg,
                    "meridian_roi": float(roi[:, j].mean()),
                    "all_avg_median": q(d_avg, 50), "all_marg_median": q(d_marg, 50),
                    **chain_diagnostics("avg", d_avg.reshape(n_chain, n_draw), np.array([b[0] for b in by_chain])),
                    **chain_diagnostics("marg", d_marg.reshape(n_chain, n_draw), np.array([b[1] for b in by_chain])),
                    **{f"sampling_{key}": v for key, v in sampling.items()}})
        if learning:
            out[-1].update({f: learning[f] for f in ("iroas", "iroas_lo", "iroas_hi", "prior_loc", "prior_scale")})
    weekly = series(an, frame)
    gap = weekly["expected"] - weekly["baseline"] - weekly[[f"fit_{c}" for c in CHANNELS]].sum(axis=1)
    if gap.abs().max() > 1e-6 * weekly["expected"].abs().max():
        raise RuntimeError("expected outcome is not baseline plus the media contributions")
    return out, weekly, saved
