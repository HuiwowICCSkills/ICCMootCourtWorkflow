# ICC Moot Footnote Verifier

ICC 模拟法庭书状脚注与引证核验 skill。逐条建立 citation ledger，比对原文精确引文，检查文书身份、pinpoint、`ibid.`/短引和命题支持关系，并默认对已确认的引证错误做最小校正。

本 skill 是 [`icc-moot-memorial-writing`](../icc-moot-memorial-writing/SKILL.md) 书状工作流的固定组成部分。使用书状写作 skill 起草、修改或定稿 memorial 时，本 skill 自动执行，不需要用户另行请求。

## 三种模式

| 模式 | 使用阶段 | 工作范围 |
|---|---|---|
| `inventory` | 大纲、局部段落、章节初稿 | 提取全部脚注；检查空脚注、缺号、重号、重复、明显格式问题、无来源、锚点错位 |
| `sample` | 完整工作稿的中间审阅，或用户要求抽查 | 分层抽取约 20%，高风险脚注全查 |
| `full` | 完整交付稿、终稿、`submission-ready` 版本 | 100% 逐条回查来源、引文、pinpoint 和命题支持 |

局部草稿默认 `inventory`；完整书状默认 `full`。`sample` 只用于中间审阅或时间受限的抽查，不能用于最终提交稿。

## 默认校正

书状工作流默认在核验后做最小校正。只修改已由原文或官方来源确认的引证层错误：

- 文书类型、案件名、文书号、分庭、日期
- pinpoint（段落号、页码、条号）
- 引证格式、`ibid.`/短引/交叉引用指向
- 脚注锚点、空脚注、缺号、重号、重复定义
- Index of Authorities 与脚注的双向对应

不得凭记忆或搜索摘要补来源、补引文、补页码；不得删除不利引证；不得改变实体立场、论证结构或请求事项。无法确认的 `QUOTE-NOT-FOUND`、`MISATTRIBUTED`、`NOT-SUPPORTED`、`MISSING-SOURCE` 保留为红项，不用猜测修复。

用户明确要求只读审计时，只交付报告和修复建议，不改文件。

## 安装与依赖

```powershell
Copy-Item -Recurse -Force `
  ".\skills\icc-moot-footnote-verifier" `
  "$env:USERPROFILE\.codex\skills\"
python -m pip install lxml
```

DOCX 脚注提取脚本依赖 `lxml`。`search_exact_quote.py` 只使用 Python 标准库。

## 脚本

```powershell
# 提取 DOCX 正文段落、脚注引用和脚注文本
python scripts/extract_docx_footnotes.py "memorial.docx" --out "footnotes.json"

# 输出 Markdown 清单
python scripts/extract_docx_footnotes.py "memorial.docx" --format md --out "footnotes.md"

# 在本地 txt/md 语料中搜索精确引文
python scripts/search_exact_quote.py "The occupying State shall be regarded..." --root "D:\ICCWork"
```

脚本只做机械提取和检索。脚本命中不等于 `VERIFIED`，仍需核对文书身份、pinpoint 和命题支持。

## 报告与校正记录

默认交付：

1. 脚注核验报告（`references/report-template.md`）；
2. 校正后的书状文件；
3. 脚注校正记录（FN、字段、修改前、修改后、依据、校正后状态）。

状态包括 `VERIFIED`、`PARTIAL`、`WRONG-PINPOINT`、`QUOTE-NOT-FOUND`、`MISATTRIBUTED`、`NOT-SUPPORTED`、`MISSING-SOURCE`、`MISSING-DEFINITION`、`UNVERIFIED`。`VERIFIED` 只能用于实际打开原文并核对过的条目。

## 边界

- 不负责实体论证写作、翻译、格式美化或论证扩写。
- 不把写作思路、旧稿、检索记录或 AI 摘要当原始来源。
- 不以搜索摘要代替全文；只读到摘要或元数据时，明确标注核验边界。
- 不以标题、案名或“附近段落”代替 pinpoint。
- 不凭记忆补引注；找不到原文就标 `MISSING-SOURCE` 或 `QUOTE-NOT-FOUND`。

## 仓库

<https://github.com/HuiwowICCSkills/ICCMootCourtWorkflow>
