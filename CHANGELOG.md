<p align="right"><a href="./CHANGELOG-zh.md"><img src="https://img.shields.io/badge/lang-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-blue?style=for-the-badge" alt="简体中文"></a></p>

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [26.08] - 2026-08-28

**rapids-first now targets a trimmed RAPIDS core instead of the full stack.**
The skill covers four packages, `cupy`, `cupyx`, `cudf` and `cuml`, down from the
thirteen it tracked in 26.06. The shipped API index is regenerated
against a live RAPIDS `26.08.00` / CUDA 13 install on an **NVIDIA GH200**.

This is a scope decision rather than a temporary gap. `fetch_rapids_apis.py`
defaults to those four packages, so regenerating on a full RAPIDS install still
produces four index files. Pass `--packages` to index whatever else your
environment provides, and add the matching `cpu-rapids-cuda-mapping.tsv` rows by
hand.

### Removed

- **Nine API index files** for the packages that left the covered set:
  `cucim.txt`, `cugraph.txt`, `cuvs.txt`, `cuxfilter.txt`, `dask_cudf.txt`,
  `nvforest.txt`, `nx_cugraph.txt`, `pylibraft.txt`, `raft_dask.txt`.
- **Every mapping row, zero-code entry, example, and doc sentence** that pointed
  at those packages, including the `nx-cugraph` and `dask-cudf` zero-code
  backends and the whole nvForest forest-inference **Example 5** added in 26.06.
- **Capabilities the trimmed stack drops**: graph algorithms, image and
  whole-slide I/O, CAGRA-class ANN indexes, multi-GPU / out-of-core dataframes,
  dashboards, and GPU forest inference for XGBoost and LightGBM models.

### Changed

- **Regenerated `apis/<pkg>.txt` for the four surviving packages** against
  RAPIDS `26.08.00`: `cupy` 1067, `cupyx` 1453, `cudf` 4779, `cuml` 3290, for
  **10589** entries total.
- **`fetch_rapids_apis.py`** — `DEFAULT_PACKAGES` cut from **13** packages to
  **4**; the `cugraph` and `nvforest` skip entries removed; `cuml.benchmark`
  newly skipped as a standalone benchmarking harness rather than an estimator
  API.
- **`cpu-rapids-cuda-mapping.tsv` retargeted** — `faiss`, `hnswlib`, `annoy`,
  `scann`, and `pynndescent` now point at `cuml.neighbors.NearestNeighbors`,
  and `sklearn.metrics.pairwise_distances` at
  `cuml.metrics.pairwise_distances`.
- **Corrected zero-code claims.** `cuml.accel` leaves `sklearn.naive_bayes`,
  `sklearn.metrics`, `sklearn.feature_extraction`, `sklearn.random_projection`,
  `sklearn.model_selection`, `sklearn.multiclass`, and `sklearn.compose` on the
  CPU, so those rows now read `-`; each keeps an explicit cuML equivalent.
  `cuml.accel` newly covers `sklearn.covariance` and `sklearn.kernel_ridge`,
  and patches `sklearn.compose` / `sklearn.pipeline` for interoperability
  without proxying an estimator.
- **Quick-demo numbers re-measured** on 1× NVIDIA GH200 120GB (pandas `3.0.3`
  `0.59 s` → cudf `26.08.00` `0.019 s`, ~31×).
- **README / README-zh environment tables** cut to Python 3.12.14, CUDA 13.2,
  cupy 14.2.0, cudf 26.08.00, cuml 26.08.00; the pip install line trimmed to
  `cudf-cu13` / `cuml-cu13` / `cupy-cuda13x`.
- **`.gitignore`** — the `cufile.log` comment names cudf alone as the producer,
  since cucim and pylibraft are no longer part of the stack.

### Added

- **New 26.08 API surface** captured by the regenerated index:
  - `cuml.IsolationForest` — GPU-accelerated Isolation Forest for anomaly
    detection, now at cuML top level.
  - `cuml.Lars` — Least Angle Regression, promoted to cuML top level out of
    `cuml.experimental.linear_model`.
  - `cupyx.scipy.sparse.csr_array` / `csc_array` / `coo_array` / `dia_array` —
    the SciPy-style sparse **array** classes, alongside the existing matrix
    classes (CuPy `14.2.0`).
