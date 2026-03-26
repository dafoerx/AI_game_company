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

## 约束
- 不扩写与 48 小时内实现无关的长文档
- 不把有趣想法直接塞进当前版本
- 不输出无法被 `prototype-build` 直接执行的模糊结论
