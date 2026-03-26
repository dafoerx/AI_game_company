# 角色 Skills 索引

> 当前项目的角色 Skill 已从 5 角模型压缩为 3 角模型，目标是减少 handoff、优先做出最小可玩原型。

## 1. 当前技能清单

| 角色 | Skill 名称 | 路径 | 用途 |
|---|---|---|---|
| product-system | `restaurant-product-system` | `.workbuddy/skills/restaurant-product-system/SKILL.md` | 做方向判断、范围控制、系统定义、数值初版与设计冻结 |
| prototype-build | `restaurant-prototype-build` | `.workbuddy/skills/restaurant-prototype-build/SKILL.md` | 做 Web 原型架构、页面骨架、任务拆分与实现落地 |
| prototype-qa | `restaurant-prototype-qa` | `.workbuddy/skills/restaurant-prototype-qa/SKILL.md` | 做轻量验证点、P0/P1 风险拦截与原型试玩反馈 |

## 2. 推荐使用顺序

对于当前阶段，最推荐的顺序是：

1. **product-system Skill**：明确做什么、不做什么，并冻结范围
2. **prototype-build Skill**：拆前端切片与实现路径，直接启动工程骨架
3. **prototype-qa Skill**：只检查关键风险，不提前扩写过量资料

## 3. 每个 Skill 的定位原则

### product-system
- 解决“方向是否成立”
- 解决“本轮要做什么、不做什么”
- 输出可直接开工的设计与范围结论

### prototype-build
- 解决“怎么在 Web 上最快落地”
- 优先做餐饮经营原型的最短可玩路径
- 代码与结构以可演示、可迭代为核心

### prototype-qa
- 解决“首版原型哪里最容易失败”
- 只围绕理解成本、卡点、P0/P1 风险和继续游玩意愿建立验证标准
- 在没有代码落点时，不扩写长篇测试文档

## 4. 当前建议

- 如果角色职责变化，直接改对应 `SKILL.md`
- 如果后续恢复更细角色拆分，再从这 3 个 Skill 派生出去
- 如果主题或平台变化，优先同步更新所有 Skill 中的项目假设
