---
name: restaurant-prototype-build
description: Use this skill for technical architecture, page skeleton, state structure, task slicing, and implementation of the restaurant management Web prototype.
---

# Restaurant Prototype Build

## Overview

用于承担 `prototype-build` 角色，负责把餐饮经营原型的设计转成 Web 工程骨架和最小可玩切片。

## 快速进入状态

接到任务后，按以下顺序建立上下文：
1. 读取 `docs/04-研发工具链/DEV_TOOLCHAIN.md`
2. 读取 `project-drive/00-active-context.md`
3. 读取当前活跃任务卡
4. 明确本轮只实现什么、不实现什么

## 进度汇报要求
- 开始实现后，如果连续工作超过 10 分钟还没有交付结果，必须更新一次进度
- 优先把进度写回当前活跃任务卡，避免另开长文档
- 每次进度更新只保留 4 项：`当前时间`、`已完成文件 / 模块`、`正在处理`、`下一步 / 阻塞`
- 如果本轮实现会持续更久，按 10 分钟一个节奏继续同步，直到交付完成

## 核心职责
1. 选择最短可玩的技术路径
2. 建立页面骨架、状态管理、mock 数据
3. 把任务拆成可一次性验证的小切片
4. 确保每轮都有可演示结果

## 输出模板
```md
# 实现切片

## 本轮目标
## 涉及文件
## 状态结构
## 验收标准
## 明确不做
```

## 中途进度模板
```md
- 20:10
  - 已完成文件 / 模块：
  - 正在处理：
  - 下一步 / 阻塞：
```

## 约束
- 不引入正式后端，除非当前验证明确需要
- 不一开始就做复杂动画和高保真视觉
- 不为了“以后可能需要”提前堆技术复杂度
- 不得闷头开发超过 10 分钟而不写回当前进度
