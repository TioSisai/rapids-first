<p align="right"><a href="./README-zh.md"><img src="https://img.shields.io/badge/lang-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-blue?style=for-the-badge" alt="简体中文"></a></p>

# rapids-first

A skill for Claude Code and Codex that steers Python code generation toward the RAPIDS GPU stack — automatically choosing `cupy`, `cudf`, `cuml`, `cugraph`, `cucim`, `cuvs`, and friends over `numpy`, `pandas`, `scikit-learn`, `scipy`, `networkx`, `scikit-image`, and `faiss`.

## What this skill does

This skill activates **only when the user includes `rapids-first` in their request**. Once active, every "writing Python code" subtask — rewriting existing CPU code, implementing a new algorithm, scaffolding an ETL / training / inference / batch script, adding tests, or fixing a bug — is handled with a RAPIDS-first mindset:

- **Zero-code acceleration first**: prefer `cudf.pandas` / `cuml.accel` / `nx-cugraph` backend / `dask-cudf` backend so existing CPU code runs on GPU without any import changes.
- **Explicit RAPIDS imports** when zero-code is unsuitable: `numpy → cupy`, `scipy.ndimage → cupyx.scipy.ndimage`, `sklearn.cluster → cuml.cluster`, `faiss → cuvs.neighbors`, etc.
- **Precise API targeting**: each RAPIDS package ships a flat-file API index under `apis/<pkg>.txt`, so a single `ripgrep` call recovers the exact signature and one-line docstring — no guessing from memory (cuML vs. sklearn frequently differ on parameter order, defaults, and `output_type`).
- **GPU data lifecycle discipline**: minimize `.to_pandas()` / `.get()` round-trips, avoid `cupy ↔ numpy` mixing, and prefer `cudf.read_*` so I/O lands directly on GPU.

See [SKILL.md](./skills/rapids-first/SKILL.md) for the full workflow, API search recipes, and "what not to do" guardrails.

## Quick demo

Drop the literal token `rapids-first` into your prompt and the skill takes over the rewrite.

Prompt:

> Rewrite this pandas preprocessing script with `rapids-first`.

Before — **0.85 s** (mean of 5 runs, after a warmup pass):

```python
import pandas as pd

df = pd.read_parquet("events.parquet")
df["x"] = df["a"] / df["b"]
out = df.groupby("user_id")["x"].mean()
```

After — **0.06 s** (mean of 5 runs, after a warmup pass) — **~15× faster**:

```python
import cudf

df = cudf.read_parquet("events.parquet")
df["x"] = df["a"] / df["b"]
out = df.groupby("user_id")["x"].mean()
```

Three things to notice:

- **The only change is the import.** `cudf` is a drop-in for `pandas` here — the same `read_parquet` / arithmetic / `groupby().mean()` chain runs end-to-end on the GPU.
- **No mid-stream device round-trips.** Per the skill's GPU-data-lifecycle rule, the result stays in GPU memory; we don't call `.to_pandas()` until the consumer actually needs CPU data.
- **Zero-code alternative.** For an existing script you'd rather not touch at all, run it as `python -m cudf.pandas script.py` — the skill picks this path automatically when the user wants "make existing code run faster" instead of "show me explicit RAPIDS imports".

Reproduce locally (10M rows, ~2M unique `user_id`, RTX 4060 Ti, cudf 26.06.00, pandas 2.3.3):

```python
# gen_events.py — generate ~130 MB events.parquet in $TMPDIR
import os, numpy as np, pandas as pd
rng = np.random.default_rng(20260514)
n_rows, n_users = 10_000_000, 2_000_000
pd.DataFrame({
    "user_id": rng.integers(0, n_users, size=n_rows, dtype=np.int32),
    "a": rng.normal(10.0, 3.0, n_rows).astype(np.float32),
    "b": rng.uniform(0.5, 5.0, n_rows).astype(np.float32),
}).to_parquet(f"{os.environ['TMPDIR']}/events.parquet", index=False)
```

## Requirements

