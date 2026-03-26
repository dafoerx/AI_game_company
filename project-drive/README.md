# Project Drive 使用说明

这个目录是项目的**执行层**，作用不是重复 `docs/` 里的正式规划，而是让不同角色可以直接通过 Git 接力推进。

## 1. 目标

做到下面这件事：

> 任意一个角色接手时，只要按顺序阅读本目录里的文件，就能知道：
> 1. 现在做到哪里；
> 2. 自己这一步要确认什么；
> 3. 做完后要把什么写回 Git；
> 4. 下一位角色是谁。

## 2. 阅读顺序

每个角色开始工作前，统一按这个顺序阅读：

1. `project-drive/README.md`
2. `project-drive/00-active-context.md`
3. `project-drive/01-role-boards/<你的角色>.md`
4. `project-drive/02-task-cards/in-progress/` 下当前活跃任务卡
5. `project-drive/04-meeting-notes/` 下与该任务相关的评审/讨论记录

如果以上文件存在冲突，以：

- **任务卡中的最新状态** 为准
- **active-context 中的当前阶段** 为总览基线
- **role board 中的确认项与答复项** 为当前角色的执行清单

## 3. 目录结构

```text
project-drive/
├─ README.md
├─ 00-active-context.md
├─ 01-role-boards/
│  ├─ producer.md
│  ├─ web-tech-lead.md
│  ├─ visual-ui.md
│  ├─ systems-economy.md
│  └─ prototype-qa.md
├─ 02-task-cards/
│  ├─ in-progress/
│  └─ done/
├─ 03-handoffs/
│  └─ HANDOFF_TEMPLATE.md
└─ 04-meeting-notes/
```

## 4. 执行协议

### 4.1 开始前必须确认

当前角色开始执行前，至少确认这四件事：

- 当前唯一活跃任务卡是什么
- 本角色这一步的输出是什么
- 哪些问题必须在本轮回答清楚
- 输出完成后要 handoff 给谁

### 4.2 做事时的最小写回要求

每个角色完成当前轮工作后，必须至少写回两类信息：

1. **确认项**：你实际确认了什么边界、风险、结论
2. **答复项**：你对上一个角色提出的问题，给出的明确答复

建议优先写到：

- 当前任务卡
- 或 `03-handoffs/` 下的新 handoff 文档

不要只在对话里说，不落 Git。

### 4.3 写回格式建议

可直接采用下面结构追加到任务卡或 handoff：

```md
## 本轮确认项
- ...
- ...

## 本轮答复项
- 问题：...
  - 答复：...

## 下一位角色
- 角色：...
- 需要继续处理：...
- 必读文件：...
```

## 5. 当前阶段

当前仓库处于：

- 已完成项目主题、平台、商业目标冻结
- 已完成团队角色与项目级 Skills 建立
- 已产出 `TASK-001` 的核心循环 / 资源流 / 首页信息架构方案
- 正在进入 **跨角色评审 → 结论归档 → 拆开发任务** 阶段

## 6. 当前活跃任务

### TASK-001
- 文件：`project-drive/02-task-cards/in-progress/TASK-001_核心循环与资源流及首页信息架构.md`
- 当前状态：设计已输出，待技术 / UI / QA / 制作人评审闭环
- 当前目标：把系统设计从“可讨论”推进到“可直接拆开发任务”

## 7. 默认接力顺序

当前阶段默认采用下面的接力顺序：

1. `systems-economy` 产出设计初稿
2. `web-tech-lead` 评审技术可行性
3. `visual-ui` 评审界面表达与交互密度
4. `prototype-qa` 补齐验证指标与测试重点
5. `producer` 做范围与优先级裁决
6. 回到 `systems-economy` / `web-tech-lead` 做收口与任务拆分

如果某次任务需要跳过某个角色，必须在 handoff 中写明原因。
