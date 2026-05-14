<p align="right"><a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/lang-English-blue?style=for-the-badge" alt="English"></a></p>

# 更新日志

本文件记录本项目所有值得关注的变更。

格式参照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。

## [0.1.0] - 2026-05-14

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

[0.1.0]: https://github.com/TioSisai/rapids-first/releases/tag/v0.1.0
