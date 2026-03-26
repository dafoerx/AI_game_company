# Project Drive 使用说明（轻量版）

这个目录保留为项目的**执行层**，但不再承担冗长过程归档的职责。

## 1. 目标

做到下面这件事：

> 任意一个角色接手时，只要按顺序阅读本目录里的文件，就能知道：
> 1. 现在做到哪里；
> 2. 自己这一步要输出什么；
> 3. 当前阻塞是什么；
> 4. 下一步该交给谁。

## 2. 阅读顺序

每个角色开始工作前，统一按这个顺序阅读：

1. `project-drive/README.md`
2. `project-drive/00-active-context.md`
3. `project-drive/01-role-boards/<你的角色>.md`
4. `project-drive/02-task-cards/in-progress/` 下当前活跃任务卡

如果存在冲突，以：

- **当前任务卡中的最新状态** 为准
- **active-context 中的当前阶段** 为总览基线
- **role board 中的执行清单** 为本轮输出要求

## 3. 目录结构

```text
project-drive/
├─ README.md
├─ 00-active-context.md
├─ 01-role-boards/
│  ├─ product-system.md
│  ├─ prototype-build.md
│  └─ prototype-qa.md
├─ 02-task-cards/
│  ├─ in-progress/
│  └─ done/
└─ 03-handoffs/
   └─ HANDOFF_TEMPLATE.md
```

## 4. 执行协议

### 4.1 开始前必须确认
- 当前唯一活跃任务卡是什么
- 本角色本轮要交付什么
- 哪些问题必须在本轮回答清楚
- 输出完成后要交给谁

### 4.2 做事时的最小写回要求
每个角色完成当前轮工作后，默认只写回四项：

- 本轮完成
- 本轮确认
- 当前阻塞
- 下一位角色

不要把短进展写成长报告。

### 4.3 handoff 长度上限
单次 handoff 建议不超过 10 行关键项；如果只是同步状态，优先回写任务卡，不单独新建文档。

## 5. 当前阶段

当前仓库处于：

- 已完成餐饮题材、平台、商业目标切换
- 已完成三角执行模型切换
- 正在定义餐饮项目的首个经营闭环
- 下一步将直接进入工程骨架搭建准备

## 6. 当前活跃任务

### TASK-001
- 文件：`project-drive/02-task-cards/in-progress/TASK-001_餐饮项目MVP与经营闭环.md`
- 当前状态：立项改版后重新启动
- 当前目标：把餐饮项目的首版经营闭环压成可直接开工的版本

## 7. 默认接力顺序

当前阶段默认采用下面的接力顺序：

1. `product-system` 冻结范围、资源和闭环
2. `prototype-build` 直接拆实现并搭工程骨架
3. `prototype-qa` 只做轻量风险审查和首轮验证准备

如果某轮无需 QA 介入，可以在任务卡中直接说明原因。