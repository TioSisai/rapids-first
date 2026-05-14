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

## Requirements

- [**RAPIDS**](https://rapids.ai/) — the GPU data-science stack this skill steers toward (`cupy`, `cudf`, `cuml`, `cugraph`, `cucim`, `cuvs`, `nx-cugraph`, `dask-cudf`, `cuxfilter`, `pylibraft`, `raft-dask`). A CUDA-capable NVIDIA GPU and matching CUDA driver are required for the underlying libraries to import.
- [**ripgrep (`rg`)**](https://github.com/BurntSushi/ripgrep) — used throughout the skill's standard workflow to recover exact API signatures from `apis/<pkg>.txt` in a single grep.

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
| CUDA runtime | 12.9                |
| cupy         | 14.0.1              |
| cupyx        | (ships with cupy)   |
| cudf         | 26.02.01            |
| dask_cudf    | 26.02.01            |
| cuml         | 26.02.000           |
| cugraph      | 26.02.00            |
| nx_cugraph   | 26.02.000           |
| cuxfilter    | 26.02.000           |
| cucim        | 26.02.01            |
| pylibraft    | 26.02.00            |
| raft_dask    | 26.02.00            |
| cuvs         | 26.02.000           |

### When to regenerate

Regenerate the API index whenever:

- You upgrade any RAPIDS package in your local environment;
- A new RAPIDS minor / major release changes public APIs (RAPIDS ships on a `YY.MM` cadence);
- Your local environment runs a CUDA / RAPIDS major version different from the table above and you observe signature drift.

If the table above already matches your environment, the shipped `apis/` is usable as-is — no regeneration needed.

### How to regenerate

From the skill root, in a Python environment that has RAPIDS installed and CUDA visible:

```bash
# Regenerate all 12 packages (default)
python fetch_rapids_apis.py

# Regenerate specific packages only
python fetch_rapids_apis.py --packages cudf cuml

# Write to a different output root
python fetch_rapids_apis.py --output-dir /tmp/rapids-apis
```

Each run rewrites `apis/<pkg>.txt` deterministically (entries sorted by qualname), so a `git diff` immediately surfaces API-surface changes — a quick way to audit RAPIDS upgrades.

If a package fails to import (missing CUDA driver, library skew, etc.), the script logs `[skip] <pkg>: import failed -> <reason>` to stderr and continues with the rest; partial regeneration is safe.
