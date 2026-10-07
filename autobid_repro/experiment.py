"""The calibrating experiments: the generator's own go-dark test on PLA, analysed on its observed columns alone.

The notebook's geo-experiment extension builds two parallel universes from one instance (create_parallel_universes):
a control universe that is the instance as generated and a treatment universe in which PLA spend is zero in the test
windows and PLA's effect is recomputed through the same adstock and saturation. Each universe gets a noisy observed
`sales` column, the same draw added to one and subtracted from the other, at a standard deviation of noise_share
times mean weekly sales. Both universes are the whole market, so the test has no geographic grain, and the
counterfactual is exact: outside the dark weeks and their carryover the two series differ by the noise alone.

Design, the notebook's own values throughout: test starts and duration as the notebook sets them (TEST_STARTS 20, 55,
100, 140; TEST_DURATION 4), slice_geo_test's measurement window of 4 pre and 8 post weeks, noise_share 0.01, and the
instance's master seed as the noise seed (the notebook's default of 42 would give every instance the same noise).

  weak     one test, the notebook's first window (weeks 20 to 23)
  strong   all four windows

Analysis. d_w is treatment sales less control sales in week w. The noise scale sigma is the standard deviation of d
over every week before the first test (19 weeks). The measured weeks are each window's test weeks and its 8 post
weeks. The effect is the sum of d over the measured weeks, its standard error sigma * sqrt(n), and the 95 percent
interval Student's t on n_pre - 1 degrees of freedom. iROAS is the effect over the spend withdrawn in the measured
weeks, and the interval is the effect's interval over the same spend.

Prior. PLA's ROI prior becomes a lognormal moment-matched to mean = the measured iROAS and standard deviation = the
interval's width over 2 * 1.959964. Meta and TV keep Meridian's default LogNormal(0.2, 0.9).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import generator

CHANNEL = "pla"
PRE_WEEKS, POST_WEEKS = 4, 8   # slice_geo_test's own defaults
NOISE_SHARE = 0.01             # create_parallel_universes' own default
ALPHA = 0.05
Z = 1.959964
LEVELS = ("weak", "strong")
DEFAULT_ROI_PRIOR = (0.2, 0.9)  # Meridian 2.0.0's LogNormal(loc, scale) on roi_m


def windows(level: str, notebook_path: str | None = None) -> list[tuple[int, int]]:
    starts, duration = generator.test_design(notebook_path)
    chosen = {"weak": starts[:1], "strong": starts}[level]
    return [(s, s + duration - 1) for s in chosen]


def measured_weeks(wins: list[tuple[int, int]]) -> list[int]:
    return sorted({w for s, e in wins for w in range(s, e + 1 + POST_WEEKS) if w <= generator.N_WEEKS})


def lognormal_from_moments(mean: float, sd: float) -> tuple[float, float]:
    s2 = float(np.log1p((sd / mean) ** 2))
    return float(np.log(mean) - s2 / 2), float(np.sqrt(s2))


def run(row: str, seed: int, level: str, notebook_path: str | None = None, frame: pd.DataFrame | None = None) -> dict:
    """One go-dark test on one instance: the measured effect and iROAS, the prior they set, and the truth."""
    frame = generator.frame(row, seed, notebook_path) if frame is None else frame
    ns = generator.namespace(notebook_path)
    wins = windows(level, notebook_path)
    control, treatment = ns["create_parallel_universes"](frame, wins, test_channel=CHANNEL, noise_share=NOISE_SHARE,
                                                         noise_seed=int(seed))
    # The analysis reads the observed columns only: week, sales and the tested channel's spend.
    c = control.set_index("week")
    t = treatment.set_index("week")
    d = t["sales"] - c["sales"]
    first = min(s for s, _ in wins)
    pre = d[d.index < first]
    sigma = float(pre.std(ddof=1))
    weeks = measured_weeks(wins)
    effect = float(d.loc[weeks].sum())
    se = sigma * np.sqrt(len(weeks))
    q = float(stats.t.ppf(1 - ALPHA / 2, len(pre) - 1))
    spend = float((t[f"{CHANNEL}_spend"] - c[f"{CHANNEL}_spend"]).loc[weeks].sum())
    iroas = effect / spend
    lo, hi = sorted(((effect - q * se) / spend, (effect + q * se) / spend))
    prior_sd = (hi - lo) / (2 * Z)
    loc, scale = lognormal_from_moments(iroas, prior_sd)
    true_effect = float((t[f"{CHANNEL}_effect"] - c[f"{CHANNEL}_effect"]).loc[weeks].sum())
    return {"row": row, "seed": int(seed), "level": level, "windows": len(wins), "measured_weeks": len(weeks),
            "pre_weeks": len(pre), "noise_sd": sigma, "effect": effect, "se": se, "effect_lo": effect - q * se,
            "effect_hi": effect + q * se, "true_effect": true_effect, "incremental_spend": spend,
            "iroas": iroas, "iroas_lo": lo, "iroas_hi": hi, "true_iroas": true_effect / spend,
            "prior_mean": iroas, "prior_sd": prior_sd, "prior_loc": loc, "prior_scale": scale}


def roi_prior(learning: dict, channels: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
    """roi_m's (loc, scale) per channel: the learning's lognormal on PLA, Meridian's default on the others."""
    loc = np.full(len(channels), DEFAULT_ROI_PRIOR[0])
    scale = np.full(len(channels), DEFAULT_ROI_PRIOR[1])
    j = channels.index(CHANNEL)
    loc[j], scale[j] = learning["prior_loc"], learning["prior_scale"]
    return loc, scale
