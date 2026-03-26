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

## 约束
- 不引入正式后端，除非当前验证明确需要
- 不一开始就做复杂动画和高保真视觉
- 不为了“以后可能需要”提前堆技术复杂度
