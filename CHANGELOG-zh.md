<p align="right"><a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/lang-English-blue?style=for-the-badge" alt="English"></a></p>

# 更新日志

本文件记录本项目所有值得关注的变更。

格式参照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。

## [26.06] - 2026-06-29

面向 **RAPIDS 26.06** + **CUDA 13**(`cu13` wheels)的刷新。仓库内置的 API 索引
基于真实的 `26.06.00` 环境重新生成,RAPIDS 26.06 新增的独立森林推理库
**nvForest** 也纳入了 skill 引导的技术栈。

### 新增

- **nvForest 覆盖。** `nvforest` 是独立的 GPU/CPU 森林*推理*库,取代 cuML 的
  Forest Inference Library(FIL):
  - `apis/nvforest.txt` —— `load_model` / `load_from_sklearn` /
    `load_from_treelite_model` 以及
    `{CPU,GPU}ForestInference{Classifier,Regressor}` 类(`.predict` /
    `.predict_proba` / `.apply` / `.optimize`)的平铺索引。
  - `cpu-rapids-cuda-mapping.tsv` —— 新增 `xgboost`、`lightgbm`、`treelite`
    以及已弃用的 `cuml.ForestInference` 到 `nvforest` 的映射行。
  - `SKILL.md` —— 新增 **Example 5**(加速 XGBoost / LightGBM / RandomForest
    推理),并在场景清单与目录结构中补充森林推理说明。
  - `fetch_rapids_apis.py` —— `nvforest` 加入默认抓取列表(现共 **13** 个包),
    其内部 `detail` / `benchmark` 子树被跳过。
- **`.gitignore`** —— 忽略 import cudf / cucim / pylibraft 时 cuFile / GPUDirect
  Storage 生成的 `cufile.log`,使重新生成索引不再污染工作区。

### 变更

- **重新生成全部 13 个包的 `apis/<pkg>.txt`**,基于 RAPIDS `26.06.00`
  (CuPy `14.1.1`),捕获新的 API 表面 —— 例如 cuVS 新增 `cuvs.preprocessing.pca`,
  `cuml.accel` 覆盖更多预处理 estimator。
- **README / CHANGELOG 的环境表**更新为 26.06 / CUDA 13.2 / CuPy 14.1.1 环境,
  并加入 `nvforest 26.06.00`;README 还补充了 `cu13` 的 pip 安装命令与 CUDA 13
  的最低驱动要求(≥ 580.65.06)。
- **Quick demo 数字**在 RAPIDS 26.06 上重新测量(pandas `0.85 秒` →
  cudf `0.06 秒`,约 15×;RTX 4060 Ti,cudf 26.06.00,pandas 2.3.3)。

### 说明

- `cuml.fil` / `cuml.ForestInference`(FIL)在 **RAPIDS 26.06 中已弃用**,
  推荐改用 `nvforest`;它仍可 import,但新的森林推理代码应以 `nvforest` 为目标。
- 零代码加速器的激活方式在 26.06 **保持不变**:`cudf.pandas`、`cuml.accel`
  (含 `CUML_ACCEL_ENABLED=1`)、`nx-cugraph`(`NX_CUGRAPH_AUTOCONFIG=True`)
  以及 `dask-cudf` backend 均沿用 26.02 时期的语法。

### 抓取环境

仓库内置的 `apis/<pkg>.txt` 基于以下环境重新生成:

| 组件         | 版本                |
|--------------|---------------------|
| Python       | 3.12.13             |
| CUDA runtime | 13.2                |
| cupy         | 14.1.1              |
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

## [26.02] - 2026-05-14

**rapids-first** 首个公开发布版本 —— 一个适用于 Claude Code 与 Codex 的 skill,
将 Python 代码生成主动引向 RAPIDS GPU 栈,自动选择 `cupy`、`cudf`、`cuml`、
`cugraph`、`cucim`、`cuvs` 等,取代对应的 CPU 库。

### 新增

- **Skill 内容**(位于 `skills/rapids-first/`):
  - `SKILL.md` —— 完整的 RAPIDS-first 工作流、API 检索范例、GPU 数据生命周期
    纪律以及「不要做的事」清单。仅当用户在请求中包含字面 token `rapids-first`
    时启用。
  - `cpu-rapids-cuda-mapping.tsv` —— CPU 库(`numpy`、`pandas`、`scikit-learn`、
    `scipy`、`networkx`、`scikit-image`、`faiss` 等)到其 RAPIDS / CUDA 对应物
    的映射表,包含零代码加速路径(`cudf.pandas`、`cuml.accel`、
    `nx-cugraph` backend、`dask-cudf` backend)。
  - `fetch_rapids_apis.py` —— API 索引的确定性重生成脚本,输出按 qualname 字典
    序排序,RAPIDS 升级后用 `git diff` 即可立刻看出 API 表面变化;某个包 import
    失败时在 stderr 打印 `[skip] <pkg>: ...` 并继续处理其余包,不会中断整个流程。
  - `apis/<pkg>.txt` —— 预生成的平铺 API 索引,覆盖 `cupy`、`cupyx`、`cudf`、
    `dask_cudf`、`cuml`、`cugraph`、`nx_cugraph`、`cuxfilter`、`cucim`、
    `pylibraft`、`raft_dask`、`cuvs`。一次 `ripgrep` 即拿到精确签名与首行
    docstring,不靠记忆瞎写。
- **顶层文档**:
  - `README.md`(英文)与 `README-zh.md`(简体中文),包含 quick demo
    (pandas → cudf 改写,~17× 加速)、Claude Code 与 Codex 的安装步骤、
    API 索引抓取环境表以及重新生成步骤。
  - `LICENSE`(MIT)。
- **安装路径**:
  - 推荐:`gh skill install TioSisai/rapids-first rapids-first`
    (`--agent claude-code` 或 `--agent codex`,`--scope user` 或项目级)。
  - 备选:`git clone` 后将 `skills/rapids-first/` 搬入目标 agent 的 skill 目录
    (`~/.claude/skills/` 或 `~/.agents/skills/`,以及对应的项目级位置)。

### 抓取环境

仓库内置的 `apis/<pkg>.txt` 基于以下环境抓取:

| 组件         | 版本                |
|--------------|---------------------|
| Python       | 3.12.13             |
| CUDA runtime | 12.9                |
| cupy         | 14.0.1              |
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

升级 RAPIDS 或本地版本与上表不一致时,用
`python <skill-dir>/fetch_rapids_apis.py` 重新生成。

[26.06]: https://github.com/TioSisai/rapids-first/releases/tag/v26.06
[26.02]: https://github.com/TioSisai/rapids-first/releases/tag/v26.02
