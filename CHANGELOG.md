<p align="right"><a href="./CHANGELOG-zh.md"><img src="https://img.shields.io/badge/lang-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-blue?style=for-the-badge" alt="简体中文"></a></p>

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[26.02]: https://github.com/TioSisai/rapids-first/releases/tag/v26.02
