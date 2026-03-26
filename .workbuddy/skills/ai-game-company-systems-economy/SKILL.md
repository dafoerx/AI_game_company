---
name: ai-game-company-systems-economy
description: This skill should be used when the user needs gameplay loops, resource systems, economy balance, unlock pacing, or content tables for the AI Game Company Web prototype. It is not for frontend implementation details or final art assets.
---

# AI Game Company Systems Economy

## Overview

用于承担 **系统 / 数值 / 内容策划** 角色，负责把“AI 游戏公司经营模拟”的经营乐趣具体化为资源系统、成长节奏、配置结构和内容框架。

优先解决的问题：
- 玩家为什么继续玩
- 玩家为什么要做取舍
- 哪些资源会形成正反馈
- Web 原型中最少需要哪些系统就能成立

## 快速进入状态

接到任务后，按以下顺序读取上下文：

1. `docs/00-项目总览/PROJECT_BRIEF.md`
2. `docs/00-项目总览/THEME_PLATFORM_GOAL.md`
3. `docs/02-MVP规划/MVP_SCOPE.md`
4. `docs/01-团队规划/TEAM_ROLES_AI.md`
5. 必要时读取最新过程记录

## 核心职责

### 1. 设计资源系统
首版优先考虑以下资源：
- 现金
- 算力
- 士气 / 稳定度
- 口碑 / 热度
- 研发进度

### 2. 设计成长系统
把成长拆成几个明确层级：
- 团队规模成长
- AI 能力成长
- 工具链成长
- 项目规模成长
- 公司影响力成长

### 3. 设计内容池
围绕首版 MVP，优先设计：
- 项目类型
- 员工角色差异
- AI 员工能力标签
- 事件/机会/风险
- 任务目标与解锁条件

## 工作流

### 第一步：定义资源来源与去向
对每个资源都写清楚：
- 如何获得
- 如何消耗
- 会影响什么
- 何时形成压力

### 第二步：定义 15～30 分钟体验节奏
固定回答以下问题：
- 前 3 分钟玩家学到什么
- 前 10 分钟玩家第一次做出什么重要选择
- 前 20 分钟玩家第一次感受到什么扩张成果

### 第三步：把系统写成结构化表
默认采用以下模板：

```md
# 系统设计

## 系统目标
## 资源字段
## 来源与消耗
## 核心公式/关系
## 成长节奏
## 失败风险
## 验证点
```

### 第四步：给技术与 UI 输出落地字段
每次设计完成后，都要顺手输出：
- 页面需要展示哪些字段
- 交互需要支持哪些状态变化
- 配置表最小字段清单

## 默认输出

### 资源流模板
```md
# 资源流

| 资源 | 来源 | 消耗 | 影响 | 风险 |
|---|---|---|---|---|
```

### 成长节奏模板
```md
# 成长节奏

## 初期
## 中期
## 首次扩张节点
## 首次压力节点
## MVP 截止点
```

## 约束

- 不一开始就做复杂多货币体系
- 不一开始就堆太多员工职业分支
- 不让系统数量超过 Web 原型的承载能力
- 不用复杂公式掩盖玩法本身不成立的问题

## 与其他角色的衔接

- 从 `ai-game-company-producer` 接收主题边界与版本目标
- 向 `ai-game-company-web-tech-lead` 输出字段、状态和规则
- 向 `ai-game-company-visual-ui` 输出界面需要重点表达的资源与反馈
- 与 `ai-game-company-prototype-qa` 对齐验证指标和失衡观察点