- **`SKILL.md`** — a bullet naming what this trimmed stack leaves uncovered, so
  the assistant says so instead of inventing an API.

### Notes

- `nvforest 26.08.00` and `pylibraft 26.08.00` remain installed in the target
  environment as transitive dependencies of cuML and cuDF, and stay
  **out of scope** for the skill.
- **cudf 26.08 tracks pandas 3.0.** `applymap`, `backfill`, `pad`, `first`,
  `last`, `values_host`, and the `Index.is_*` dtype predicates are gone;
  `DataFrame.flags` / `set_flags` and `cudf.api.types.is_dtype_obj_numeric` /
  `is_dtype_obj_string` are new.
- The index no longer carries `cuml.dask`, because `dask` is absent from the
  target environment.
- Zero-code activation syntax for `cudf.pandas` and `cuml.accel` is
  **unchanged** from 26.06.

### Environment

Pre-built `apis/<pkg>.txt` files were regenerated against:

| Component    | Version            |
|--------------|--------------------|
| Python       | 3.12.14            |
| CUDA runtime | 13.2               |
| GPU          | NVIDIA GH200 120GB |
| cupy         | 14.2.0             |
| cudf         | 26.08.00           |
| cuml         | 26.08.00           |

## [26.06] - 2026-06-29

Refresh for **RAPIDS 26.06** on **CUDA 13** (`cu13` wheels). The shipped API
index is regenerated against a live `26.06.00` environment, and **nvForest** —
the new standalone forest-inference library introduced in RAPIDS 26.06 — joins
the stack the skill steers toward.

### Added

- **nvForest coverage.** `nvforest` is the standalone GPU/CPU forest-*inference*
  library that supersedes cuML's Forest Inference Library (FIL):
  - `apis/nvforest.txt` — flat index for `load_model` / `load_from_sklearn` /
    `load_from_treelite_model` and the
    `{CPU,GPU}ForestInference{Classifier,Regressor}` classes (`.predict` /
    `.predict_proba` / `.apply` / `.optimize`).
  - `cpu-rapids-cuda-mapping.tsv` — new rows mapping `xgboost`, `lightgbm`,
    `treelite`, and the deprecated `cuml.ForestInference` to `nvforest`.
  - `SKILL.md` — a new **Example 5** for accelerating XGBoost / LightGBM /
    RandomForest inference, plus a forest-inference note in the scenarios list
    and the directory listing.
  - `fetch_rapids_apis.py` — `nvforest` added to the default package list (now
    **13** packages); its internal `detail` / `benchmark` subtrees are skipped.
- **`.gitignore`** — ignores the `cufile.log` that cuFile / GPUDirect Storage
  emits when importing cudf / cucim / pylibraft, so regenerating the index no
  longer dirties the working tree.

### Changed

- **Regenerated `apis/<pkg>.txt` for all 13 packages** against RAPIDS `26.06.00`
  (CuPy `14.1.1`), capturing the new API surface — e.g. cuVS gains
  `cuvs.preprocessing.pca`, and `cuml.accel` covers more preprocessing
  estimators.
- **README / CHANGELOG environment tables** updated to the 26.06 / CUDA 13.2 /
  CuPy 14.1.1 environment, with `nvforest 26.06.00` added; the README also
  documents the `cu13` pip install and the CUDA 13 driver floor (≥ 580.65.06).
- **Quick-demo numbers re-measured** on RAPIDS 26.06 (pandas `0.85 s` →
  cudf `0.06 s`, ~15×; RTX 4060 Ti, cudf 26.06.00, pandas 2.3.3).

### Notes

- `cuml.fil` / `cuml.ForestInference` (FIL) is **deprecated in RAPIDS 26.06** in
  favor of `nvforest`; it still imports but new forest-inference code should
  target `nvforest`.
- Zero-code accelerator activation is **unchanged** in 26.06: `cudf.pandas`,
  `cuml.accel` (incl. `CUML_ACCEL_ENABLED=1`), `nx-cugraph`
  (`NX_CUGRAPH_AUTOCONFIG=True`), and the `dask-cudf` backend keep their
  26.02-era syntax.

