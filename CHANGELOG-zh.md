<p align="right"><a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/lang-English-blue?style=for-the-badge" alt="English"></a></p>

# 更新日志

本文件记录本项目所有值得关注的变更。

格式参照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。

## [26.08] - 2026-08-28

**rapids-first 的覆盖范围从完整 RAPIDS 栈收窄为精简核心。**skill 现在覆盖
`cupy`、`cupyx`、`cudf`、`cuml` 四个包,26.06 时期跟踪的是十三个。仓库
内置的 API 索引基于 **NVIDIA GH200** 上真实的 RAPIDS `26.08.00` + CUDA 13 安装
重新生成。

这是一次范围决策,而非临时缺口。`fetch_rapids_apis.py` 的默认抓取列表就是这四个
包,在装有完整 RAPIDS 的环境里重新生成同样只产出四个索引文件。需要索引本地环境
提供的其他包时,用 `--packages` 指定,并自行补上对应的
`cpu-rapids-cuda-mapping.tsv` 映射行。

### 移除

- **九个 API 索引文件**,对应退出覆盖范围的包:`cucim.txt`、`cugraph.txt`、
  `cuvs.txt`、`cuxfilter.txt`、`dask_cudf.txt`、`nvforest.txt`、`nx_cugraph.txt`、
  `pylibraft.txt`、`raft_dask.txt`。
- **指向这些包的全部映射行、零代码条目、示例与文档表述**,包括 `nx-cugraph` 与
  `dask-cudf` 两条零代码 backend,以及 26.06 新增的整个 nvForest 森林推理
  **Example 5**。
- **精简后的技术栈不再覆盖的能力**:图算法、图像与全切片 I/O、CAGRA 类 ANN 索引、
  多 GPU / 外存 dataframe、可视化面板,以及针对 XGBoost 与 LightGBM 模型的 GPU
  森林推理。

### 变更

- **基于 RAPIDS `26.08.00` 重新生成保留下来的四个包的 `apis/<pkg>.txt`**:
  `cupy` 1067、`cupyx` 1453、`cudf` 4779、`cuml` 3290,合计 **10589** 条。
- **`fetch_rapids_apis.py`** —— `DEFAULT_PACKAGES` 从 **13** 个包缩减到 **4** 个;
  移除 `cugraph` 与 `nvforest` 的跳过项;新增跳过 `cuml.benchmark`,它是独立的
  benchmark 工具,不是 estimator API。
- **`cpu-rapids-cuda-mapping.tsv` 重新对齐** —— `faiss`、`hnswlib`、`annoy`、
  `scann`、`pynndescent` 现指向 `cuml.neighbors.NearestNeighbors`,
  `sklearn.metrics.pairwise_distances` 指向 `cuml.metrics.pairwise_distances`。
- **修正零代码相关表述。** `cuml.accel` 将 `sklearn.naive_bayes`、
  `sklearn.metrics`、`sklearn.feature_extraction`、`sklearn.random_projection`、
  `sklearn.model_selection`、`sklearn.multiclass` 与 `sklearn.compose` 留在
  CPU 上,这些行的零代码列改为 `-`,各自保留显式的 cuML 对应物。`cuml.accel`
  新增覆盖 `sklearn.covariance` 与 `sklearn.kernel_ridge`,并为互操作性 patch
  `sklearn.compose` / `sklearn.pipeline`,但不代理其中的 estimator。
- **Quick demo 数字**在 1× NVIDIA GH200 120GB 上重新测量(pandas `3.0.3`
  `0.59 秒` → cudf `26.08.00` `0.019 秒`,约 31×)。
- **README / README-zh 的环境表**收缩为 Python 3.12.14、CUDA 13.2、cupy 14.2.0、
  cudf 26.08.00、cuml 26.08.00;pip 安装命令精简为 `cudf-cu13` / `cuml-cu13` /
  `cupy-cuda13x`。
- **`.gitignore`** —— `cufile.log` 的注释只保留 cudf 作为产生方,cucim 与
  pylibraft 已不属于这套技术栈。

### 新增

- **重新生成的索引捕获到的 26.08 新 API 表面**:
  - `cuml.IsolationForest` —— GPU 加速的 Isolation Forest 异常检测,现位于
    cuML 顶层。
  - `cuml.Lars` —— 最小角回归,从 `cuml.experimental.linear_model` 提升到
    cuML 顶层。
  - `cupyx.scipy.sparse.csr_array` / `csc_array` / `coo_array` / `dia_array`
    —— SciPy 风格的稀疏 **array** 类,与既有的 matrix 类并存(CuPy `14.2.0`)。
- **`SKILL.md`** —— 新增一条条目,写明这套精简技术栈未覆盖的范围,让助手直接
  说明现状,而不是凭空编造 API。

### 说明

- `nvforest 26.08.00` 与 `pylibraft 26.08.00` 仍作为 cuML 与 cuDF 的传递依赖
  安装在目标环境中,并 **不在 skill 的范围内**。
- **cudf 26.08 跟进 pandas 3.0。** `applymap`、`backfill`、`pad`、`first`、
  `last`、`values_host` 以及 `Index.is_*` 系列 dtype 判定方法已移除;
  `DataFrame.flags` / `set_flags` 与 `cudf.api.types.is_dtype_obj_numeric` /
  `is_dtype_obj_string` 为新增。
- 索引不再包含 `cuml.dask`,目标环境中没有 `dask`。
- `cudf.pandas` 与 `cuml.accel` 的零代码激活语法相对 26.06 **保持不变**。

### 抓取环境

仓库内置的 `apis/<pkg>.txt` 基于以下环境重新生成:

| 组件         | 版本                |
|--------------|---------------------|
| Python       | 3.12.14             |
| CUDA runtime | 13.2                |
| GPU          | NVIDIA GH200 120GB  |
| cupy         | 14.2.0              |
| cudf         | 26.08.00            |
| cuml         | 26.08.00            |

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

[26.08]: https://github.com/TioSisai/rapids-first/releases/tag/v26.08-cuml-cudf-only
[26.06]: https://github.com/TioSisai/rapids-first/releases/tag/v26.06
[26.02]: https://github.com/TioSisai/rapids-first/releases/tag/v26.02
