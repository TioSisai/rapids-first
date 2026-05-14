---
name: rapids-first
description: Prefer the RAPIDS stack for GPU acceleration. Use this skill if and only if the user's request explicitly contains "rapids-first". It covers all "writing Python code" scenarios: rewriting existing CPU code, implementing new features/algorithms, creating new scripts (ETL/training/inference/batch processing), adding new tests, fixing bugs — by default, prefer RAPIDS APIs (cupy / cudf / cuml / cugraph / cucim / cupyx.scipy / cuvs / dask-cudf / nx-cugraph, etc.) as substitutes for the corresponding numpy / pandas / scikit-learn / scipy / networkx / scikit-image / faiss / umap / hdbscan / dask.dataframe; and preferentially adopt the "zero-code" acceleration mechanisms provided by RAPIDS (cudf.pandas, cuml.accel, nx-cugraph backend, dask-cudf backend), only manually modifying imports when zero-code does not apply. Whenever scenarios involve RAPIDS, GPU dataframes, GPU scikit-learn, GPU vector search, GPU graph algorithms, etc., as long as the user mentions rapids-first, this skill must be used.
---

# RAPIDS-first

## When to Enable

Enable this skill if and only if the user's request explicitly contains `rapids-first` (or the synonymous wording "RAPIDS first"). Do not apply it proactively in other scenarios, to avoid modifying code outside the user's expectations.

## Applicable Scenarios

Once rapids-first is enabled, **all "writing Python code" subtasks** are handled according to the RAPIDS-first principle, not limited to rewriting existing CPU code:

1. **Rewriting existing CPU code**: replace numpy / pandas / sklearn / scipy / networkx / skimage / faiss / umap / hdbscan / dask.dataframe calls with the corresponding RAPIDS APIs.
2. **Adding new features / implementing new algorithms**: when writing implementations from scratch, prefer RAPIDS APIs as the foundation rather than numpy / scipy / sklearn. Example: for matrix decomposition → directly choose `cuml.decomposition` over `sklearn.decomposition`; for nearest neighbors → directly choose `cuvs.neighbors` / `cuml.neighbors` over `faiss` / `sklearn.neighbors`.
3. **Creating new scripts (ETL / training / inference / batch processing)**: use `cudf.read_*` / `dask_cudf.read_*` for data loading, `cupy` for matrix computation, `cudf` + `cuml.preprocessing` for feature engineering, `cuml` / `cugraph` for model training, `cucim.skimage` / `cupyx.scipy.ndimage` for image processing.
4. **Adding new tests**: use RAPIDS as much as possible for test data generation and assertion comparison (`cudf.testing` / `cuml.testing`, etc.); let numpy / pandas appear only for RAPIDS↔CPU numerical comparisons, with a one-shot conversion at the boundary.
5. **Fixing bugs**: even when just fixing a single numpy function call, if a suitable RAPIDS equivalent exists in the context, replace it in passing.

In short: after enabling this skill, "think first how to do it with RAPIDS" takes priority over "think first how to do it with numpy / pandas / sklearn". Only fall back to the CPU path when the RAPIDS stack truly has no corresponding implementation.

## Three Core Principles

1. **Zero-code acceleration first**: RAPIDS provides monkey-patch or backend-dispatch mechanisms for the most common CPU libraries (pandas, sklearn, umap, hdbscan, networkx, dask.dataframe), allowing existing CPU code to run on GPU without changing any imports. Use zero-code whenever possible — especially in the "rewriting existing CPU code" scenario.
2. **Avoid redundant CPU↔GPU conversions**: once data is on GPU, keep it on GPU as much as possible, minimizing calls like `.to_pandas()` / `.to_numpy()` / `.get()` that trigger device synchronization and copying; only do a one-shot downlink at the pipeline endpoint or at necessary output/visualization boundaries. Mixing `cupy.ndarray` with `numpy.ndarray` (or `cudf.DataFrame` with `pandas.DataFrame`) triggers implicit synchronization and should be proactively eliminated.
3. **Precise API targeting**: this skill directory ships a complete API index `apis/<pkg>.txt` for each RAPIDS package, with each line formatted as "full path(signature) - first line of docstring". A single `ripgrep` search retrieves both the call syntax and purpose, **avoiding writing signatures from memory** (cuML and sklearn often differ in parameter order, default values, `output_type`, etc.).

