# ICCMootCourtWorkflow

ICC 国际刑事法院模拟法庭书状写作工作流：把 `icc-moot-memorial-writing` 与 `icc-moot-footnote-verifier` 作为一个配套工具发布。前者负责从赛题、角色、程序阶段和法律要件出发组织书状；后者作为固定步骤，默认核验并校正脚注与引证。

本仓库不是单站检索技能。资料检索仍由 `icl-research`、`gil-research` 及各 `*Searcher` 仓库承担；本仓库只处理书状写作、审校和引证质量。

## 两个 skill

| Skill | 作用 |
|---|---|
| [`skills/icc-moot-memorial-writing`](skills/icc-moot-memorial-writing/SKILL.md) | 书状写作路线、框架、正文起草、修改和审校；按赛题、角色、程序阶段、IRAC 和可定位引证组织论证 |
| [`skills/icc-moot-footnote-verifier`](skills/icc-moot-footnote-verifier/SKILL.md) | 逐条核验脚注的来源、文书身份、精确引文、pinpoint 和命题支持；默认对已确认的引证错误做最小校正 |

## 默认工作流

```text
确定赛题 / 角色 / 程序阶段 / 争点
        ↓
搭建写作路线与 IRAC 框架
        ↓
起草或修改正文（脚注随文建立）
        ↓
脚注核验（按阶段自动选模式）
        ↓
最小校正 + 校正记录
        ↓
复审受影响条目 → 交付
```

书状写作 skill 不会等用户另行说“核验脚注”。任何起草、续写、实质修改或定稿任务的交付版本，都默认执行脚注核验与最小校正；用户明确要求“只报告、不改稿”时除外。

## 核验模式

| 阶段 | 模式 | 范围 |
|---|---|---|
| 大纲、局部段落、章节初稿 | `inventory` | 全部脚注清点；空脚注、缺号、重号、重复、明显格式问题、无来源、锚点错位 |
| 完整工作稿的中间审阅，或用户明确要求抽查 | `sample` | 分层约 20%，高风险脚注全查 |
| 完整交付稿、终稿、`submission-ready` 版本 | `full` | 100% 逐条回查来源、引文、pinpoint 和命题支持 |

完整书状默认 `full`。`sample` 不能用于最终提交稿；未完成 `full` 的稿件不得标为 `submission-ready`。

## 校验与校正的边界

核验回答四个问题：

1. 来源是否真实存在？
2. 文书身份（案件、文书类型、文书号、分庭、日期）是否对应？
3. 引文是否确实出现在标注的 pinpoint？
4. 该引文是否支持正文中的那个命题？

四项全部通过才可标 `VERIFIED`。仅凭元数据、摘要、索引片段或写作思路中的引文块，最高只能标 `PARTIAL`。

默认校正只处理已由原文或官方来源确认的引证层错误：

- 文书号、分庭、日期、案名、pinpoint
- 引证格式、`ibid.`/短引/交叉引用指向
- 脚注锚点、空脚注、缺号、重号、重复定义
- Index of Authorities 与脚注的双向对应

不得凭记忆或搜索摘要补来源、补引文、补页码、补 URL；不得为通过核验删除不利引证或不利事实；不得改变实体立场、论证结构或请求事项。`QUOTE-NOT-FOUND`、`MISATTRIBUTED`、`NOT-SUPPORTED`、`MISSING-SOURCE` 等无法确认的条目保留为红项，不用猜测修复。

## 安装

Windows PowerShell：

```powershell
git clone https://github.com/HuiwowICCSkills/ICCMootCourtWorkflow.git "$env:USERPROFILE\Documents\ICCMootCourtWorkflow"
Copy-Item -Recurse -Force `
  "$env:USERPROFILE\Documents\ICCMootCourtWorkflow\skills\*" `
  "$env:USERPROFILE\.codex\skills\"
python -m pip install lxml
```

两个 skill 应在同一 `~/.codex/skills` 根目录下。`lxml` 只用于 `icc-moot-footnote-verifier` 的 DOCX 脚注提取脚本；`search_exact_quote.py` 只用 Python 标准库。

## 使用

```text
使用 $icc-moot-memorial-writing，根据本次赛题、赛规和指定立场，完成我需要的书状写作或修改。
```

书状写作 skill 会在交付前调用 `$icc-moot-footnote-verifier`。也可以单独核验现有稿件：

```text
使用 $icc-moot-footnote-verifier，对这份 memorial 做 full 核验，并校正能够确认的引证错误。
```

默认交付：

1. 书状正文或指定写作产物；
2. 脚注核验报告；
3. 脚注校正记录；
4. 未解决红项及其对交付状态的影响。

## 目录

| 路径 | 用途 |
|---|---|
| `skills/icc-moot-memorial-writing/SKILL.md` | 书状写作主流程 |
| `skills/icc-moot-memorial-writing/references/` | 争点、法源、起草、审校、中文/英文格式参考 |
| `skills/icc-moot-footnote-verifier/SKILL.md` | 脚注核验与校正主流程 |
| `skills/icc-moot-footnote-verifier/references/verification-protocol.md` | 完整核验协议、状态定义、校正协议 |
| `skills/icc-moot-footnote-verifier/references/report-template.md` | 核验报告与校正记录模板 |
| `skills/icc-moot-footnote-verifier/scripts/extract_docx_footnotes.py` | DOCX 脚注提取（依赖 `lxml`） |
| `skills/icc-moot-footnote-verifier/scripts/search_exact_quote.py` | 本地 txt/md 精确引文初筛 |

## 与其它仓库的关系

- `icl-research` / `gil-research`：可选的研究检索来源；本工作流只使用已经取得并核验的材料，不把检索摘要当原文。
- 各 `*Searcher` 仓库：按来源获取一手材料；本工作流负责写作与引证核验，不重复实现站点访问。
- 本仓库不包含任何案件事实、赛题答案、获奖书状或本地语料；这些内容由使用者按当届赛题和项目目录提供。

## 验证

```powershell
# 检查 skill 结构和 frontmatter
Get-ChildItem .\skills -Directory | ForEach-Object {
  Test-Path (Join-Path $_.FullName 'SKILL.md')
}

# 检查脚本语法
python -m py_compile .\skills\icc-moot-footnote-verifier\scripts\extract_docx_footnotes.py
python -m py_compile .\skills\icc-moot-footnote-verifier\scripts\search_exact_quote.py
```

## 边界

- 不把虚构赛题当真实新闻检索，也不拿现实报道填补虚构记录。
- 不把写作思路、旧稿、检索记录或 AI 摘要当原始来源。
- 不以搜索摘要代替全文；只读到摘要或元数据时，明确标注核验边界。
- 不以标题、案名或“附近段落”代替 pinpoint。
- 不凭记忆补引注；找不到原文就标 `MISSING-SOURCE` 或 `QUOTE-NOT-FOUND`。
- 格式要求依当届规则；历史样本只能作为校准，不是硬性规则。

## 更新

```powershell
git -C "$env:USERPROFILE\Documents\ICCMootCourtWorkflow" pull
Copy-Item -Recurse -Force `
  "$env:USERPROFILE\Documents\ICCMootCourtWorkflow\skills\*" `
  "$env:USERPROFILE\.codex\skills\"
```

仓库：<https://github.com/HuiwowICCSkills/ICCMootCourtWorkflow>
