<p align="right"><a href="./README.md"><img src="https://img.shields.io/badge/lang-English-blue?style=for-the-badge" alt="English"></a></p>

# rapids-first

一个适用于 Claude Code 与 Codex 的 skill,将 Python 代码生成主动引向 RAPIDS GPU 栈 —— 自动选择 `cupy`、`cudf`、`cuml`、`cugraph`、`cucim`、`cuvs` 等,取代 `numpy`、`pandas`、`scikit-learn`、`scipy`、`networkx`、`scikit-image`、`faiss`。

## 这个 skill 做什么

本 skill **仅当用户在请求中包含 `rapids-first` 时启用**。激活后,所有「写 Python 代码」的子任务 —— 重写现有 CPU 代码、实现新算法、搭建 ETL / 训练 / 推理 / 批处理脚本、新增测试、修 bug —— 都按 RAPIDS-first 原则处理:

- **零代码加速优先**:优先采用 `cudf.pandas` / `cuml.accel` / `nx-cugraph` backend / `dask-cudf` backend,让现有 CPU 代码无需修改任何 import 即可在 GPU 上运行。
- **显式 RAPIDS import**(零代码不适用时):`numpy → cupy`、`scipy.ndimage → cupyx.scipy.ndimage`、`sklearn.cluster → cuml.cluster`、`faiss → cuvs.neighbors` 等等。
- **API 精准命中**:每个 RAPIDS 包都附带一份平铺的 API 索引 `apis/<pkg>.txt`,一次 `ripgrep` 即拿到精确签名与首行 docstring —— 不靠记忆瞎写(cuML 与 sklearn 在参数顺序、默认值、`output_type` 等处常有差异)。
- **GPU 数据生命周期纪律**:尽量减少 `.to_pandas()` / `.get()` 往返,避免 `cupy ↔ numpy` 混用,优先用 `cudf.read_*` 让 I/O 直接落到 GPU。

完整工作流、API 检索范例与「不要做的事」清单见 [SKILL.md](./SKILL.md)。

## 依赖

- [**RAPIDS**](https://rapids.ai/) —— 本 skill 引导使用的 GPU 数据科学栈(`cupy`、`cudf`、`cuml`、`cugraph`、`cucim`、`cuvs`、`nx-cugraph`、`dask-cudf`、`cuxfilter`、`pylibraft`、`raft-dask`)。底层库的 import 需要一块 CUDA 兼容的 NVIDIA GPU 以及匹配的 CUDA driver。
- [**ripgrep(`rg`)**](https://github.com/BurntSushi/ripgrep) —— skill 的标准工作流全程依赖它,从 `apis/<pkg>.txt` 中一次性查到精确的 API 签名。

## 安装

本 skill 是一个自包含的目录,放到所在 CLI 的 skills 根目录下即可。

### Claude Code

用户级(跨所有项目可用):

```bash
git clone https://github.com/TioSisai/rapids-first.git ~/.claude/skills/rapids-first
```

项目级(仅作用于当前项目):

```bash
git clone https://github.com/TioSisai/rapids-first.git .claude/skills/rapids-first
```

### Codex

用户级:

```bash
git clone https://github.com/TioSisai/rapids-first.git ~/.codex/skills/rapids-first
```

Codex 与 Claude Code 一样,会从 `~/.codex/skills/<skill-name>/SKILL.md` 发现 skill。

### 共享安装(一份副本,两个 CLI 共用)

如果你想保留单一工作副本并让两个 CLI 都识别:

```bash
ln -s /absolute/path/to/rapids-first ~/.claude/skills/rapids-first
ln -s /absolute/path/to/rapids-first ~/.codex/skills/rapids-first
```

### 触发方式

安装后重启 CLI(或开新会话)。只要在 prompt 中包含字面 token `rapids-first` 即可触发,例如:

> `rapids-first` 改写这个预处理脚本。

> 用 `rapids-first` 在这份 DataFrame 上实现 KMeans。

## API 索引版本

仓库中预生成的 `apis/<pkg>.txt` 是基于以下环境抓取的:

| 组件         | 版本                |
|--------------|---------------------|
| Python       | 3.12.13             |
| CUDA runtime | 12.9                |
| cupy         | 14.0.1              |
| cupyx        | (随 cupy 一同安装)  |
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

### 何时需要重新生成

以下任一情形都建议重新生成 API 索引:

- 本地任一 RAPIDS 包升级了;
- RAPIDS 发布了新的 minor / major 版本,公共 API 有变化(RAPIDS 按 `YY.MM` 节奏发版);
- 本地环境的 CUDA / RAPIDS 主版本与上表不一致,并观察到签名漂移。

如果上表已与你的环境完全一致,仓库自带的 `apis/` 可直接使用,无需重新生成。

### 如何重新生成

在已安装 RAPIDS 且 CUDA 可见的 Python 环境中,从 skill 根目录运行:

```bash
# 默认抓取全部 12 个包
python fetch_rapids_apis.py

# 只抓取指定包
python fetch_rapids_apis.py --packages cudf cuml

# 输出到其他根目录
python fetch_rapids_apis.py --output-dir /tmp/rapids-apis
```

脚本每次运行都会以确定性方式重写 `apis/<pkg>.txt`(条目按 qualname 字典序排序),`git diff` 可立即看出 API 表面变化 —— 用于审计 RAPIDS 升级很方便。

如果某个包 import 失败(缺少 CUDA driver、库版本错位等),脚本会在 stderr 打印 `[skip] <pkg>: import failed -> <原因>` 并继续处理其余包,部分重新生成是安全的。