## Directory Structure

```
<this skill's root directory>/
├── SKILL.md                       # This file
├── cpu-rapids-cuda-mapping.tsv    # Index of CPU library → RAPIDS package (TSV)
├── fetch_rapids_apis.py           # Script that (re-)generates apis/<pkg>.txt
└── apis/                          # One API index file per package
    ├── cupy.txt                   # CuPy (replaces numpy)
    ├── cupyx.txt                  # CuPy.scipy and other extensions (replaces scipy)
    ├── cudf.txt                   # cuDF (replaces pandas)
    ├── dask_cudf.txt              # dask-cuDF
    ├── cuml.txt                   # cuML (replaces scikit-learn / umap / hdbscan / statsmodels.tsa)
    ├── cugraph.txt                # cuGraph (explicit graph algorithm APIs)
    ├── nx_cugraph.txt             # nx-cugraph (NetworkX backend)
    ├── cuxfilter.txt              # cuXfilter
    ├── cucim.txt                  # cuCIM (replaces scikit-image / openslide)
    ├── pylibraft.txt              # RAFT primitives
    ├── raft_dask.txt              # RAFT-Dask communication layer
    └── cuvs.txt                   # cuVS (replaces faiss and other vector search)
```

## Standard Workflow

### Step 1: Identify the CPU library to replace/select

- **Rewrite scenario**: scan the user's code to find the imports to accelerate (`import numpy as np`, `import pandas as pd`, `from sklearn.cluster import KMeans`, `import scipy.ndimage`, `import networkx as nx`, `from skimage import ...`, `import faiss / hnswlib / umap / hdbscan`, `import dask.dataframe as dd`, etc.).
- **New code scenario**: against the functional requirements, **first mentally write out "if using a CPU library, which one would I use"** (pandas? sklearn? scipy?), then follow the steps below to convert it to RAPIDS.

### Step 2: Use ripgrep on mapping.tsv to locate the RAPIDS package

`cpu-rapids-cuda-mapping.tsv` fields:

```
cpu_module  rapids_target  zero_code  notes
```

For an exact top-level package lookup use `^pkg\t`; for fuzzy submodule lookup use plain grep:

```bash
rg -P '^pandas\t'            cpu-rapids-cuda-mapping.tsv
rg -P '^sklearn\.cluster\t'  cpu-rapids-cuda-mapping.tsv
rg -P '^scipy\.ndimage\t'    cpu-rapids-cuda-mapping.tsv
rg -P '^networkx\t'          cpu-rapids-cuda-mapping.tsv
rg -i 'faiss'                cpu-rapids-cuda-mapping.tsv
```

Read out `rapids_target` (target import path) and `zero_code` (zero-code solution identifier).

### Step 3: Check whether the zero-code solution applies

If the `zero_code` field is not `-` and the scenario allows it (primarily "rewriting existing CPU code"), prefer the zero-code solution. Canonical activation methods:

| zero_code identifier | Activation method |
|---|---|
| `cudf.pandas` | CLI: `python -m cudf.pandas script.py`<br>Jupyter first cell: `%load_ext cudf.pandas`<br>In-program (must precede `import pandas`): `import cudf.pandas; cudf.pandas.install()` |
| `cuml.accel` | CLI: `python -m cuml.accel script.py`<br>Jupyter first cell: `%load_ext cuml.accel`<br>Environment variable: `CUML_ACCEL_ENABLED=1`<br>In-program (must precede `import sklearn` / `umap` / `hdbscan`): `from cuml.accel import install; install()` |
| `nx-cugraph-backend` | Environment variable: `NX_CUGRAPH_AUTOCONFIG=True` (automatic)<br>Or single call: `nx.pagerank(G, backend="cugraph")`<br>Or config: `nx.config.backend_priority = ["cugraph"]` (NetworkX ≥ 3.2) |
| `dask-cudf-backend` | `dask.config.set({"dataframe.backend": "cudf"})`, continue using `dask.dataframe`; often combined with `dask_cuda.LocalCUDACluster` |

Once a zero-code solution is enabled, **the original code does not need any import changes**; unsupported APIs automatically fall back to CPU without raising errors.

