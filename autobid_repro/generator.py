"""The instances, regenerated from the public notebook.

The notebook (arXiv:2608.21130's generator) carries no version and lives on a branch that moves, so its sha256 is the
version: the pin below is the notebook as retrieved on 7 September 2026. The notebook's code cells, joined in order
by one blank line with a trailing newline, are the verbatim module; generator.diff (one master seed per instance and
the mechanism values exposed as arguments) is applied to it with `patch`. Nothing else changes a line of it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import urllib.request

NOTEBOOK_URL = "https://raw.githubusercontent.com/niklas-heusch/mmm-materials/main/generate_synthetic_mmm_data.ipynb"
NOTEBOOK_SHA256 = "90408809611458ef821dd52b8114f5e9066a070452cba1b8fe0166b3634ee086"
TAIL_MARKER = "synthetic_dataset, quarterly_multipliers, transformation_details = build_dataset("
GEO_START = "def create_parallel_universes("
GEO_END = "# The four PLA go-dark tests of the calibration paper"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIFF = os.path.join(HERE, "generator.diff")
CACHE = os.path.join(HERE, "data")

SEEDS = (20260908, 20260909, 20260910, 20260911, 20260912)
N_WEEKS = 156
START = "2023-01-02"  # week 1's Monday; a label with no effect on any generated value

# Each mechanism's published value and its ablated value (zero for a coefficient, one for a burst multiplier).
MECHANISMS = {
    "quarterly_budget_feedback": ({"budget_feedback_sensitivity": 0.3}, {"budget_feedback_sensitivity": 0}),
    "anticipatory_pre_promotion_spend": (
        {"strategic_endogeneity_pla": 0.2, "strategic_endogeneity_meta": 0.4, "strategic_endogeneity_tv": 0.0,
         "anticipation_coefficient": 0.4},
        {"strategic_endogeneity_pla": 0.0, "strategic_endogeneity_meta": 0.0, "strategic_endogeneity_tv": 0.0,
         "anticipation_coefficient": 0.0}),
    "scheduled_tv_bursts": ({"tv_burst_multiplier_weeks_47_51": 15, "tv_burst_multiplier_weeks_20_22": 8},
                            {"tv_burst_multiplier_weeks_47_51": 1, "tv_burst_multiplier_weeks_20_22": 1}),
    "algorithmic_performance_chasing": ({"roi_sensitivity": 0.8}, {"roi_sensitivity": 0}),
}
ROWS = {
    "none": ([], {}),
    "budget_feedback": (["quarterly_budget_feedback"], {}),
    "anticipatory_spend": (["anticipatory_pre_promotion_spend"], {}),
    "tv_bursts": (["scheduled_tv_bursts"], {}),
    "performance_chasing": (["algorithmic_performance_chasing"], {}),
    "all_four": (list(MECHANISMS), {}),
    "performance_chasing_0p2": (["algorithmic_performance_chasing"], {"roi_sensitivity": 0.2}),
    "performance_chasing_0p4": (["algorithmic_performance_chasing"], {"roi_sensitivity": 0.4}),
}


def sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def notebook(path: str | None = None) -> str:
    """A local copy of the notebook, fetched once if none is given, refused unless it hashes to the pin."""
    if path is None:
        os.makedirs(CACHE, exist_ok=True)
        path = os.path.join(CACHE, "generate_synthetic_mmm_data.ipynb")
        if not os.path.exists(path):
            tmp = f"{path}.{os.getpid()}.tmp"
            urllib.request.urlretrieve(NOTEBOOK_URL, tmp)
            os.replace(tmp, path)
    got = sha256(path)
    if got != NOTEBOOK_SHA256:
        raise RuntimeError(f"{path} hashes {got}, not the pinned {NOTEBOOK_SHA256}; the branch has moved")
    return path


def forked_source(notebook_path: str | None = None) -> str:
    nb_path = notebook(notebook_path)
    with open(nb_path) as f:
        nb = json.load(f)
    verbatim = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code") + "\n"
    # Written under this process's own names and renamed into place, so concurrent runs never read a partial file.
    os.makedirs(CACHE, exist_ok=True)
    vpath, fpath = os.path.join(CACHE, "generator_verbatim.py"), os.path.join(CACHE, "generator_forked.py")
    vtmp, ftmp = f"{vpath}.{os.getpid()}.tmp", f"{fpath}.{os.getpid()}.tmp"
    with open(vtmp, "w") as f:
        f.write(verbatim)
    subprocess.run(["patch", "-s", "-o", ftmp, vtmp, DIFF], check=True)
    with open(ftmp) as f:
        forked = f.read()
    os.replace(vtmp, vpath)
    os.replace(ftmp, fpath)
    return forked


_NS: dict | None = None


def namespace(notebook_path: str | None = None) -> dict:
    """The fork's definitions and the notebook's two geo-experiment functions, create_parallel_universes and
    slice_geo_test. The notebook's own runs of them, which write files, are not executed: the source is sliced
    before the build_dataset call and around the geo-experiment run."""
    global _NS
    if _NS is None:
        src = forked_source(notebook_path)
        _NS = {"__name__": "heusch_fork"}
        exec(compile(src[:src.index(TAIL_MARKER)], "generator_forked.py", "exec"), _NS)
        exec(compile(src[src.index(GEO_START):src.index(GEO_END)], "generator_forked.py", "exec"), _NS)
    return _NS


def test_design(notebook_path: str | None = None) -> tuple[list[int], int]:
    """TEST_STARTS and TEST_DURATION as the notebook sets them, read from its source rather than restated."""
    src = forked_source(notebook_path)
    m = re.search(r"TEST_STARTS,\s*TEST_DURATION\s*=\s*\[([0-9,\s]+)\],\s*(\d+)", src)
    if not m:
        raise RuntimeError("the notebook no longer sets TEST_STARTS and TEST_DURATION")
    return [int(x) for x in m.group(1).split(",")], int(m.group(2))


def mechanism_kwargs(row: str) -> dict:
    active, overrides = ROWS[row]
    kw = {}
    for name, (published, ablated) in MECHANISMS.items():
        kw.update(published if name in active else ablated)
    kw.update(overrides)
    return kw


def frame(row: str, seed: int, notebook_path: str | None = None):
    """build_dataset's frame for one instance: observed and true columns side by side."""
    df, _, _ = namespace(notebook_path)["build_dataset"](N_WEEKS, master_seed=int(seed), **mechanism_kwargs(row))
    return df


def channel_configs(notebook_path: str | None = None) -> dict:
    return namespace(notebook_path)["CHANNEL_CONFIGS"]
