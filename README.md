# meridian-autobid-baseline

When an ad platform's automated bidding chases the demand that also drives sales, PLA spend rises and falls with
sales that the PLA ads did not cause. On Heusch's synthetic MMM generator with that mechanism switched on, Google
Meridian 2.0.0 at its defaults (one time knot on a national model, so a baseline that cannot move in time) reads PLA's
average return at about 37 against a true 4.29. The weekly decomposition shows where it comes from: the fixed baseline
undershoots true non-marketing sales, and the shortfall, which tracks PLA spend, is credited to PLA. Meridian's own
worked example, with automatic knot selection, follows the baseline and reads about 1.5 (posterior median of the
per-draw return; 2.3 as the plug-in the note first reported), the same understatement it shows with no mechanism at
all. Fixing the knot count between the two moves the estimate from one side of the truth to the other. A PLA ROI
prior set from a go-dark experiment brings the average return to about 4.2 on either configuration, but leaves the
marginal return at about half the truth.

This package regenerates every number and both figures of the note from public sources: the generator notebook,
fetched and verified at run time, and Meridian from PyPI.

## What it reproduces

| Result in the note | Output | Command |
|---|---|---|
| (a) Arm 1, arm 2a and step 1 on the six mechanism rows (PLA, Meta, TV; per seed; convergence; arm 2a knot counts) | `results/tables/mechanisms.md` | `python -m autobid_repro --sets mechanisms` |
| (b) Weekly baseline decomposition: fitted baseline, fitted PLA contribution, true non-marketing sales; corr(baseline, truth), RMSE, corr(residual, PLA spend), residual share of PLA's fitted contribution; step 1's Hill curve at the mean spend | `results/tables/baseline.md`, `results/baseline_metrics.csv`, `results/units/*.series.csv` | `python -m autobid_repro --sets mechanisms` (the decomposition is written by every fit) |
| (c) Knot sweep: arm 1 with knots fixed at 4, 13, 26, 52 on `none` and `performance_chasing` | `results/tables/knots.md` | `python -m autobid_repro --sets mechanisms,knots` |
| (d) Auto-bidding strength: performance chasing alone at roi_sensitivity 0.2 and 0.4, arms 1 and 2a | `results/tables/strength.md` | `python -m autobid_repro --sets mechanisms,strength` |
| (e) Calibration: weak and strong go-dark experiments, the priors they set, calibrated arm 1 and arm 2a | `results/tables/calibration.md`, `results/learnings.csv` | `python -m autobid_repro --sets mechanisms,calibration` |
| Figure 1: weekly baseline and PLA contribution against the truth, data seed 20260908 | `results/figures/fig1_baseline_seed20260908.{pdf,png}` | `python figures/baseline_figure.py` |
| Figure 2: PLA estimated over true average return against knots and against bidding strength | `results/figures/fig2_sweeps.{pdf,png}` | `python figures/sweep_figure.py` |
| Agreement with the original fits; the estimand check (per-draw, plug-in, Meridian's ROI) | `results/comparison.md`, `results/estimand_check.csv` | `python -m autobid_repro.compare` |
| Long-chain test of the fragile fits | `results/longchain/longchain.md`, `results/longchain/longchain.csv` | see [Long-chain test](#long-chain-test) |

`python -m autobid_repro` with no arguments runs all of it (190 fits) and writes every table; `--quick` runs two fits
(`performance_chasing`, data seed 20260908, arms 1 and 2a) as a check that the installation reproduces the headline
numbers. Every result set names the fits it needs; tables (b) to (e) reuse the arm 1 and arm 2a fits of (a) for their
one-knot, automatic-knot, zero-strength and uncalibrated rows. Each fit runs in its own process and writes
`results/units/<row>__<data seed>__<config>.csv`, `.series.csv` and `.draws.npz`, so a killed run resumes where it
stopped and a finished fit is never refitted.

**Saved draws.** Every fit saves 1,000 posterior draws, spread evenly over its chains, of the parameters the return
formulas need (`beta_gm`, `ec_m`, `slope_m`, with the constants that turn them into cap and k) and Meridian's per-draw
ROI per channel, as `<unit>.draws.npz` next to its CSV (about 95 KB each). Every per-draw column is computed from
that file, so a change to the formula is a recompute, `python -m autobid_repro.report --recompute`, not a refit. The
draws are not committed (`.gitignore`): 378 files, 29 MB, under `results/units/`,
`results/sampler_seed_101/units/` and `results/longchain/sampler_seed_*/units/`. Rerunning the fits regenerates them
bit for bit.

## Run

    git clone https://github.com/TrevorBirba/meridian-autobid-baseline.git
    cd meridian-autobid-baseline
    python3.11 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m autobid_repro --quick            # two fits, about two minutes
    .venv/bin/python -m autobid_repro                    # all 190 fits and every table
    .venv/bin/python -m autobid_repro.compare            # results/comparison.md
    .venv/bin/python figures/baseline_figure.py
    .venv/bin/python figures/sweep_figure.py

`--results DIR` writes somewhere other than `results/`; `--notebook PATH` uses a local copy of the notebook (it is
still checked against the pinned hash). `--only <row>__<data seed>__<config>,...` runs the named fits and writes no
tables; `--n-chains`, `--n-adapt`, `--n-burnin` and `--n-keep` change the sampler settings (defaults 4, 2,000, 1,000,
5,000), and then `--results` is required, so the main results cannot be overwritten.

### Long-chain test

The fits whose results moved under the original's six-decimal input or under a second sampler seed, refitted with
8 chains of 4,000 adaptation steps, 2,000 burn-in and 20,000 kept draws at sampler seeds 20260908 and 101:

    U=$(.venv/bin/python -m autobid_repro.longchain --units)      # the 49 fragile fits; --list gives the reasons
    for S in 20260908 101; do
      .venv/bin/python -m autobid_repro --only "$U" --sampler-seed $S --n-chains 8 --n-adapt 4000 \
          --n-burnin 2000 --n-keep 20000 --results results/longchain/sampler_seed_$S
    done
    .venv/bin/python -m autobid_repro.longchain                   # results/longchain/longchain.md

The fragile fits are every data seed of the Table 1 cells whose median moved beyond the second-seed spread, every fit
whose convergence flag differs from the original's, and arm 1 at roi_sensitivity 0.2 and 0.4 on every data seed.
The findings are in `results/comparison.md`: the chains of 45 of the 49 agree (under-sampling); four have separate
modes (arm 1 at 0.2, data seed 20260908; arm 1 at 0.4, 20260909; step 1 none, 20260910; step 1 anticipatory_spend,
20260909).

## The generator

The data come from the notebook accompanying Heusch, *A Synthetic Benchmark Dataset with Endogenous Marketing Spend
for Validating Marketing Mix Models* (arXiv:2608.21130; see [Reference](#reference)),
`generate_synthetic_mmm_data.ipynb` in
[github.com/niklas-heusch/mmm-materials](https://github.com/niklas-heusch/mmm-materials). The generator notebook is the
work of Niklas Heusch, who permitted its use and modification on condition of attribution (personal communication,
7 October 2026). The notebook itself is not redistributed here; it is fetched at run time from

    https://raw.githubusercontent.com/niklas-heusch/mmm-materials/main/generate_synthetic_mmm_data.ipynb

and refused unless its sha256 is `90408809611458ef821dd52b8114f5e9066a070452cba1b8fe0166b3634ee086` (31,350 bytes,
retrieved 7 September 2026). The notebook carries no version and its branch moves, so the hash is the version: if the
branch has moved, the run stops rather than fitting different data. The notebook's code cells, joined in order, are
the verbatim module; `generator.diff` is applied to it with `patch`; the cache under `data/` is not committed.
`generator.diff` is a modification of the notebook, published under the author's permission; its first two lines
name the source notebook, its sha256, the author and the attribution condition (`patch` and `git apply` skip them).

### What `generator.diff` changes

Two things, and no equation:

1. **One master seed per instance.** The notebook seeds each of four functions with numpy's global generator at
   `random_state=42`. The fork makes `random_state` a required keyword and has `build_dataset` take a `master_seed`,
   from which the four seeds are `np.random.SeedSequence(master_seed).generate_state(4)`, assigned in a fixed order
   (base sales, measurement errors, traditional spend, PLA spend). Instances at different seeds are therefore
   independent draws of the same process. The fork at master seed 42 is not the notebook's own dataset, which seeds
   every function with 42.
2. **The four mechanisms as arguments.** Values the notebook writes as literals become `build_dataset` arguments
   whose defaults are the notebook's published values: `budget_feedback_sensitivity` (0.3),
   `strategic_endogeneity_pla`, `_meta`, `_tv` (0.2, 0.4, 0.0), `tv_burst_multiplier_weeks_47_51` and `_20_22` (15, 8),
   `anticipation_coefficient` (0.4) and `roi_sensitivity` (0.8). A row switches a mechanism off by setting its
   coefficients to zero and its burst multipliers to one.

The notebook's own runs (writing CSV and JSON files) are not executed: the source is sliced before them.
`create_parallel_universes` and `slice_geo_test`, the notebook's geo-experiment extension, are used unchanged.

### Rows and seeds

| row | mechanisms on |
|---|---|
| `none` | none |
| `budget_feedback` | quarterly budget feedback |
| `anticipatory_spend` | anticipatory pre-promotion spend |
| `tv_bursts` | scheduled TV bursts |
| `performance_chasing` | algorithmic performance chasing on PLA (roi_sensitivity 0.8) |
| `all_four` | all four |
| `performance_chasing_0p2`, `_0p4` | performance chasing alone at roi_sensitivity 0.2, 0.4 |

Data seeds 20260908 to 20260912, 156 weeks each.

## The model

A single national market: weekly revenue (the generator's `total_sales`) as the KPI; PLA, Meta and TV weekly spend as
both media and spend; three controls, a linear trend in years and one annual sine and cosine; population the mean
weekly revenue; the last 13 weeks held out of the likelihood; `max_lag` 8. Sampling: 500 prior draws, then 4 chains of
2,000 adaptation steps, 1,000 burn-in and 5,000 kept draws. A fit converges when max R-hat is at most 1.1 and minimum
bulk ESS at least 400; tables report medians over converged seeds.

**Two kinds of seed.** The *data seed* (20260908 to 20260912) is the generator's master seed: it fixes an instance,
and "seed" in the tables always means this one. The *sampler seed* seeds Meridian's prior and posterior sampling. The
main run uses sampler seed 20260908 for every fit. It is a fixed constant, not derived from the instance; it equals the
first data seed only because the original study chose it that way. `--sampler-seed N` refits the same instances at
another sampler seed and writes to `results/sampler_seed_N/`; every fit records its sampler seed and the sha256 of the
instance it read, and `results/comparison.md` checks that a second-seed run (sampler seed 101) read byte-identical
instances.

| config | differs from arm 1 in |
|---|---|
| `arm1` | nothing: every optional value at Meridian 2.0.0's default; one time knot, Hill slope fixed at 1 |
| `arm2a` | the getting-started example: roi_m LogNormal(0.2, 0.9) stated, automatic knot selection |
| `step1` | Hill slope freed under LogNormal(0.7, 0.4) |
| `knots4`, `knots13`, `knots26`, `knots52` | that many time knots |
| `arm1_weak`, `arm1_strong`, `arm2a_weak`, `arm2a_strong` | PLA's ROI prior set from the weak or strong experiment |

**Returns.** Meridian's media response at a sustained weekly spend x is the Hill curve cap * x^s / (x^s + k^s), with
cap the channel's scaled coefficient times population and k and s the half-saturation and slope. Average return is
f(x)/x and marginal return f'(x), both at the channel's mean weekly spend over all 156 weeks, computed for every one
of the fit's 1,000 saved posterior draws; the tables report the median and, as the 90 percent interval, the 5th to
95th percentile. Beside them: the plug-in, the curve at posterior-mean cap and posterior-median k and s, which is
what the note first reported and what the original fits record; and Meridian's own ROI, `Analyzer.roi()` per draw
(its median over the same draws; `meridian_roi` in `fits.csv` is its posterior mean over every kept draw). The
truth is the generator's: realized effect over spend for the average, the derivative of its logistic response at the
mean spend for the marginal.

**Baseline decomposition.** Meridian's baseline is its posterior-mean expected outcome with every media channel at
zero and the controls as observed, by week; expected outcome less baseline equals the summed media contributions,
which every fit checks. The truth is `base_sales + promotional_sales_uplift`.

**Calibration.** `experiment.py` runs the notebook's go-dark test on PLA through `create_parallel_universes`, at the
notebook's own windows and duration (starts 20, 55, 100, 140; 4 weeks), `slice_geo_test`'s window (4 pre, 8 post
weeks) and noise share (0.01), with the instance's master seed as the noise seed. Weak is the first window, strong all
four. The effect is the summed treatment-less-control gap over each window's test and post weeks, the noise scale is
identified on the 19 weeks before the first test, and the 95 percent interval is Student's t. The iROAS and its
interval are the effect's over the spend withdrawn. PLA's prior becomes the lognormal with mean the iROAS and
standard deviation the interval width over 2 x 1.96; Meta and TV keep LogNormal(0.2, 0.9).

## Environment

Python 3.11.13. Pinned in `requirements.txt`: google-meridian 2.0.0, tensorflow 2.21.0, tf_keras 2.21.0,
tfp-nightly 0.26.0.dev20260130, numpy 2.3.5, pandas 2.3.3, scipy 1.17.1, arviz 0.19.0, xarray 2026.7.0,
protobuf 6.33.6, matplotlib 3.10.9. The sampler is deterministic given its inputs and these builds; other versions
may move the draws.

## Hardware and run time

Measured on an Apple M4 (10 cores, 16 GB), macOS 15.6, CPU only, one fit at a time, notebook already cached:

| mode | fits | wall time |
|---|---|---|
| `--quick` | 2 | 1 min 56 s to 1 min 57 s (two runs) |
| full | 190 | 2 h 46 min (9,960 s) |
| `--sets mechanisms --sampler-seed 101` | 90 | 1 h 19 min (4,746 s, sharing the machine with other fits for part of it) |
| all 280 fits regenerated with saved draws, and the 98 long-chain fits | 378 | 2 h 56 min, as nine processes at once |

Median sampler time per fit, one at a time: 17 to 24 s at arm 1 (calibrated or not), 28 s at step 1, 34 to 41 s at
the fixed-knot configurations, 74 to 79 s at arm 2a. Process start-up, the weekly decomposition and writing add about
6 s a fit. The `wall_seconds` now stored in the fit files come from the nine-process regeneration and run two to
four times longer (arm 1 61 s, arm 2a 265 s median); a long-chain fit took a median 155 to 193 s at arm 1, 312 to
332 s at step 1 and 1,370 s at arm 2a under the same load. Each fit process uses about one core. Installing the
requirements takes a few minutes more.

## Agreement with the original fits

`results/comparison.md` sets every PLA estimate beside the original fits' (exported to `results/reference/`), per
data seed, and records why they differ:

- **Instances and experiments:** identical. The generated instances match to 4.5e-13; the 20 go-dark experiments
  and the priors they set match to 1e-12.
- **Headline cells:** arm 1 and arm 2a on `performance_chasing` agree within 0.5 and 1.5 percent on every data seed.
  The calibrated cells agree within 0.6 percent. In the baseline decomposition the correlations agree within
  0.005 and RMSE within 10; the residual share of PLA's contribution and PLA's fitted-over-true ratio move with
  the PLA estimate, by up to 0.22 and 0.12, most where PLA's fitted contribution is small (arm 1 and step 1 on
  `none`). On arm 1 `performance_chasing` the share agrees to 0.001.
- **Elsewhere:** cells can differ by more, up to 29 percent at step 1, and 14 fits change their convergence flag.
  The cause is the input. The original pipeline stored the observed series as daily values at six decimals, so its
  weekly inputs differ from the generator's by at most 3.5e-6. Meridian's sampler is deterministic but not
  continuous in its inputs. Refitted on the original's exact weekly input, this package returns the original's
  estimates to six decimals, R-hat and convergence flag on all nine cells checked. The size of the difference is
  set by the posterior: small where it is narrow, large where it is wide or has two modes.
- **Robustness checks:** a second sampler seed (101) gives a per-cell yardstick for that sensitivity. A strict
  R-hat gate of 1.01 shows which table cells depend on borderline fits. The long-chain test settles the fragile fits:
  45 of 49 converge to one answer with long chains, and against it the main run and the original are two short runs
  of the same posterior (both match on 29, only the main run on 12, only the original on 8, neither on none).

These comparisons are on the plug-in returns, the only ones the original records.

Four caveats for readers of the tables:

- **The estimate is the per-draw median.** It agrees with Meridian's own ROI median within 2.5 percent on every
  configuration and row but step 1 performance_chasing (5 percent) and step 1 all_four (22 percent, the curve's
  shape over the realized spend path). Where the posterior is wide it sits well below the plug-in (0.63 to 0.69 of it
  on the understated arm 1 and arm 2a rows, 0.27 to 0.56 at step 1), because the per-draw distribution is
  right-skewed and the plug-in tracks its mean. Mean or median moves those cells as much as plug-in or per-draw does.
- **The saved draws carry Monte Carlo error.** Over 1,000 saved draws the per-draw median moves 5 to 9 percent
  between sampler seeds on the wide rows, against 2 percent over every kept draw (`all_avg_median` in `fits.csv`).
- **Where PLA reads low, the posterior is the default prior.** Every uncalibrated configuration carries Meridian's
  default LogNormal(0.2, 0.9) ROI prior on PLA (median 1.22, 90 percent interval [0.28, 5.37]). On the cells that read
  PLA low, arm 2a's included, the per-draw median is 0.94 to 1.64 times that median with an interval of about the
  prior's width, and PLA's half-saturation k sits on its own prior; those levels are the prior's, not an estimate.
  Each per-draw table and `results/comparison.md` set every uncalibrated cell beside the prior.
- **Two strength fits are bimodal.** Arm 1 at 0.2, data seed 20260908, and at 0.4, data seed 20260909, have
  posteriors with two modes that long chains do not resolve. Every other strength fit lands in one mode, the same at
  both sampler seeds under long chains.

## Reference

Heusch, N. (2026). *A Synthetic Benchmark Dataset with Endogenous Marketing Spend for Validating Marketing Mix
Models*. arXiv:2608.21130 [stat.AP]. https://arxiv.org/abs/2608.21130

    @misc{heusch2026synthetic,
      author        = {Heusch, Niklas},
      title         = {A Synthetic Benchmark Dataset with Endogenous Marketing Spend for Validating Marketing Mix Models},
      year          = {2026},
      eprint        = {2608.21130},
      archivePrefix = {arXiv},
      primaryClass  = {stat.AP},
      url           = {https://arxiv.org/abs/2608.21130}
    }

## Licence

The code in this repository is MIT licensed (`LICENSE`). The generator notebook is the work of Niklas Heusch, who
permitted its use and modification on condition of attribution (personal communication, 7 October 2026). The notebook
itself is not redistributed: it is fetched at run time. `generator.diff` is a modification of it, published under
that permission.