**Applicability decision**:
- Rewrite scenario + user wants "to make existing code run faster" → zero-code
- New code / user wants explicit GPU APIs / user wants the code to clearly read as using RAPIDS → proceed to the explicit import in Step 4

### Step 4: Explicit import replacement (when zero-code does not apply, or when writing new code)

Two-step API location:

1. Get `rapids_target` from mapping.tsv. Examples: `numpy → cupy`, `scipy.ndimage → cupyx.scipy.ndimage`, `sklearn.cluster → cuml.cluster`, `faiss → cuvs.neighbors`.

2. Search for the target API in `apis/<pkg>.txt` using `ripgrep`:

   ```bash
   # Search for a class: exact match of class name followed by ( or .
   rg -i '\.KMeans\(' apis/cuml.txt
   rg -i '^cuml\.cluster\.KMeans' apis/cuml.txt

   # Search for a function: similarly match .funcname(
   rg -i '\.gaussian_filter\(' apis/cupyx.txt
   rg -i '\.read_parquet\(' apis/cudf.txt
   rg -i '\.fft2\(' apis/cupy.txt

   # Search for all APIs under a given submodule
   rg '^cuml\.cluster\.' apis/cuml.txt
   rg '^cuvs\.neighbors\.cagra\.' apis/cuvs.txt

   # Search multiple files at once
   rg -i '\.PCA\(' apis/cuml.txt apis/cuvs.txt
   ```

   Each matched line is formatted as "full path(signature) - first line of docstring"; **copy the signature directly when writing code**.

### Step 5: Respect the GPU data lifecycle

- **Continuous GPU pipeline**: avoid mid-stream round-trips like `cudf.to_pandas() → processing → cudf.from_pandas()`. If some intermediate step does not yet provide a GPU version, search `apis/*.txt` once more to confirm before falling back.
- **No device mixing**: mixing `cupy.ndarray` with `numpy.ndarray`, or `cudf.DataFrame` with `pandas.DataFrame`, triggers implicit copying and forces stream synchronization. All array types within the same computation graph should be consistent.
- **I/O lands directly on GPU**: use `cudf.read_csv` / `cudf.read_parquet` / `cudf.read_orc` / `cudf.read_json`, etc., to go from disk straight to GPU memory, rather than `pandas.read_*` followed by an upload; the same applies to `cuml.preprocessing`, which works directly on cuDF.
- **Default dtypes**: some cuDF / cuML operators default to `float32`, while sklearn defaults to `float64`. For high-precision comparisons, explicitly pass `dtype=cupy.float64` or `convert_dtype=False`.
- **Fail-fast, no existence checks**: importing a RAPIDS package already requires CUDA to be available; do not write defensive fallbacks like `try: import cupy except: import numpy as cupy` — if the environment is missing, let it fail directly.

## Search Examples

### Example 1: Accelerate `from sklearn.cluster import KMeans` to GPU (rewrite scenario)

```
$ rg -P '^sklearn\.cluster\t' cpu-rapids-cuda-mapping.tsv
sklearn.cluster	cuml.cluster	cuml.accel	KMeans, DBSCAN, HDBSCAN, AgglomerativeClustering
```

- **Zero-code preferred**: have the user run with `python -m cuml.accel script.py`; the original code stays untouched.
- **Explicit replacement** (if the user prefers):
  ```
  $ rg -i '^cuml\.cluster\.KMeans\(' apis/cuml.txt
  cuml.cluster.KMeans(*, handle=None, n_clusters=8, max_iter=300, tol=0.0001, ...) - KMeans is a basic but powerful clustering method ...
  ```
  Per the signature, change directly to `from cuml.cluster import KMeans`.

### Example 2: Implement a matrix FFT pipeline from scratch (new code scenario)

Requirement: perform fft2 + magnitude + normalization on a batch of 2D matrices.

1. "If using CPU, I would use numpy.fft + numpy" → look up the mapping:
   ```
   $ rg -P '^numpy(\.fft)?\t' cpu-rapids-cuda-mapping.tsv
   numpy	cupy	-	import cupy as cp; substitute cp for np
   numpy.fft	cupy.fft	-	-
   ```
