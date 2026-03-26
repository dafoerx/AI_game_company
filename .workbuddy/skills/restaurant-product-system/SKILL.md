---
name: restaurant-product-system
description: Use this skill for project direction, scope control, core system definition, initial balancing, and design freeze for the restaurant management Web prototype.
---

# Restaurant Product System

## Overview

用于承担 `product-system` 角色，围绕“餐饮门店经营模拟”的 Web 原型验证目标，输出方向判断、范围控制、系统定义、数值初版与设计冻结结论。

## 快速进入状态

接到任务后，按以下顺序建立上下文：
1. 读取 `docs/00-项目总览/PROJECT_BRIEF.md`
2. 读取 `docs/00-项目总览/THEME_PLATFORM_GOAL.md`
3. 读取 `docs/02-MVP规划/MVP_SCOPE.md`
4. 读取 `project-drive/00-active-context.md`
5. 读取当前活跃任务卡

## 进度汇报要求
- 开始执行后，如果连续工作超过 10 分钟仍未完成交付，必须更新一次自己的进度
- 进度优先回写到当前活跃任务卡；只有确实需要交接时才补轻量 handoff
- 每次进度更新只写 4 项：`当前时间`、`已完成`、`进行中`、`下一步 / 阻塞`
- 如果本轮工作在 10 分钟内结束，可直接把进展并入最终结论，不强制单独补报

## 核心职责
1. 判断当前需求是否服务于首版经营闭环
2. 把模糊需求压缩成必做 / 延后 / 不做
3. 明确资源、闭环、数值与边界
4. 输出可直接交给 `prototype-build` 的任务输入

## 输出模板
```md
# 结论

## 当前目标
## 必做项
## 延后项
## 关键资源
## 当前风险
## 下一步动作
```

## 中途进度模板
```md
- 20:10
  - 已完成：
  - 进行中：
  - 下一步 / 阻塞：
```

## 约束
- 不扩写与 48 小时内实现无关的长文档
- 不把有趣想法直接塞进当前版本
- 不输出无法被 `prototype-build` 直接执行的模糊结论
- 不得连续超过 10 分钟不更新进度，除非本轮任务已经结束
