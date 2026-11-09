---
name: icc-moot-footnote-verifier
description: 核验并校正 ICC 模拟法庭书状中的脚注与引证：逐条建立 citation ledger、比对原文精确引文、检查 pinpoint、文书号和命题支持关系。默认作为 icc-moot-memorial-writing 书状起草、修改与定稿流程的固定步骤自动执行，也可单独用于“核验脚注”“查引证”“citation check”“提交前核验”等显式请求。
metadata:
  short-description: ICC 书状脚注核验与校正（书状工作流默认）
---

# ICC Moot Footnote Verifier

## 用途与边界

本 skill 回答一个问题：**书状中的每一条脚注，是否真的由其所引用的原始来源、在所指的精确位置、支持正文中的那个命题。**

它同时是 `icc-moot-memorial-writing` 的默认组成部分。使用书状写作 skill 起草、续写、实质修改或定稿 ICC memorial 时，本 skill 应自动执行脚注核验，并对能够由已打开原文确认的引证错误做最小校正；不需要用户另行说“核验脚注”。只有用户明确要求“只报告、不要改稿”时，才保持只读。

它不负责实体论证的写作、翻译、格式美化或论证扩写。发现来源不支持正文命题时，按本协议标记、收窄或阻断，不替作者另写论证。

## 触发与默认执行

| 场景 | 行为 |
|---|---|
| 通过 `icc-moot-memorial-writing` 起草、修改或定稿书状 | **自动执行**；按阶段选择模式，默认完成核验与最小校正 |
| 用户点名 `$icc-moot-footnote-verifier`，或要求“核验脚注 / 核对引证 / citation check / 提交前核验” | 执行 |
| 用户明确要求只读审计、只出报告、不要改稿 | 只核验，不校正 |
| 普通翻译、润色、格式调整，且不涉及书状交付 | 不执行完整核验 |

## 三种模式与工作流阶段

| 模式 | 对应阶段 | 工作范围 | 默认校正 |
|---|---|---|---|
| `inventory` | 大纲、局部段落、章节初稿 | 提取全部脚注；检查空脚注、缺号、重号、重复、明显格式错误、无来源、锚点错位 | 修正机械与结构问题 |
| `sample` | 完整工作稿的中间审阅，或用户明确要求抽查 | 按来源类型分层抽取约 20%，加上所有高风险脚注（新来源、二手来源、AI 辅助、无本地文件、引文过长、一条脚注多个来源） | 修正已确认项 |
| `full` | 任何完整交付稿、终稿，或声称 `submission-ready` 的版本 | 100% 脚注逐条回查原文、pinpoint 和命题支持关系 | 修正已确认项，并复审受影响条目 |

没有阶段信息时，按交付物判断：局部草稿用 `inventory`；完整书状用 `full`。`sample` 只在时间受限或用户要求抽查时使用，不能用于最终提交稿。

## 工作流

### 1. 锁定核验对象

先读当前任务适用的项目指引、当届赛题及勘误/澄清、书状格式规范、当前书状 DOCX/Markdown，以及相关研究底稿。确认：

- 文件版本与哈希
- 角色、issue、程序阶段
- 正文与脚注语言
- 脚注编号体系

不要把旧版 DOCX 或写作思路当成当前稿。当前项目若使用 `D:\ICCWork` 结构，可参考文末“当前项目路径”；其他项目按实际路径替换。

### 2. 提取脚注清单

DOCX 使用：

```powershell
python scripts/extract_docx_footnotes.py "<docx路径>" --out "<输出.json>"
```

Markdown 直接解析 `[^n]` 与 `[^n]:` 定义；若脚注定义缺失，记为 `MISSING-DEFINITION`。

每条脚注分配稳定 ID：`FN-001`、`FN-002`……并记录其所在段落、章节和正文命题。

### 3. 建立 citation ledger

每条脚注至少记录：