2. Look up the specific API:
   ```
   $ rg -i '\.fft2\(' apis/cupy.txt
   cupy.fft.fft2(a, s=None, axes=(-2, -1), norm=None) - Compute the two-dimensional FFT.
   ```
3. Write the code: a one-shot upload via `cp.asarray` → `cp.fft.fft2` → `cp.abs` → `cp.linalg.norm`, all done on GPU, then `.get()` or write the file output at the very end.

### Example 3: Write unit tests for a new algorithm implementation (new test scenario)

Requirement: test that a GPU-implemented PCA produces numerically consistent results with sklearn's PCA.

1. Data generation: `cuml.datasets.make_blobs(...)` or `cupy.random.RandomState(seed).normal(...)` — **not** `sklearn.datasets` / `numpy.random`.
2. Run on GPU: `cuml.decomposition.PCA(...).fit_transform(X)`.
3. CPU comparison: one-shot downlink with `X.get()` → `sklearn.decomposition.PCA(...).fit_transform(X_cpu)`.
4. Assertion: `cupy.testing.assert_allclose(...)`, or `numpy.testing.assert_allclose` on the CPU side (because the comparison target is numpy).
5. Across the whole process, data transfer happens only once, at step 3.

### Example 4: Replace faiss for ANN search (rewrite scenario)

```
$ rg -i 'faiss' cpu-rapids-cuda-mapping.tsv
faiss	cuvs.neighbors	-	ANN vector search; CAGRA/IVF-Flat/IVF-PQ/HNSW/Brute-Force ...

$ rg '^cuvs\.neighbors\.cagra\.' apis/cuvs.txt | head
cuvs.neighbors.cagra.IndexParams(...) - ...
cuvs.neighbors.cagra.SearchParams(...) - ...
cuvs.neighbors.cagra.build(index_params, dataset, ...) - ...
cuvs.neighbors.cagra.search(search_params, index, queries, k, ...) - ...
```

Rewrite per the signatures: `build` builds the index, `search` queries k-nearest neighbors. CAGRA is cuVS's flagship GPU graph index.

## When RAPIDS Has No Corresponding Implementation

Handle by priority:
1. Search for similar keywords again in `apis/<pkg>.txt`. RAPIDS naming often differs slightly from sklearn / scipy (e.g., sklearn's `cross_val_score` has no direct counterpart in cuml, but can be reproduced with `train_test_split` plus a handwritten loop; sklearn's `Pipeline` is also absent in cuml but can be chained manually).
2. Check neighboring packages: when a scikit-image operator is not found in cuCIM, see whether `cupyx.scipy.ndimage` / `cupy` can implement it by hand.
3. When there is still no counterpart, **explicitly tell the user that the operator is not in the current RAPIDS stack**, then use the CPU version and consolidate data transfers at the CPU↔GPU boundary to minimize the number of transfers (ideal: the entire pipeline does `.get()` / `.to_pandas()` only once at the end).

## (Re-)Generating apis/

- After any RAPIDS package upgrade, run `python fetch_rapids_apis.py` to regenerate `apis/<pkg>.txt`.
- You can also target specific packages only: `python fetch_rapids_apis.py --packages cudf cuml`.
- The script must run in "a Python environment with RAPIDS installed" and requires the CUDA driver to be visible.

## What Not to Do

- **Do not proactively enable** `cudf.pandas` / `cuml.accel` — monkey-patches affect the entire Python process, so **let the user decide** whether to turn it on; your job is only to inform them of the activation command.
- **Do not write try/except defenses for "is GPU available"**; the presence of RAPIDS packages itself assumes CUDA is available — if the environment is missing, let it fail-fast.
- **Do not convert every numpy / pandas call to cupy / cudf** — in rewrite scenarios, the user may only want to accelerate the hot path; check the context before deciding the scope of refactoring.
- **Do not write RAPIDS API signatures from memory**; first `rg` once into `apis/<pkg>.txt` to get the accurate signature (cuml and sklearn often differ in `n_init`, `output_type`, keyword-only parameters, etc.).
- **Do not let data downlink mid-stream**; place `cudf.DataFrame.to_pandas()` only at the very end of the pipeline or at necessary integration points (plotting, writing compatible output formats, etc.).
