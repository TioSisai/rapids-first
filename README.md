<p align="right"><a href="./README-zh.md"><img src="https://img.shields.io/badge/lang-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-blue?style=for-the-badge" alt="简体中文"></a></p>

# rapids-first

A skill for Claude Code and Codex that steers Python code generation toward the RAPIDS GPU stack — automatically choosing `cupy`, `cupyx`, `cudf`, and `cuml` over `numpy`, `scipy`, `pandas`, `scikit-learn`, and `umap-learn`.

## What this skill does

This skill activates **only when the user includes `rapids-first` in their request**. Once active, every "writing Python code" subtask — rewriting existing CPU code, implementing a new algorithm, scaffolding an ETL / training / inference / batch script, adding tests, or fixing a bug — is handled with a RAPIDS-first mindset:

- **Zero-code acceleration first**: prefer `cudf.pandas` / `cuml.accel` so existing CPU code runs on GPU without any import changes.
- **Explicit RAPIDS imports** when zero-code is unsuitable: `numpy → cupy`, `scipy.ndimage → cupyx.scipy.ndimage`, `sklearn.cluster → cuml.cluster`, `faiss → cuml.neighbors`, etc.
- **Precise API targeting**: each of the four RAPIDS packages ships a flat-file API index under `apis/<pkg>.txt`, so a single `ripgrep` call recovers the exact signature and one-line docstring — no guessing from memory (cuML vs. sklearn frequently differ on parameter order, defaults, and `output_type`).
- **GPU data lifecycle discipline**: minimize `.to_pandas()` / `.get()` round-trips, avoid `cupy ↔ numpy` mixing, and prefer `cudf.read_*` so I/O lands directly on GPU.

See [SKILL.md](./skills/rapids-first/SKILL.md) for the full workflow, API search recipes, and "what not to do" guardrails.

## Quick demo

Drop the literal token `rapids-first` into your prompt and the skill takes over the rewrite.

Prompt:

> Rewrite this pandas preprocessing script with `rapids-first`.

Before — **0.59 s** (mean of 5 runs, after a warmup pass):

```python
import pandas as pd

df = pd.read_parquet("events.parquet")
df["x"] = df["a"] / df["b"]
out = df.groupby("user_id")["x"].mean()
```

After — **0.019 s** (mean of 5 runs, after a warmup pass) — **~31× faster**:

```python
import cudf

df = cudf.read_parquet("events.parquet")
df["x"] = df["a"] / df["b"]
out = df.groupby("user_id")["x"].mean()
```

Three things to notice:

- **One-line import swap.** The same `read_parquet` / arithmetic / `groupby().mean()` chain runs end-to-end on the GPU. One behavioural difference to carry over: `cudf.DataFrame.groupby` leaves group keys unsorted by default while pandas sorts them, so pass `groupby("user_id", sort=True)` when the caller depends on ordered group keys.
- **No mid-stream device round-trips.** Per the skill's GPU-data-lifecycle rule, the result stays in GPU memory; we don't call `.to_pandas()` until the consumer actually needs CPU data.
- **Zero-code alternative.** For an existing script you'd rather not touch at all, run it as `python -m cudf.pandas script.py` — the skill picks this path automatically when the user wants "make existing code run faster" instead of "show me explicit RAPIDS imports".

Reproduce locally (10M rows, ~2M unique `user_id`, 1× NVIDIA GH200 120GB, cudf 26.08.00, pandas 3.0.3):

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

- [**RAPIDS**](https://rapids.ai/) — the GPU data-science stack this skill steers toward (`cupy`, `cupyx`, `cudf`, `cuml`). A CUDA-capable NVIDIA GPU is required for the underlying libraries to import. The pre-built API index targets **RAPIDS 26.08 on CUDA 13** (`cu13` wheels, NVIDIA driver ≥ 580.65.06), but the skill works against any recent RAPIDS install.
- [**ripgrep (`rg`)**](https://github.com/BurntSushi/ripgrep) — used throughout the skill's standard workflow to recover exact API signatures from `apis/<pkg>.txt` in a single grep.

Installing RAPIDS itself (the environment the shipped index was captured against — CUDA 13 / `cu13` wheels):

```bash
pip install --extra-index-url=https://pypi.nvidia.com \
    "cudf-cu13==26.8.*" "cuml-cu13==26.8.*" "cupy-cuda13x"
```

`cupyx` ships inside `cupy`. For CUDA 12, swap each `-cu13` suffix for `-cu12` and install `cupy-cuda12x` instead. See the [RAPIDS install guide](https://docs.rapids.ai/install/) for conda / Docker and the official release selector.

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

The four pre-built `apis/<pkg>.txt` files in this repository were generated against the following environment:

| Component    | Version             |
|--------------|---------------------|
| Python       | 3.12.14             |
| CUDA runtime | 13.2                |
| cupy         | 14.2.0              |
| cupyx        | (ships with cupy)   |
| cudf         | 26.08.00            |
| cuml         | 26.08.00            |

### When to regenerate

Regenerate the API index whenever:

- You upgrade any RAPIDS package in your local environment;
- A new RAPIDS minor / major release changes public APIs (RAPIDS ships on a `YY.MM` cadence);
- Your local environment runs a CUDA / RAPIDS major version different from the table above and you observe signature drift.

If the table above already matches your environment, the shipped `apis/` is usable as-is — no regeneration needed.

### How to regenerate

A bare run regenerates the four default packages (`cupy`, `cupyx`, `cudf`, `cuml`). `--packages` overrides that list and accepts any importable module name.

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

Each run rewrites `apis/<pkg>.txt` with entries sorted by qualname, so a `git diff` surfaces API-surface changes — a quick way to audit RAPIDS upgrades. Three entries print a per-process memory address in place of a sentinel default (`cupy.testing.NumpyAliasBasicTestBase.subTest`, `cupy.testing.NumpyAliasValuesTestBase.subTest`, `cudf.io.dlpack.ColumnAccessor.pop`) and change on every run; ignore those lines when reading the diff.

If a package fails to import (missing CUDA driver, library skew, etc.), the script logs `[skip] <pkg>: import failed -> <reason>` to stderr and continues with the rest; partial regeneration is safe.

### Covering more of RAPIDS

Four packages is the default scope. On an install that carries the rest of RAPIDS, widen it in three steps.

Index the extra packages. Anything that imports gets its own `apis/<pkg>.txt`; the rest print `[skip]` and are ignored:

```bash
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py \
    --packages cugraph nx_cugraph cucim cuvs dask_cudf pylibraft raft_dask nvforest
```

Add the matching rows to `cpu-rapids-cuda-mapping.tsv`. The skill greps that file first, so a package stays invisible to it until its rows exist, even with the index file in place. Give any package with a zero-code backend a `zero_code` value, and document its activation in the SKILL.md table (`nx-cugraph` and `dask-cudf` are the two that have one).

List the new files in the SKILL.md directory tree, and add them to `DEFAULT_PACKAGES` in `fetch_rapids_apis.py` so a bare run keeps them fresh.

The `v26.06` tag is the last release that shipped all thirteen index files with the matching mapping rows and SKILL.md text. `git checkout v26.06 -- skills/rapids-first` restores that whole payload; regenerate `apis/` afterwards unless you are actually running RAPIDS 26.06.
