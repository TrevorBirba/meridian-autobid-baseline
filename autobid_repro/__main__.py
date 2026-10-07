"""python -m autobid_repro --quick          two fits: performance_chasing, seed 20260908, arms 1 and 2a
python -m autobid_repro                  every fit behind every table (190 fits)
python -m autobid_repro --sets knots     one result set; several as a comma-separated list
python -m autobid_repro --sets mechanisms --sampler-seed 101
                                         the same instances at another sampler seed, into results/sampler_seed_101/
python -m autobid_repro --only none__20260908__arm1,... --n-chains 8 --n-adapt 4000 --n-burnin 2000 --n-keep 20000
        --results results/longchain/sampler_seed_20260908
                                         named fits only, at other chain settings; --results is then required, so
                                         the main results are never overwritten, and no tables are written

One fit per process, each written to its own pair of files under <results>/units/ (the per-channel row and the
weekly decomposition), so an interrupted run resumes where it stopped and a finished fit is never refitted. The
tables under <results>/tables/ are rewritten at the end from whatever units exist.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

from . import fit, generator, report

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(HERE, "results")

MECHANISM_ROWS = ("none", "budget_feedback", "anticipatory_spend", "tv_bursts", "performance_chasing", "all_four")
TWO_ROWS = ("none", "performance_chasing")
SETS = {
    # six mechanism rows at arm 1, arm 2a and step 1; the baseline decomposition reads these fits' series
    "mechanisms": [(r, s, c) for c in ("arm1", "arm2a", "step1") for r in MECHANISM_ROWS for s in generator.SEEDS],
    "knots": [(r, s, f"knots{n}") for n in (4, 13, 26, 52) for r in TWO_ROWS for s in generator.SEEDS],
    "strength": [(r, s, c) for c in ("arm1", "arm2a") for r in ("performance_chasing_0p2", "performance_chasing_0p4")
                 for s in generator.SEEDS],
    "calibration": [(r, s, f"{a}_{lv}") for a in ("arm1", "arm2a") for lv in ("weak", "strong") for r in TWO_ROWS
                    for s in generator.SEEDS],
}
QUICK = [("performance_chasing", generator.SEEDS[0], "arm1"), ("performance_chasing", generator.SEEDS[0], "arm2a")]


def unit_paths(units_dir: str, row: str, seed: int, config: str) -> tuple[str, str, str]:
    stem = os.path.join(units_dir, f"{row}__{seed}__{config}")
    return stem + ".csv", stem + ".series.csv", stem + ".draws.npz"


def done(units_dir, row, seed, config) -> bool:
    return all(os.path.exists(p) for p in unit_paths(units_dir, row, seed, config)[:2])


def run_unit(units_dir: str, unit: str, notebook: str | None, sampler_seed: int = fit.SAMPLER_SEED,
             sampling: dict | None = None) -> None:
    row, seed, config = unit.split("__")
    rows, weekly, saved = fit.fit(row, int(seed), config, notebook, sampler_seed, sampling)
    os.makedirs(units_dir, exist_ok=True)
    table, series, draws = unit_paths(units_dir, row, int(seed), config)
    with open(draws + ".tmp", "wb") as fh:
        np.savez_compressed(fh, **saved)
    os.replace(draws + ".tmp", draws)  # the draws first: a unit is done when its CSVs exist
    for path, df in ((series, weekly), (table, pd.DataFrame(rows))):
        df.to_csv(path + ".tmp", index=False)
        os.replace(path + ".tmp", path)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="regenerate the instances, fit Meridian, and write every table")
    p.add_argument("--quick", action="store_true", help="two fits only: performance_chasing, one seed, arms 1 and 2a")
    p.add_argument("--sets", default=",".join(SETS), help=f"comma-separated, of {', '.join(SETS)}")
    p.add_argument("--results", default=None,
                   help="output directory (default: results/, or results/sampler_seed_<N>/ at another sampler seed)")
    p.add_argument("--sampler-seed", type=int, default=fit.SAMPLER_SEED,
                   help=f"Meridian's sampling seed (default {fit.SAMPLER_SEED}); the data seeds are unaffected")
    p.add_argument("--notebook", default=None, help="a local copy of the notebook; fetched from the pinned URL if absent")
    p.add_argument("--only", default=None,
                   help="comma-separated fits <row>__<data seed>__<config> to run instead of --sets; no tables are written")
    for key, n in fit.SAMPLING.items():
        p.add_argument(f"--{key.replace('_', '-')}", type=int, default=n, help=f"sampler setting {key} (default {n})")
    p.add_argument("--unit", default=None, help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    sampling = {key: getattr(a, key) for key in fit.SAMPLING}
    if sampling != fit.SAMPLING and a.results is None:
        p.error("non-default sampler settings need an explicit --results directory")
    if a.results is None:
        a.results = RESULTS if a.sampler_seed == fit.SAMPLER_SEED else os.path.join(RESULTS, f"sampler_seed_{a.sampler_seed}")
    units_dir = os.path.join(a.results, "units")
    if a.unit:
        run_unit(units_dir, a.unit, a.notebook, a.sampler_seed, sampling)
        return 0
    if a.quick:
        todo = list(QUICK)
    elif a.only:
        todo = [tuple(u.split("__")) for u in a.only.split(",")]
        todo = [(r, int(s), c) for r, s, c in todo]
        bad = [c for _, _, c in todo if c not in fit.CONFIGS]
        if bad:
            p.error(f"unknown configurations {sorted(set(bad))}")
    else:
        unknown = set(a.sets.split(",")) - set(SETS)
        if unknown:
            p.error(f"unknown sets {sorted(unknown)}")
        todo = list(dict.fromkeys(u for name in a.sets.split(",") for u in SETS[name]))
    generator.notebook(a.notebook)  # verify the pin before any fit
    t0, failed = time.time(), []
    for i, (r, s, c) in enumerate(todo, 1):
        if done(units_dir, r, s, c):
            continue
        print(f"[{i}/{len(todo)}] {r} {s} {c}  ({(time.time() - t0) / 60:.1f} min)", flush=True)
        cmd = [sys.executable, "-m", "autobid_repro", "--results", a.results, "--sampler-seed", str(a.sampler_seed),
               "--unit", f"{r}__{s}__{c}"] + [f"--{key.replace('_', '-')}={n}" for key, n in sampling.items()]
        if a.notebook:
            cmd += ["--notebook", a.notebook]
        if subprocess.run(cmd, cwd=HERE).returncode:
            failed.append(f"{r} {s} {c}")
    print(f"fits finished in {(time.time() - t0) / 60:.1f} min; {len(failed)} failed{': ' + ', '.join(failed) if failed else ''}",
          flush=True)
    if not a.only:
        report.write_all(a.results, a.notebook)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