- [**RAPIDS**](https://rapids.ai/) — the GPU data-science stack this skill steers toward (`cupy`, `cudf`, `cuml`, `cugraph`, `cucim`, `cuvs`, `nvforest`, `nx-cugraph`, `dask-cudf`, `cuxfilter`, `pylibraft`, `raft-dask`). A CUDA-capable NVIDIA GPU is required for the underlying libraries to import. The pre-built API index targets **RAPIDS 26.06 on CUDA 13** (`cu13` wheels, NVIDIA driver ≥ 580.65.06), but the skill works against any recent RAPIDS install.
- [**ripgrep (`rg`)**](https://github.com/BurntSushi/ripgrep) — used throughout the skill's standard workflow to recover exact API signatures from `apis/<pkg>.txt` in a single grep.

Installing RAPIDS itself (the environment the shipped index was captured against — CUDA 13 / `cu13` wheels):

```bash
pip install --extra-index-url=https://pypi.nvidia.com \
    "cudf-cu13==26.6.*" "dask-cudf-cu13==26.6.*" "cuml-cu13==26.6.*" \
    "cugraph-cu13==26.6.*" "nx-cugraph-cu13==26.6.*" "cuxfilter-cu13==26.6.*" \
    "cucim-cu13==26.6.*" "pylibraft-cu13==26.6.*" "raft-dask-cu13==26.6.*" \
    "cuvs-cu13==26.6.*" "nvforest-cu13==26.6.*"
```

For CUDA 12, swap each `-cu13` suffix for `-cu12`. See the [RAPIDS install guide](https://docs.rapids.ai/install/) for conda / Docker and the official release selector.

## Installation

The actual skill payload lives at `skills/rapids-first/` inside this repository.

### Recommended: GitHub CLI

If you have the [GitHub CLI](https://cli.github.com/) with the `skill` subcommand available, it handles the `skills/<name>/` subdirectory automatically:

```bash
# Claude Code
gh skill install TioSisai/rapids-first rapids-first --agent claude-code --scope user

# Codex
gh skill install TioSisai/rapids-first rapids-first --agent codex --scope user
```

### Manual: git clone

#### Claude Code

User-level (available across all projects):

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first ~/.claude/skills/rapids-first
```

Project-level (scoped to the current project):

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first .claude/skills/rapids-first
```

#### Codex

User-level:

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first ~/.agents/skills/rapids-first
```

Project-level:

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first .agents/skills/rapids-first
```

### Usage

After installation, restart the CLI (or start a new session). Trigger the skill by including the literal token `rapids-first` in any prompt, for example:

> Rewrite this preprocessing script `rapids-first`.

> Implement KMeans on this DataFrame with `rapids-first`.

## API index versions

The pre-built `apis/<pkg>.txt` files in this repository were generated against the following environment:

| Component    | Version             |
|--------------|---------------------|
| Python       | 3.12.13             |
| CUDA runtime | 13.2                |
| cupy         | 14.1.1              |
| cupyx        | (ships with cupy)   |
| cudf         | 26.06.00            |
| dask_cudf    | 26.06.00            |
| cuml         | 26.06.00            |
| cugraph      | 26.06.00            |
| nx_cugraph   | 26.06.00            |
| cuxfilter    | 26.06.00            |
| cucim        | 26.06.00            |
| pylibraft    | 26.06.00            |
| raft_dask    | 26.06.00            |
| cuvs         | 26.06.00            |
| nvforest     | 26.06.00            |

### When to regenerate

Regenerate the API index whenever:

- You upgrade any RAPIDS package in your local environment;
- A new RAPIDS minor / major release changes public APIs (RAPIDS ships on a `YY.MM` cadence);
- Your local environment runs a CUDA / RAPIDS major version different from the table above and you observe signature drift.

If the table above already matches your environment, the shipped `apis/` is usable as-is — no regeneration needed.

### How to regenerate

```bash
# 1. Activate the Python environment that has RAPIDS installed
conda activate <your-rapids-env>            # conda
# source /path/to/venv/bin/activate         # venv

# 2. Run the script via its absolute path (Claude Code, user-level install)
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py
# Project-level install:  python /path/to/your/project/.claude/skills/rapids-first/fetch_rapids_apis.py
# For Codex:              replace `.claude` with `.agents`

# Regenerate specific packages only
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py --packages cudf cuml

# Write to a different output root
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py --output-dir /tmp/rapids-apis
```

Each run rewrites `apis/<pkg>.txt` deterministically (entries sorted by qualname), so a `git diff` immediately surfaces API-surface changes — a quick way to audit RAPIDS upgrades.

If a package fails to import (missing CUDA driver, library skew, etc.), the script logs `[skip] <pkg>: import failed -> <reason>` to stderr and continues with the rest; partial regeneration is safe.