| 字段 | 说明 |
|---|---|
| `fn_id` | `FN-001` |
| `location` | 章节 + 段落号/页码 |
| `proposition` | 该脚注支持的正文命题，用一句话概括 |
| `citation_text` | 脚注原文 |
| `source_type` | Treaty / Judgment / Decision / Order / Case File / Commentary / Other |
| `document_number` | 条约编号、案件文书号、官方文件号 |
| `court_chamber` | 法院、分庭 |
| `date` | 裁判/文件日期 |
| `pinpoint` | 精确到 para. / page / article |
| `exact_quote` | 从原文逐字复制的英文（或原文语言）句子 |
| `local_path` | 本地原件路径 |
| `sha256` | 本地原件哈希（终稿核验时） |
| `official_url` | 官方来源 URL |
| `read_scope` | `full-text` / `abstract-only` / `metadata-only` / `index-snippet` |
| `verification_status` | 见下方状态 |
| `notes` | 例外、缺口、需人工判断之处 |

详细字段与状态定义见 `references/verification-protocol.md`。

### 4. 逐条核验

按以下顺序做，任一步失败即记录，不要跳步：

1. **来源存在**：本地原件或官方 URL 是否真实存在；仅有二手笔记不算。
2. **文书身份**：案件名、文书类型、文书号、分庭、日期是否对应。
3. **精确引文**：脚注所依赖的句子是否能在原文中找到；用 `scripts/search_exact_quote.py` 在本地文本层搜索。
4. **Pinpoint**：引文是否确实位于标注的 paragraph/page/article，而不是“附近段落”。
5. **命题支持**：原文是否支持正文命题，而不是只支持一个更窄或不同的命题。
6. **引证体系**：全篇是否只用一种体系；`ibid.`、短引、交叉引用是否指回正确来源。
7. **权威索引**：Index of Authorities 中的来源是否都出现在脚注；脚注来源是否都进入索引（终稿适用）。
8. **AI 虚构风险**：若无法在本地原文或官方来源中找到原句，标记 `QUOTE-NOT-FOUND`；不得用“搜索摘要看起来像”放行。

### 5. 状态与严重级别

| 状态 | 含义 | 级别 |
|---|---|---|
| `VERIFIED` | 原文、pinpoint、命题三者均核对通过 | 通过 |
| `PARTIAL` | 来源存在且引文存在，但命题支持或 pinpoint 需人工确认；或只读到摘要/元数据 | 黄 |
| `WRONG-PINPOINT` | 引文存在，但不在标注的 para./page | 红 |
| `QUOTE-NOT-FOUND` | 在指定来源或可检索文本中找不到该引文 | 红 |
| `MISATTRIBUTED` | 引文存在，但属于另一案件/文书/段落 | 红 |
| `NOT-SUPPORTED` | 引文存在，但不支持正文命题 | 红 |
| `MISSING-SOURCE` | 无本地原件且无官方 URL，无法核验 | 红 |
| `MISSING-DEFINITION` | 脚注引用存在但脚注文本缺失 | 红 |
| `UNVERIFIED` | 尚未核验（不得计入通过） | 灰 |

`VERIFIED` 只能用于实际打开原文并核对过的条目。仅凭元数据、摘要、索引片段或写作思路中的引文块，最高只能标 `PARTIAL`。

### 6. 默认校正

在书状写作工作流中，核验后默认继续做**最小校正**；用户明确要求只读时跳过本步，只在报告中给出修复建议。

#### 6.1 可以校正的项

只有已经从原文或官方来源确认的事实性、机械性错误才可自动修改：

- 文书类型、案件名、文书号、分庭、日期
- pinpoint（段落号、页码、条号）
- 引证格式统一（服从当届规则与用户指定体例）
- `ibid.`、短引、交叉引用指向
- 脚注锚点位置、空脚注、缺号、重号和重复定义
- Index of Authorities 与脚注的双向对应
- 拼写、大小写、标点等不改变命题的引证外观问题

#### 6.2 不得校正的项

- 不得凭记忆、搜索摘要或语言模型补写来源、引文、页码、段号、URL
- 不得为通过核验而删除不利引证或不利事实
- 不得改变实体立场、论证结构或请求事项
- 不得把 `QUOTE-NOT-FOUND`、`MISATTRIBUTED`、`NOT-SUPPORTED`、`MISSING-SOURCE` 用猜测“修好”

