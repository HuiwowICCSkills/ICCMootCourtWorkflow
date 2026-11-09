# ICC Moot Memorial Writing

ICC 国际刑事法院模拟法庭书状写作 skill。用于 prosecution、defence、State 等赛题指定角色的中文或英文 memorial / written submissions：确定写作路线、搭建框架、起草正文、修改和审校，并把赛题记录、程序阶段、法律要件、IRAC 和可定位引证组织成法院可以逐项裁判的书面论证。

本 skill 不绑定某一届赛题。每次使用都重新确定案件、角色、程序阶段、争点、篇幅、法源截止日和当届规则。

## 与脚注核验的关系

本 skill 把 [`icc-moot-footnote-verifier`](../icc-moot-footnote-verifier/SKILL.md) 作为工作流的固定组成部分：

- 任何书状起草、续写、实质修改或定稿任务的交付版本，默认执行脚注核验与最小校正；
- 大纲、局部段落和章节初稿用 `inventory`；
- 完整交付稿、终稿和任何声称 `submission-ready` 的版本用 `full`；
- 用户明确要求“只报告、不改稿”时，按只读模式处理。

脚注核验不是可选的附加步骤。未完成 `full` 核验的稿件不得标为 `submission-ready`。

## 安装

把本目录放入 Codex skills 根目录：

```powershell
Copy-Item -Recurse -Force `
  ".\skills\icc-moot-memorial-writing" `
  "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse -Force `
  ".\skills\icc-moot-footnote-verifier" `
  "$env:USERPROFILE\.codex\skills\"
```

两个 skill 应安装在同一 skills 根目录下。书状写作 skill 会按名称调用脚注核验 skill。

## 使用

```text
使用 $icc-moot-memorial-writing，根据本次赛题、赛规和指定立场，完成我需要的书状写作或修改。
```

默认交付包括：

1. 书状正文或指定写作产物；
2. 脚注核验报告；
3. 脚注校正记录；
4. 未解决红项及其对交付状态的影响。

## 参考文件

| 文件 | 用途 |
|---|---|
| [`references/issue-design.md`](references/issue-design.md) | 争点拆解、证明任务、角色与程序阶段 |
| [`references/authorities.md`](references/authorities.md) | 法源、判例、引证与双语问题 |
| [`references/drafting.md`](references/drafting.md) | 正文起草、IRAC、压缩与局部修改 |
| [`references/review.md`](references/review.md) | 实质审校、形式核查与脚注核验交接 |
| [`references/chinese-memorial-format-and-language.md`](references/chinese-memorial-format-and-language.md) | 中文书状规则、版式与语言 |
| [`references/format-and-language.md`](references/format-and-language.md) | 英文书状规则、版式与语言 |

## 边界

- 事实从赛题记录来，不把虚构赛题当真实新闻检索。
- 每个论点必须有裁判任务，不以背景介绍或案例堆积代替证明。
- 法源只承担它能够承担的命题；先读原文，再确定规则内容、程序阶段和适用限制。
- 不捏造案号、页码、段号、引语或版本。
- 格式要求依当届规则；历史样本只能作为校准，不是硬性规则。

## 仓库

<https://github.com/HuiwowICCSkills/ICCMootCourtWorkflow>
