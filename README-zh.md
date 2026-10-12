<p align="right"><a href="./README.md"><img src="https://img.shields.io/badge/lang-English-blue?style=for-the-badge" alt="English"></a></p>

# rapids-first

一个适用于 Claude Code 与 Codex 的 skill,将 Python 代码生成主动引向 RAPIDS GPU 栈 —— 自动选择 `cupy`、`cupyx`、`cudf`、`cuml`,取代 `numpy`、`scipy`、`pandas`、`scikit-learn`、`umap-learn`。

## 这个 skill 做什么

本 skill **仅当用户在请求中包含 `rapids-first` 时启用**。激活后,所有「写 Python 代码」的子任务 —— 重写现有 CPU 代码、实现新算法、搭建 ETL / 训练 / 推理 / 批处理脚本、新增测试、修 bug —— 都按 RAPIDS-first 原则处理:

- **零代码加速优先**:优先采用 `cudf.pandas` / `cuml.accel`,让现有 CPU 代码无需修改任何 import 即可在 GPU 上运行。
- **显式 RAPIDS import**(零代码不适用时):`numpy → cupy`、`scipy.ndimage → cupyx.scipy.ndimage`、`sklearn.cluster → cuml.cluster`、`faiss → cuml.neighbors` 等等。
- **API 精准命中**:四个 RAPIDS 包各自附带一份平铺的 API 索引 `apis/<pkg>.txt`,一次 `ripgrep` 即拿到精确签名与首行 docstring —— 不靠记忆瞎写(cuML 与 sklearn 在参数顺序、默认值、`output_type` 等处常有差异)。
- **GPU 数据生命周期纪律**:尽量减少 `.to_pandas()` / `.get()` 往返,避免 `cupy ↔ numpy` 混用,优先用 `cudf.read_*` 让 I/O 直接落到 GPU。

完整工作流、API 检索范例与「不要做的事」清单见 [SKILL.md](./skills/rapids-first/SKILL.md)。

## Quick demo

在 prompt 里写上字面 token `rapids-first`,skill 就会接管整段改写。

Prompt:

> 用 `rapids-first` 改写这个 pandas 预处理脚本。

改写前 —— **0.60 秒**(5 次取平均,首次 warmup 不计):

```python
import pandas as pd

df = pd.read_parquet("events.parquet")
df["x"] = df["a"] / df["b"]
out = df.groupby("user_id")["x"].mean()
```

改写后 —— **0.021 秒**(5 次取平均,首次 warmup 不计)—— **约 29× 加速**:

```python
import cudf

df = cudf.read_parquet("events.parquet")
df["x"] = df["a"] / df["b"]
out = df.groupby("user_id")["x"].mean()
```

三个值得注意的点:

- **改动只有一行 import。** 同一套 `read_parquet` / 算术运算 / `groupby().mean()` 全程在 GPU 上跑完。有一处行为差异要注意:`cudf.DataFrame.groupby` 默认不对分组键排序,pandas 默认排序,下游依赖分组键顺序时要显式写 `groupby("user_id", sort=True)`。
- **链路中段不做 device 往返。** 遵循 skill 的「GPU 数据生命周期」纪律,结果一直留在 GPU 显存里,直到下游真正需要 CPU 数据才会调 `.to_pandas()`。
- **零代码替代方案。** 如果你压根不想动现有脚本,直接用 `python -m cudf.pandas script.py` 跑;当用户的诉求是「让现有代码跑得更快」而不是「写显式的 RAPIDS import」时,skill 会自动选这条路径。

复现命令(10M 行,~2M 个不同 `user_id`,1× NVIDIA GH200 120GB,cudf 26.10.00,pandas 3.0.6):

```python
# gen_events.py —— 在 $TMPDIR 下生成 ~130 MB 的 events.parquet
import os, numpy as np, pandas as pd
rng = np.random.default_rng(20260514)
n_rows, n_users = 10_000_000, 2_000_000
pd.DataFrame({
    "user_id": rng.integers(0, n_users, size=n_rows, dtype=np.int32),
    "a": rng.normal(10.0, 3.0, n_rows).astype(np.float32),
    "b": rng.uniform(0.5, 5.0, n_rows).astype(np.float32),
}).to_parquet(f"{os.environ['TMPDIR']}/events.parquet", index=False)
```

## 依赖

