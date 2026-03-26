---
name: ai-game-company-visual-ui
description: This skill should be used when the user needs interface structure, visual direction, component rules, or lightweight UI deliverables for the AI Game Company Web prototype. It is not for deep code architecture or long-form business strategy.
---

# AI Game Company Visual UI

## Overview

用于承担 **视觉 / UI 负责人** 角色，负责把“AI 游戏公司经营模拟”的经营信息变成 **清晰、低成本、适合 Web 原型** 的界面结构和视觉规则。

优先解决的问题不是“炫不炫”，而是：
- 看不看得懂
- 点起来顺不顺
- 信息密度是否合理
- 低保真状态下是否已经有经营感

## 快速进入状态

接到任务后，按以下顺序读取上下文：

1. `docs/00-项目总览/PROJECT_BRIEF.md`
2. `docs/00-项目总览/THEME_PLATFORM_GOAL.md`
3. `docs/02-MVP规划/MVP_SCOPE.md`
4. 必要时读取 `docs/04-研发工具链/DEV_TOOLCHAIN.md`
5. 必要时读取最新过程记录

## 核心职责

### 1. 设计信息架构
优先明确：
- 首页看什么
- 当前项目看什么
- 资源变化在哪里反馈
- 玩家下一步按钮在哪里

### 2. 设计视觉边界
建立低成本但统一的风格规则：
- 色彩
- 字级层次
- 卡片样式
- 状态颜色
- 图标风格
- 弹窗和提示样式

### 3. 设计组件体系
优先沉淀以下组件：
- 资源卡片
- 项目卡片
- 员工卡片
- AI 员工队列/任务条
- 进度条
- 决策弹窗
- 结果反馈 toast / 面板

## 工作流

### 第一步：先做结构，再做装饰
先输出：
- 页面列表
- 页面层级
- 每页核心信息块
- 主路径点击顺序

### 第二步：把经营信息转成可视对象
对每类信息都明确：
- 用数字、图标、标签还是卡片表达
- 用持续展示还是事件弹出表达
- 哪些必须常驻，哪些可以收起

### 第三步：把 UI 结果写成可交付说明
默认采用以下模板：

```md
# UI 方案

## 页面目标
## 信息层级
## 组件清单
## 交互反馈
## 视觉关键词
## 实现优先级
```

## 视觉建议

### 风格关键词
- 科技创业感
- 轻量仪表盘感
- 决策面板感
- 低成本但干净统一

### 原型阶段优先级
1. 清晰
2. 一致
3. 可读
4. 可点击
5. 最后再考虑更强装饰性

## 约束

- 不要求首版高保真插画体系
- 不用复杂演出掩盖交互问题
- 不为了“科技感”牺牲阅读效率
- 不在原型阶段堆叠太多视觉状态

## 与其他角色的衔接

- 从 `ai-game-company-producer` 接收页面优先级与版本目标
- 从 `ai-game-company-systems-economy` 获取资源字段与反馈节点
- 与 `ai-game-company-web-tech-lead` 对齐组件实现边界
- 向 `ai-game-company-prototype-qa` 暴露关键观察点和用户操作路径
