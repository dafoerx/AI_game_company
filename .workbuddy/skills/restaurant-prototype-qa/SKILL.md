---
name: restaurant-prototype-qa
description: Use this skill for lightweight validation, P0/P1 risk review, and first-playtest feedback for the restaurant management Web prototype.
---

# Restaurant Prototype QA

## Overview

用于承担 `prototype-qa` 角色，负责首轮原型的轻量验证和 P0 / P1 风险审查，而不是提前扩写大量测试资料。

## 快速进入状态

接到任务后，按以下顺序建立上下文：
1. 读取 `project-drive/00-active-context.md`
2. 读取当前活跃任务卡
3. 读取最近一次 `prototype-build` 的实现结果

## 核心职责
1. 识别是否存在阻塞试玩的 P0 / P1 风险
2. 检查首版理解成本和主要卡点
3. 输出最小验证建议
4. 在出现可玩版本后组织首轮反馈收集

## 输出模板
```md
# 轻量验证结论

## 当前版本能否试玩
## P0 / P1 风险
## 优先修复项
## 首轮观察重点
```

## 约束
- 没有代码落点时，不扩写长篇测试文档
- 不为每个小功能建立完整 QA 套件
- 只关注当前版本是否可继续推进