对 `NOT-SUPPORTED`，只有在不改变论证方向且能忠实收窄命题时，才可把正文命题收窄到原文实际支持的范围；否则列为阻断项，交作者决定。对 `QUOTE-NOT-FOUND` 和 `MISSING-SOURCE`，优先在已有已核验来源中找替代；没有替代就保留红项并写明最小修复动作。

#### 6.3 校正记录

每次校正都写入 `脚注校正记录`，至少包含：

| 字段 | 说明 |
|---|---|
| `fn_id` | 受影响的脚注 |
| `field` | 修改的字段（pinpoint、document_number、date、citation_text 等） |
| `before` | 修改前内容 |
| `after` | 修改后内容 |
| `basis` | 依据的原文文件、页码/段号或官方 URL |
| `status_after` | 校正后重新核验的状态 |

修改 DOCX 时保留原有样式、脚注锚点、编号和书签；不要为了改一条脚注重建整篇文档。修改后计算新哈希，并对受影响条目重新核验。

### 7. 输出

默认交付三部分：

1. **脚注核验报告**：使用 `references/report-template.md`，包含核验模式、文件与哈希、总数与状态统计、逐条表、阻断项、未核验边界。
2. **校正后的书状文件**：仅在书状写作工作流中或用户要求修复时生成；保留改前副本或可审阅差异。
3. **脚注校正记录**：逐条列明改了什么、依据是什么、改后状态。

用户明确只读时，只交付报告和修复建议，不改文件。

## 硬规则

- **不凭记忆补引注。** 找不到原文就标 `MISSING-SOURCE` 或 `QUOTE-NOT-FOUND`。
- **不把写作思路当原始来源。** 写作思路中的引文块是线索，不是最终证据；必须回到条约、判决、决定或赛题原文。
- **不以搜索摘要代替全文。** 只读到摘要/元数据时，明确写“核验边界：仅元数据/摘要”。
- **不以标题或案名代替 pinpoint。** 必须落到 para./page/article。
- **不把“来源存在”等同于“来源支持命题”。**
- **不使用 AI 生成或补写脚注。** 当届规则禁止 AI 虚构脚注/引证时尤其如此。
- **校正不是补写。** 校正只修正已确认的引证错误；不能修复的缺口保留为红项。
- **最小编辑。** 只动脚注、引证和使本次校正成立的依赖项；不顺手改写正文。
- **改后必复审。** 任何影响脚注的修改都要重新核验受影响条目，并更新报告与哈希。

## 当前项目路径（2027 IBA ICCMCC 示例）

以下路径只适用于当前项目；其他届次或项目按实际结构替换。

- 项目规则：`D:\ICCWork\AGENTS.md`
- 赛题：`D:\ICCWork\00-赛题（研究基础）\2027-IBA-ICC-Moot-Court-Case.md`
- 2027 书状格式规范：`D:\ICCWork\00-赛题（研究基础）\2027-书状格式规范.md`
- 2027 Rules：`C:\Users\chips\Documents\Obsidian Vault\90-系统\附件\法律\ICC模拟法庭最佳书状\官方规则\IBA-ICCMCC-Rules-of-Procedure-2027.pdf`
- 2027 Rules 文字层：同目录 `IBA-ICCMCC-Rules-of-Procedure-2027.txt`
- 当前 issue 工作目录示例：`D:\ICCWork\工作文件\考核期书状-issue2-辩方\`
- 本地原件检索根目录：`D:\ICCWork\Issues\`、`D:\ICCWork\工作文件\`、`C:\Users\chips\Documents\Obsidian Vault\90-系统\附件\法律\`

## 参考文件

- `references/verification-protocol.md`：完整字段、状态、来源层级、边界情形、校正协议和终稿审计流程。
- `references/report-template.md`：核验报告与校正记录模板。

## 脚本

- `scripts/extract_docx_footnotes.py`：从 DOCX 提取正文段落、脚注引用和脚注文本，输出 JSON/Markdown 清单。
- `scripts/search_exact_quote.py`：在本地 `.txt`/`.md` 语料中搜索精确引文，输出文件、行号和上下文，用于 `QUOTE-NOT-FOUND` 初筛。

脚本只做机械提取和检索，不替代人工判断；脚本命中不等于 `VERIFIED`，仍需核对文书身份、pinpoint 和命题支持。