- [**RAPIDS**](https://rapids.ai/) —— 本 skill 引导使用的 GPU 数据科学栈(`cupy`、`cupyx`、`cudf`、`cuml`)。底层库的 import 需要一块 CUDA 兼容的 NVIDIA GPU。仓库预生成的 API 索引基于 **RAPIDS 26.10 + CUDA 13**(`cu13` wheels,NVIDIA driver ≥ 580.65.06)抓取,但 skill 本身可配合任意较新的 RAPIDS 安装使用。
- [**ripgrep(`rg`)**](https://github.com/BurntSushi/ripgrep) —— skill 的标准工作流全程依赖它,从 `apis/<pkg>.txt` 中一次性查到精确的 API 签名。

安装 RAPIDS 本身(即仓库索引抓取所基于的环境 —— CUDA 13 / `cu13` wheels):

```bash
pip install "cudf-cu13==26.10.*" "cuml-cu13==26.10.*" "cupy-cuda13x"
```

`cupyx` 随 `cupy` 一同安装。如需 CUDA 12,把每个 `-cu13` 后缀换成 `-cu12`,并改装 `cupy-cuda12x`。conda / Docker 安装与官方 release selector 见 [RAPIDS 安装指南](https://docs.nvidia.com/datascience/install/)。

## 安装

本仓库的真正 skill 内容位于 `skills/rapids-first/` 子目录。

### 推荐:GitHub CLI

如果本地装有 [GitHub CLI](https://cli.github.com/) 且支持 `skill` 子命令,它会自动处理 `skills/<name>/` 子目录:

```bash
# Claude Code
gh skill install TioSisai/rapids-first rapids-first --agent claude-code --scope user

# Codex
gh skill install TioSisai/rapids-first rapids-first --agent codex --scope user
```

### 备选:git clone

#### Claude Code

用户级(跨所有项目可用):

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first ~/.claude/skills/rapids-first
```

项目级(仅作用于当前项目):

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first .claude/skills/rapids-first
```

#### Codex

用户级:

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first ~/.agents/skills/rapids-first
```

项目级:

```bash
git clone https://github.com/TioSisai/rapids-first.git
mv rapids-first/skills/rapids-first .agents/skills/rapids-first
```

### 触发方式

安装后重启 CLI(或开新会话)。只要在 prompt 中包含字面 token `rapids-first` 即可触发,例如:

> `rapids-first` 改写这个预处理脚本。

> 用 `rapids-first` 在这份 DataFrame 上实现 KMeans。

## API 索引版本

仓库中预生成的四份 `apis/<pkg>.txt` 是基于以下环境抓取的:

| 组件         | 版本               |
| ------------ | ------------------ |
| Python       | 3.12.15            |
| CUDA runtime | 13.2               |
| cupy         | 14.2.0             |
| cupyx        | (随 cupy 一同安装) |
| cudf         | 26.10.00           |
| cuml         | 26.10.00           |

各版本的更新日志(含此前各版索引的抓取环境)见 [`CHANGELOGS/zh/`](./CHANGELOGS/zh/)。

### 何时需要重新生成

以下任一情形都建议重新生成 API 索引:

- 本地任一 RAPIDS 包升级了;
- RAPIDS 发布了新的 minor / major 版本,公共 API 有变化(RAPIDS 按 `YY.MM` 节奏发版);
- 本地环境的 CUDA / RAPIDS 主版本与上表不一致,并观察到签名漂移。

如果上表已与你的环境完全一致,仓库自带的 `apis/` 可直接使用,无需重新生成。

### 如何重新生成

不带参数运行会重新生成四个默认包(`cupy`、`cupyx`、`cudf`、`cuml`)。`--packages` 会覆盖这份列表,接受任意可 import 的模块名。

```bash
# 1. 激活已装好 RAPIDS 的 Python 环境
conda activate <your-rapids-env>            # conda
# source /path/to/venv/bin/activate         # venv

# 2. 用脚本的绝对路径调用(Claude Code 用户级安装)
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py
# 项目级安装:python /path/to/your/project/.claude/skills/rapids-first/fetch_rapids_apis.py
# Codex:    将 `.claude` 替换成 `.agents`

# 只抓取指定包
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py --packages cudf cuml

# 输出到其他根目录
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py --output-dir /tmp/rapids-apis
```

脚本每次运行都会按 qualname 字典序重写 `apis/<pkg>.txt`,`git diff` 可看出 API 表面变化 —— 用于审计 RAPIDS 升级很方便。其中三条(`cupy.testing.NumpyAliasBasicTestBase.subTest`、`cupy.testing.NumpyAliasValuesTestBase.subTest`、`cudf.io.dlpack.ColumnAccessor.pop`)的签名会打印哨兵默认值的进程内存地址,每次运行都会变,读 diff 时忽略这几行。

如果某个包 import 失败(缺少 CUDA driver、库版本错位等),脚本会在 stderr 打印 `[skip] <pkg>: import failed -> <reason>` 并继续处理其余包,部分重新生成是安全的。

### 覆盖更多 RAPIDS 包

四个包是默认范围。如果本地装有完整的 RAPIDS,按三步扩展。

抓取额外的包。能 import 的会各自生成 `apis/<pkg>.txt`,其余打印 `[skip]` 后跳过:

```bash
python ~/.claude/skills/rapids-first/fetch_rapids_apis.py \
    --packages cugraph nx_cugraph cucim cuvs dask_cudf pylibraft raft_dask nvforest
```

在 `cpu-rapids-cuda-mapping.tsv` 中补上对应的映射行。skill 的工作流先 grep 这张表,所以索引文件存在但没有映射行时,这个包对 skill 仍然是不可见的。有零代码 backend 的包要填上 `zero_code` 字段,并在 SKILL.md 的表格里写明激活方式(有零代码路径的是 `nx-cugraph` 和 `dask-cudf`)。

把新文件补进 SKILL.md 的目录结构,并加入 `fetch_rapids_apis.py` 的 `DEFAULT_PACKAGES`,这样不带参数运行也会一并刷新。

`v26.06` 标签是最后一个同时包含十三份索引文件、对应映射行与 SKILL.md 文案的版本。`git checkout v26.06 -- skills/rapids-first` 可整体还原那一版;除非本地跑的确实是 RAPIDS 26.06,还原后请重新生成 `apis/`。