### Environment

Pre-built `apis/<pkg>.txt` files were regenerated against:

| Component    | Version           |
|--------------|-------------------|
| Python       | 3.12.13           |
| CUDA runtime | 13.2              |
| cupy         | 14.1.1            |
| cudf         | 26.06.00          |
| dask_cudf    | 26.06.00          |
| cuml         | 26.06.00          |
| cugraph      | 26.06.00          |
| nx_cugraph   | 26.06.00          |
| cuxfilter    | 26.06.00          |
| cucim        | 26.06.00          |
| pylibraft    | 26.06.00          |
| raft_dask    | 26.06.00          |
| cuvs         | 26.06.00          |
| nvforest     | 26.06.00          |

## [26.02] - 2026-05-14

Initial public release of **rapids-first** — a skill for Claude Code and Codex
that steers Python code generation toward the RAPIDS GPU stack, automatically
choosing `cupy`, `cudf`, `cuml`, `cugraph`, `cucim`, `cuvs`, and friends over
their CPU counterparts.

### Added

- **Skill payload** at `skills/rapids-first/`:
  - `SKILL.md` — full RAPIDS-first workflow, API search recipes,
    GPU data-lifecycle discipline, and "what not to do" guardrails. The skill
    activates only when the literal token `rapids-first` appears in the user
    request.
  - `cpu-rapids-cuda-mapping.tsv` — curated mapping from CPU libraries
    (`numpy`, `pandas`, `scikit-learn`, `scipy`, `networkx`, `scikit-image`,
    `faiss`, …) to their RAPIDS / CUDA equivalents, including zero-code
    accelerators (`cudf.pandas`, `cuml.accel`, `nx-cugraph` backend,
    `dask-cudf` backend).
  - `fetch_rapids_apis.py` — deterministic regenerator for the per-package API
    index. Output is sorted by qualname so a `git diff` immediately surfaces
    RAPIDS API-surface changes after an upgrade; failed imports are reported
    on stderr and skipped without aborting the run.
  - `apis/<pkg>.txt` — pre-built flat API indexes for `cupy`, `cupyx`, `cudf`,
    `dask_cudf`, `cuml`, `cugraph`, `nx_cugraph`, `cuxfilter`, `cucim`,
    `pylibraft`, `raft_dask`, and `cuvs`. One `ripgrep` over these files
    recovers the exact signature and first-line docstring without guessing
    from memory.
- **Top-level documentation**:
  - `README.md` (English) and `README-zh.md` (Simplified Chinese), with a
    quick demo (pandas → cudf rewrite, ~17× speed-up), installation
    instructions for both Claude Code and Codex, the captured API-index
    environment table, and regeneration steps.
  - `LICENSE` (MIT).
- **Installation paths**:
  - Recommended: `gh skill install TioSisai/rapids-first rapids-first`
    (`--agent claude-code` or `--agent codex`, `--scope user` or project).
  - Manual: `git clone` followed by moving `skills/rapids-first/` into the
    target agent's skill directory (`~/.claude/skills/` or `~/.agents/skills/`,
    or their project-local equivalents).

### Environment

Pre-built `apis/<pkg>.txt` files were captured against:

| Component    | Version           |
|--------------|-------------------|
| Python       | 3.12.13           |
| CUDA runtime | 12.9              |
| cupy         | 14.0.1            |
| cudf         | 26.02.01          |
| dask_cudf    | 26.02.01          |
| cuml         | 26.02.000         |
| cugraph      | 26.02.00          |
| nx_cugraph   | 26.02.000         |
| cuxfilter    | 26.02.000         |
| cucim        | 26.02.01          |
| pylibraft    | 26.02.00          |
| raft_dask    | 26.02.00          |
| cuvs         | 26.02.000         |

Regenerate with `python <skill-dir>/fetch_rapids_apis.py` when upgrading
RAPIDS or when local versions diverge from the table above.

[26.08]: https://github.com/TioSisai/rapids-first/releases/tag/v26.08-cuml-cudf-only
[26.06]: https://github.com/TioSisai/rapids-first/releases/tag/v26.06
[26.02]: https://github.com/TioSisai/rapids-first/releases/tag/v26.02
